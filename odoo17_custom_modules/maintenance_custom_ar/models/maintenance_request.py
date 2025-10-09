# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request.custom'
    _description = 'طلب صيانة'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='الرقم',
        default=lambda self: self.env['ir.sequence'].next_by_code('maintenance.request.custom'),
        readonly=True
    )
    user_id = fields.Many2one(
        'res.users',
        string='المسؤول',
        default=lambda self: self.env.user,
        required=True
    )
    date = fields.Date(
        string='تاريخ الطلب',
        default=fields.Date.context_today,
        required=True
    )
    execution_duration = fields.Integer(string='مدة التنفيذ (بالأيام)', default=1)
    vehicle_id = fields.Many2one('maintenance.vehicle', string='المركبة')
    vehicle_type = fields.Char(string='نوع السيارة', related='vehicle_id.vehicle_type', store=True, readonly=True)
    driver_id = fields.Many2one('maintenance.driver', string='السائق')

    part_line_ids = fields.One2many(
        'maintenance.request.line', 'request_id',
        string='قطع الغيار المطلوبة'
    )

    state = fields.Selection(
        [('draft', 'مسودة'), ('confirmed', 'مؤكد'), ('done', 'منفذ')],
        default='draft',
        string='الحالة'
    )

    picking_id = fields.Many2one('stock.picking', string='حركة المخزون', readonly=True, copy=False)
    bill_id = fields.Many2one('account.move', string='فاتورة مشتريات', readonly=True, copy=False)

    # =========================
    # أزرار الحالة/الإجراءات
    # =========================
    def action_confirm(self):
        for rec in self:
            if not rec.part_line_ids:
                raise UserError('لا توجد قطع غيار.')
            rec.state = 'confirmed'

    def action_done(self):
        """تنفيذ بسيط - خصم مباشر من المخزون مع جمع الكميات"""
        for rec in self:
            if not rec.part_line_ids:
                raise UserError('لا توجد قطع غيار.')

            # البحث عن warehouse
            warehouse = self.env['stock.warehouse'].search([], limit=1)
            if not warehouse:
                raise UserError('يرجى إنشاء Warehouse.')

            location = warehouse.lot_stock_id

            # جمع الكميات المطلوبة لكل منتج
            product_quantities = {}
            for line in rec.part_line_ids:
                if not line.product_id:
                    continue

                product_id = line.product_id.id
                if product_id not in product_quantities:
                    product_quantities[product_id] = {
                        'product': line.product_id,
                        'total_qty': 0.0
                    }
                product_quantities[product_id]['total_qty'] += line.quantity

            # التحقق من الكميات المتاحة لكل منتج
            for product_id, data in product_quantities.items():
                product = data['product']
                required_qty = data['total_qty']

                # البحث عن الكمية الموجودة
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', product_id),
                    ('location_id', '=', location.id)
                ])

                available_qty = sum(quants.mapped('quantity'))

                if available_qty < required_qty:
                    raise UserError(
                        f'الكمية المتاحة غير كافية!\n\n'
                        f'المنتج: {product.display_name}\n'
                        f'المطلوب: {required_qty}\n'
                        f'المتاح: {available_qty}'
                    )

                # تحديث الكمية (خصم)
                remaining = required_qty
                for quant in quants:
                    if remaining <= 0:
                        break

                    if quant.quantity >= remaining:
                        quant.quantity -= remaining
                        remaining = 0
                    else:
                        remaining -= quant.quantity
                        quant.quantity = 0

            rec.state = 'done'

    def action_create_bill(self):
        """إنشاء فاتورة مشتريات من طلب الصيانة"""
        for rec in self:
            if not rec.part_line_ids:
                raise UserError('لا توجد قطع غيار.')

            partner = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
            if not partner:
                raise UserError('يرجى إنشاء مورد أولاً.')

            lines = []
            for l in rec.part_line_ids:
                expense_account = (l.product_id.property_account_expense_id
                                   or l.product_id.categ_id.property_account_expense_categ_id)
                if not expense_account:
                    raise UserError('يرجى ضبط حساب المصروف للمنتج أو لفئة المنتج.')

                # جلب السعر من المنتج إذا كان فارغاً أو صفر
                price = l.price_unit
                if not price or price == 0:
                    # استخدام سعر البيع من المنتج
                    price = l.product_id.list_price
                    # أو استخدام التكلفة: price = l.product_id.standard_price

                lines.append((0, 0, {
                    'product_id': l.product_id.id,
                    'name': l.product_id.display_name,
                    'quantity': l.quantity or 0.0,
                    'price_unit': price,
                    'account_id': expense_account.id,
                }))

            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': partner.id,
                'invoice_origin': rec.name,
                'invoice_date': rec.date,
                'date': rec.date,
                'invoice_line_ids': lines,
            })

            rec.bill_id = bill.id
            return {
                'name': 'فاتورة مشتريات',
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': bill.id,
                'target': 'current',
            }

    # =========================
    # مخرجات PDF / Excel
    # =========================
    def action_print_pdf(self):
        """يطبع تقرير PDF"""
        self.ensure_one()
        # البحث عن التقرير بالاسم بدلاً من XML ID
        report = self.env['ir.actions.report'].search([
            ('report_name', '=', 'maintenance_custom_ar.report_maintenance_req'),
            ('model', '=', 'maintenance.request.custom')
        ], limit=1)

        if not report:
            # إذا لم يوجد، أنشئه ديناميكياً
            report = self.env['ir.actions.report'].create({
                'name': 'بيان طلب الصيانة (PDF)',
                'model': 'maintenance.request.custom',
                'report_type': 'qweb-pdf',
                'report_name': 'maintenance_custom_ar.report_maintenance_req',
                'print_report_name': "'بيان_طلب_صيانة_' + (object.name or '')",
            })

        return report.report_action(self)

    def action_export_xlsx(self):
        """يفتح رابط الكونترولر لتصدير Excel للطلب الحالي"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/maintenance_custom_ar/request/xlsx/{self.id}',
            'target': 'self',
        }


class MaintenanceRequestLine(models.Model):
    _name = 'maintenance.request.line'
    _description = 'سطر قطع غيار'

    request_id = fields.Many2one(
        'maintenance.request.custom',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='اسم القطعة',
        required=True,
        domain=[('detailed_type', 'in', ['product', 'consu'])]
    )
    quantity = fields.Float(string='الكمية', default=1.0)
    price_unit = fields.Float(string='السعر')
    price_subtotal = fields.Float(string='الإجمالي', compute='_compute_subtotal', store=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ملء السعر تلقائياً عند اختيار المنتج"""
        if self.product_id:
            # استخدام سعر البيع (Sales Price)
            self.price_unit = self.product_id.list_price

    @api.model_create_multi
    def create(self, vals_list):
        """ملء السعر تلقائياً عند الإنشاء إذا كان فارغاً"""
        for vals in vals_list:
            if 'product_id' in vals and (not vals.get('price_unit') or vals.get('price_unit') == 0):
                product = self.env['product.product'].browse(vals['product_id'])
                if product:
                    vals['price_unit'] = product.list_price
        return super().create(vals_list)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for rec in self:
            rec.price_subtotal = (rec.quantity or 0.0) * (rec.price_unit or 0.0)

