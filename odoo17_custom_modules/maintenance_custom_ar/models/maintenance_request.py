# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class MaintenanceRequest(models.Model):
    _name = 'maintenance.request.custom'
    _description = 'طلب صيانة (مخصص)'
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
    vehicle_name = fields.Char(string='اسم المركبة')
    vehicle_type = fields.Char(string='نوع السيارة')
    driver_name = fields.Char(string='اسم السائق')

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

    def _get_internal_picking_type(self):
        """يحاول إيجاد نوع عملية داخلية (internal). لو مش موجود، يجرّب outgoing."""
        PickingType = self.env['stock.picking.type']
        picking_type = PickingType.search([('code', '=', 'internal')], limit=1)
        if not picking_type:
            picking_type = PickingType.search([('code', '=', 'outgoing')], limit=1)
        return picking_type

    def action_done(self):
        for rec in self:
            if not rec.part_line_ids:
                raise UserError('لا توجد قطع غيار.')

            picking_type = rec._get_internal_picking_type()
            if not picking_type:
                raise UserError('لم يتم العثور على نوع عملية مخزنية (internal/outgoing).')

            if not picking_type.default_location_src_id or not picking_type.default_location_dest_id:
                raise UserError('يرجى ضبط المواقع الافتراضية لنوع العملية المختار.')

            # إنشاء تحريك مخزني واستهلاك الكميات
            moves = []
            for l in rec.part_line_ids:
                if not l.product_id:
                    raise ValidationError('يرجى اختيار المنتج لكل سطر.')
                moves.append((0, 0, {
                    'name': l.product_id.display_name,
                    'product_id': l.product_id.id,
                    'product_uom_qty': l.quantity or 0.0,
                    'product_uom': l.product_id.uom_id.id,
                    'location_id': picking_type.default_location_src_id.id,
                    'location_dest_id': picking_type.default_location_dest_id.id,
                }))

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'origin': rec.name,
                'move_ids_without_package': moves,
            })

            # تأكيد وتعيين ثم تسجيل الكميات المُنفذة
            picking.action_confirm()
            picking.action_assign()

            # أسهل وأضمن: أنجز التحريك مباشرة بدون نوافذ (Backorder Wizard)
            # لو محتاجين تحديد كميات من خطوط التحريك:
            for mv in picking.move_ids_without_package:
                mv.quantity_done = mv.product_uom_qty

            # إنهاء العملية
            picking.button_validate()

            rec.picking_id = picking.id
            rec.state = 'done'

    def action_create_bill(self):
        for rec in self:
            if not rec.part_line_ids:
                raise UserError('لا توجد قطع غيار.')

            partner = self.env['res.partner'].search([('supplier_rank', '>', 0)], limit=1)
            if not partner:
                raise UserError('يرجى إنشاء مورد أولاً.')

            lines = []
            for l in rec.part_line_ids:
                # تحديد حساب المصروف المناسب (من المنتج وإلا من فئة المنتج)
                expense_account = (l.product_id.property_account_expense_id
                                   or l.product_id.categ_id.property_account_expense_categ_id)
                if not expense_account:
                    raise UserError('يرجى ضبط حساب المصروف للمنتج أو لفئة المنتج.')

                lines.append((0, 0, {
                    'product_id': l.product_id.id,
                    'name': l.product_id.display_name,
                    'quantity': l.quantity or 0.0,
                    'price_unit': l.price_unit or 0.0,
                    'account_id': expense_account.id,
                }))

            bill = self.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id': partner.id,
                'invoice_origin': rec.name,
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
        """يطبع تقرير PDF المعرّف بـ XML-ID: maintenance_custom_ar.action_maintenance_req_pdf"""
        self.ensure_one()
        return self.env.ref('maintenance_custom_ar.action_maintenance_req_pdf').report_action(self)

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

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for rec in self:
            rec.price_subtotal = (rec.quantity or 0.0) * (rec.price_unit or 0.0)
