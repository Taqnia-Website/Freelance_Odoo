# -*- coding: utf-8 -*-
# from odoo import http


# class AbHotelDashboard(http.Controller):
#     @http.route('/ab_hotel_dashboard/ab_hotel_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ab_hotel_dashboard/ab_hotel_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ab_hotel_dashboard.listing', {
#             'root': '/ab_hotel_dashboard/ab_hotel_dashboard',
#             'objects': http.request.env['ab_hotel_dashboard.ab_hotel_dashboard'].search([]),
#         })

#     @http.route('/ab_hotel_dashboard/ab_hotel_dashboard/objects/<model("ab_hotel_dashboard.ab_hotel_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ab_hotel_dashboard.object', {
#             'object': obj
#         })

