from odoo import fields, models, api
from odoo.osv import expression


class Nationality(models.Model):
    _name = 'ntmp.nationality'
    _description = 'NTMP Nationality'
    _rec_name = 'arabic_title'
    _order = 'code'

    arabic_title = fields.Char(required=True)
    english_title = fields.Char(required=True)
    code = fields.Char(required=True)

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', '|', ('arabic_title', operator, name), ('english_title', operator, name), ('code', operator, name)]
        return self._search(domain, limit=limit, order=order)
