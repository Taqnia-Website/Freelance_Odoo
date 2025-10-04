import re

import unicodedata

from odoo import models, fields, api


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    hotel_url_path = fields.Char("Url Path Hotel", required=False)

    _sql_constraints = [
        ('hotel_url_path_uniq', 'unique (hotel_url_path)', "hotel_url_path SHOULD BE UNIQUE!"),
    ]
    @api.onchange('name')
    def _onchange_name(self):
        """
        Convert a string to a valid URL path.
        """
        text = self.name
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Normalize unicode characters (convert accented chars to ASCII equivalents)
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ascii', 'ignore').decode('ascii')

        # Replace spaces and other separators with hyphens
        text = re.sub(r'[\s_]+', '-', text)

        # Remove all characters that aren't alphanumeric or hyphens
        text = re.sub(r'[^a-z0-9\-]', '', text)

        # Remove multiple consecutive hyphens
        text = re.sub(r'-+', '-', text)

        # Remove leading and trailing hyphens
        text = text.strip('-')


        self.hotel_url_path = text