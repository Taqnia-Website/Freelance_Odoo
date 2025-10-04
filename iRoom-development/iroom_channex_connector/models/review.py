from odoo import fields, models, api
import requests
import json


class ChannexReviewCategory(models.Model):
    _name = 'channex.review.category'
    _description = 'Channex Review Category'

    name = fields.Char(required=True)



class ChannexReviewTag(models.Model):
    _name = 'channex.review.tag'
    _description = 'Channex Review Tag'

    name = fields.Char(required=True)


class ChannexReview(models.Model):
    _name = 'channex.review'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Channex Review'

    name = fields.Char(required=True)
    channex_id = fields.Char(string='Channex ID')
    guest_name = fields.Char()
    is_hidden = fields.Boolean()
    is_replied = fields.Boolean()
    ota = fields.Char()
    ota_reservation_id = fields.Char()
    overall_score = fields.Float()
    score_ids = fields.One2many('channex.score', 'review_id')


    def get_channex_reviews(self):
        shops = self.env['sale.shop'].search([('channex_id', '!=', False)])
        if shops:
            company = shops[0].company_id
            url = f"{company.channex_url}/reviews"
            headers = {
                "Content-Type": "application/json",
                "user-api-key": company.channex_key
            }
            response = requests.request("GET", url, headers=headers)
            reviews = json.loads(response.text).get('data', False)
            for review in reviews:
                data = review['attributes']
                reservation_vals = {
                    'name': data.get('content', False),
                    'guest_name': data.get('guest_name', False),
                    'channex_id': data.get('id', False),
                    'is_hidden': data.get('is_hidden', False),
                    'is_replied': data.get('is_replied', False),
                    'ota': data.get('ota', False),
                    'ota_reservation_id': data.get('ota_reservation_id', False),
                    'overall_score': data.get('overall_score', False),
                }
                line_vals = []
                lines = data['scores']
                for line in lines:
                    line_vals.append([0, 0, {
                        'category': line['category'],
                        'score': line['score'],
                    }])
                if line_vals:
                    review_id = self.env['channex.review'].create(reservation_vals)
                    review_id.write({
                        'score_ids': line_vals
                    })


class ChannexScore(models.Model):
    _name = 'channex.score'
    _description = 'Channex Score'

    review_id = fields.Many2one('channex.review')
    category_id = fields.Many2one('channex.review.category')
    category = fields.Char()
    score = fields.Float()
