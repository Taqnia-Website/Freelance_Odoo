# -*- coding: utf-8 -*-
from attr.validators import instance_of

from odoo import models, fields, api
import logging

class RoomType(models.Model):
    _inherit = 'hotel.room_type'

    def list_room_type(self):
        # Show only room categories that have at least one room assigned to the current agent.
        if self.env.user.partner_id.agent:
            records = self.env['hotel.reservation.line'].sudo().search([('line_id.partner_id', '=', self.env.user.partner_id.id),
                                                                       ('line_id.state', '=', 'confirm'),
                                                                       ('company_id', 'in', self.env.companies.ids)
                                                                      ])

            room_type_ids = self.env['hotel.room_type'].sudo().search_read([
                ('cat_id', 'in', records.mapped('categ_id.id'))
            ], ['name'])

            return room_type_ids
        res = super().list_room_type()
        return res

        # return self.sudo().search_read([("isroomtype", "=", True), ('company_id', '=', self.env.company.id)],
        #                                fields=['name'])

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

    def search_reserve_room(self, room_id):
        if self.env.user.partner_id.agent:
            domain = [('room_number', '=', room_id.product_id.id)]

            res = self.env['hotel.reservation.line'].search(domain)
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
        return super().search_reserve_room(room_id)
