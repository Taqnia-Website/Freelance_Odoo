# -*- coding: utf-8 -*-
from collections import defaultdict

import odoo.tools
from odoo import models, fields, api, _, exceptions
from datetime import datetime, date, timedelta
import re
import logging

_logger = logging.getLogger(__name__)


def _get_number(chr):
    numbers = re.findall(r'\d+', chr)

    # Convert the extracted numbers into integers
    numbers = [int(number) for number in numbers]
    return numbers


class HotelDashboard(models.Model):
    _inherit = 'hotel.reservation'

    # @api.model
    def get_all_reservation_details(self, shop_id):
        shop_id = int(shop_id)

        # Call each method and store the results in a dictionary
        reservation_details = {
            'folio': self.search_folio(shop_id),
            'cleaning': self.search_cleaning(shop_id),
            'repair': self.search_repair(shop_id),
        }

        reservation_details.update(self.env['hotel.room_type'].get_room_and_type_data(shop_id))

        return reservation_details

    def search_folio(self, shop_id):
        shop_id = int(shop_id)
        if self.env.user.partner_id.agent:
            fo = self.env['hotel_folio.line'].search([('folio_id.shop_id.id', '=', shop_id)])
        else:
            fo = self.env['hotel_folio.line'].sudo().search([('folio_id.shop_id.id', '=', shop_id)])
        folio = []
        for i in fo:
            if i.folio_id.reservation_id.state != 'cancel' and i.folio_id.reservation_id:
                folio.append({
                    'checkin': i.checkin_date,
                    'checkout': i.checkout_date,
                    'status': i.folio_id.state,
                    'id': i.folio_id.id,
                    'room_name': i.product_id.name,
                    'fol_no': i.folio_id.reservation_id.reservation_no,
                })
        return folio

    def folio_detail(self, id):
        id = int(id)
        res = []
        user = self.env.user
        if not user.partner_id.agent:
            folios = self.env['hotel_folio.line'].sudo().search([('folio_id', '=', id)])
            for folio in folios:
                res.append(
                    {
                        'res_no': folio.folio_id.reservation_id.reservation_no,
                        'checkin': folio.checkin_date,
                        'checkout': folio.checkout_date,
                        'state': folio.folio_id.state,
                        'partner': folio.folio_id.partner_id.name,
                    }
                )
            return res
        else:
            return res

    def search_cleaning(self, shop_id):
        shop_id = int(shop_id)
        clean = self.env['hotel.housekeeping'].sudo().search([('room_no.shop_id.id', '=', shop_id)])
        cleans = []
        for i in clean:
            cleans.append({
                'room_no': i.room_no.name,
                'checkin': i.current_date,
                'checkout': i.end_date,
                'id': i.id,
                'status': i.state,
            })
        return cleans

    def search_repair(self, shop_id):
        shop_id = int(shop_id)
        repair = self.env['rr.housekeeping'].sudo().search([('shop_id', '=', shop_id)])
        repairs = []
        for i in repair:
            repairs.append({
                'room_no': i.room_no.name,
                'date': i.date,
                'id': i.id,
                'type': i.activity,
                'status': i.state,
            })
        return repairs

    def create_detail(self, room_type, room, checkin, checkout):
        print("*****************ff**********************")
        if not self.env.user.has_group('hotel_management.group_hotel_reservation_manager') or not self.env.user.has_group('hotel_management.group_hotel_reservation_user'):
            raise exceptions.AccessError(_('You do not have permission to make reservations. Please contact your system administrator for assistance'))

        date_obj = datetime.strptime(checkin, "%Y-%m-%d")
        check_in = date_obj.date()
        date2_date = datetime.strptime(checkout, "%Y-%m-%d")
        check_out = date2_date.date()
        if check_in == check_out:
            check_out = check_out + timedelta(days=1)
        room_types = int(room_type)
        room = int(room)
        categ_id = self.env['hotel.room_type'].sudo().search([('id', '=', room_types)])
        cat_id = categ_id.cat_id.id
        rooms = self.env['hotel.room'].sudo().search([('id', '=', room)])
        price = rooms.list_price
        room_id = rooms.product_id.id
        detail = [{
            'room': room_id,
            'cat_id': cat_id,
            'price': price,
            'checkout': check_out,

        }]
        return detail

    def cleaning_detail(self, id):
        id = int(id)
        res = []
        user = self.env.user
        if not user.partner_id.agent:
            clean = self.env['hotel.housekeeping'].sudo().browse(id)
            res.append(
                {
                    'name': 'Unavilable/Under Cleaning',
                    'start': clean.current_date,
                    'end': clean.end_date,
                    'inspector': clean.inspector.name,
                    'state': clean.state,
                }
            )
            return res
        else:
            return res

    def repair_repace_detail(self, id):
        id = int(id)
        res = []
        user = self.env.user
        if not user.partner_id.agent:
            repair = self.env['rr.housekeeping'].sudo().browse(id)
            res.append(
                {
                    'name': 'Repair/Repacement',
                    'date': repair.date,
                    'activity': repair.activity,
                    'request': repair.requested_by.name,
                    'approved': repair.approved_by,
                    'state': repair.state,
                }
            )
            return res
        else:
            return res

    def check_user(self):
        user = self.env.user
        if user.partner_id.agent:
            return False
        else:
            return True

    def get_datas(self, shop):
        shop_ids = int(shop)
        if shop_ids:
            check_in = self.env['hotel.reservation'].search([('state', '=', 'confirm'), ('shop_id', '=', shop_ids)])
            check_out = self.env['hotel.folio'].search([('state', '=', 'check_out'), ('shop_id', '=', shop_ids)])
            roomid = []
            room_id = self.env['hotel.room'].search([('shop_id', '=', shop_ids)])
            for i in room_id:
                roomid.append(i)
            for i in room_id:
                book_his = self.env['hotel.room.booking.history'].search(
                    [('history_id', '=', i.id), ('state', '!=', 'done'), ('history_id.shop_id', '=', shop_ids)])
                if book_his and i in roomid:
                    roomid.remove(i)
            for i in room_id:
                prod = i.product_id.id
                housekeep = self.env['hotel.housekeeping'].search(
                    [('room_no', '=', prod), ('state', '!=', 'done'), ('room_no.shop_id', '=', shop_ids)])
                if housekeep and i in roomid:
                    roomid.remove(i)
            for i in room_id:
                repair = self.env['rr.housekeeping'].search(
                    [('room_no', '=', i.id), ('state', '!=', 'done'), ('shop_id', '=', shop_ids)])
                if repair and i in roomid:
                    roomid.remove(i)
            booked = self.env['hotel.reservation'].search([('state', '!=', 'cancel'), ('shop_id', '=', shop_ids)])

            return {
                'check_in': len(check_in),
                'check_out': len(check_out),
                'total': len(roomid),
                'booked': len(booked),
            }
        else:
            return {
                'check_in': '',
                'check_out': '',
                'total': '',
                'booked': '',
            }

    def get_view_reserve(self):
        view_id = self.env.ref('hotel_management.view_hotel_reservation_form1').id
        return view_id


from collections import defaultdict


class RoomType(models.Model):
    _inherit = 'hotel.room_type'

    def list_room_type(self):
        if self.env.user.partner_id.agent:
            records = self.env['hotel.reservation.line'].search([('line_id.partner_id', '=', self.env.user.partner_id.id),
                                                                       ('line_id.state', '=', 'confirm'),
                                                                       ('company_id', 'in', self.env.companies.ids)
                                                                      ])

            room_type_ids = self.env['hotel.room_type'].sudo().search_read([
                ('cat_id', 'in', records.mapped('categ_id.id'))
            ], ['name'])

            return room_type_ids
        return self.sudo().search_read([("isroomtype", "=", True), ('company_id', '=', self.env.company.id)],
                                       fields=['name'])

    def _get_own_agent_rooms(self, shop_id, cat_id):
        """
        Retrieve rooms for the specified hotel and category that are assigned to current agent.
        :param shop_id: Hotel
        :param cat_id: Room Category
        :return:
        """
        res = self.env['hotel.reservation.line'].sudo().search(
            [('line_id.partner_id', '=', self.env.user.partner_id.id),
             ('line_id.state', '=', 'confirm'),
             ('categ_id', '=', cat_id),
             ('line_id.shop_id', '=', shop_id)
             ])
        return  self.env['hotel.room'].search([('product_id', 'in', res.mapped('room_number.id'))])

    def list_room(self, room_type_id, shop_id):
        shop_id = int(shop_id)
        room_type_id = int(room_type_id)
        if room_type_id and shop_id:
            # Fetch the room category in a single query
            room_type = self.env['hotel.room_type'].browse(room_type_id)
            cat_id = room_type.cat_id.id

            if self.env.user.partner_id.agent:
                rooms = self._get_own_agent_rooms(shop_id, cat_id)
            else:
                rooms = self.env['hotel.room'].search([
                    ('categ_id', 'child_of', cat_id),
                    ('shop_id', '=', shop_id),
                    ('isroom', '=', True),
                    ('company_id', '=', self.env.company.id),
                ])

            # Prepare room data
            if rooms:
                datas = [{'name': room.name, 'id': room.id, 'categ_id': room.categ_id.id,
                          'reserve_room': self.search_reserve_room(room)} for room in rooms]
                return datas
        return []

    def list_shop(self):
        # ! We have disabled this code because, we will make filter via 'ir.rule'

        # current_user = self.env.user
        #
        # if current_user.partner_id.agent:
        #     # Fetch shops related to the agent in a single query
        #     shops = self.env['agent.relation'].search([('agent_id', '=', current_user.partner_id.id)])
        #     res = [{'name': s.name, 'id': s.id} for rel in shops for s in rel.shop_ids]
        # else:
        #     # Fetch all shops
        #     shops = self.env['sale.shop'].search([])
        #     res = [{'name': shop.name, 'id': shop.id} for shop in shops]

        shops = self.env['sale.shop'].search([])
        res = [{'name': shop.name, 'id': shop.id} for shop in shops]
        return res

    @api.model
    def get_room_and_type_data(self, shop_id):
        room_type_data = self.list_room_type()
        rooms_types = []
        for room_type in room_type_data:
            # Use list_room once per room type
            list_room = self.list_room(room_type['id'], shop_id)
            if list_room:
                room_type.update({'rooms': list_room})
                rooms_types.append(room_type)

        return {
            'room_types': rooms_types,
        }

    def search_reserve_room(self, room_id):
        if self.env.user.partner_id.agent:
            res = self.env['hotel.reservation.line'].search([
                ('room_number', '=', room_id.product_id.id)
            ])
        else:
            res = self.env['hotel.reservation.line'].sudo().search(
                [('line_id.state', 'in', ['draft', 'confirm', 'done']), ('room_number', '=', room_id.product_id.id)])

        reservation = []
        for i in res:
            if i.line_id:
                reservation.append({
                    'checkin': i.checkin,
                    'checkout': i.checkout,
                    'status': i.line_id.state,
                    'id': i.line_id.id,
                    'ref_no': i.line_id.reservation_no,
                    'boolean': i.line_id.agent_id_boolean,
                })
        return reservation




class ReservationLine(models.Model):
    _inherit = 'hotel.reservation.line'

    def reserve_room(self, id):
        reservation = []
        try:
            line_id = int(id)
            res = self.browse(line_id)
            for i in res:
                reservation.append({
                    'checkin': i.checkin,
                    'checkout': i.checkout,
                    'status': i.line_id.state,
                    'id': i.line_id.id,
                    'partner': i.line_id.partner_id.name,
                    'ref_no': i.line_id.reservation_no,
                    'boolean': i.line_id.agent_id_boolean,
                })
        except Exception as e:
            _logger.info(f"*************************************************{e}")
        return reservation
