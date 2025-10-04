from odoo.http import request, Controller, route


class HomeController(Controller):
    @route('/similar_hotels/<string:name>/<int:id>', website=True, type='http', auth='public')
    def similar_hotels(self, **kwargs):

        return request.render('iroom_website.similar_hotels')