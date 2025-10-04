# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo import http
from odoo.http import request
from odoo.addons.point_of_sale.controllers.main import PosController as PosInheritController

class BackendConfigration(http.Controller):

	@http.route(['/get/tab/title/'], type='json', auth='public')
	def get_tab_title(self, **kw):
		company_id = request.env.company
		new_name = company_id.sys_tab_name
		return new_name

class PosController(PosInheritController):
	@http.route(['/pos/web', '/pos/ui'], type='http', auth='user')
	def pos_web(self, config_id=False, **k):
		# inherit function for pass company id in order receipt
		res = super(PosController, self).pos_web(config_id)
		pos_session_id = res.qcontext.get('pos_session_id',False)
		pos_session = request.env['pos.session'].sudo().browse(pos_session_id)
		res.qcontext.update({'company_id':pos_session.company_id})
		return res