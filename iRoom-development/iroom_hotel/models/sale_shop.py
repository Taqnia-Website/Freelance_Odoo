from odoo import models, fields


class SaleShop(models.Model):
    _inherit = 'sale.shop'

    name = fields.Char(translate=True)

    address = fields.Char(translate=True)
    email = fields.Char()
    mobile = fields.Char()
    website = fields.Char()
    location = fields.Char()
    location_iframe = fields.Char('Location IFrame')
    x_coordinate = fields.Char('X-Coordinate')
    y_coordinate = fields.Char('Y-Coordinate')
    distance_from_center = fields.Integer()
    facebook = fields.Char()
    twitter = fields.Char()
    vk = fields.Char()
    instagram = fields.Char()

    image_ids = fields.One2many('sale.shop.image', 'sale_shop_id')

    activity_ids = fields.One2many('sale.shop.activity.line', 'shop_id')

    breakfast = fields.Text(translate=True)
    lunch = fields.Text(translate=True)
    dinner = fields.Text(translate=True)

    option_ids = fields.One2many('sale.shop.option', 'sale_shop_id')

    amenity_ids = fields.Many2many('hotel.room_amenities')
    tag_ids = fields.Many2many('sale.shop.tag')
    similar_hotels_ids = fields.Many2many(
        'sale.shop',
        'sale_shop_similar_rel',  # Relation table name
        'shop_id',  # Column for the current shop
        'similar_shop_id',  # Column for the related shop
        domain="[('id', '!=', id)]"
    )
    close_to = fields.Char()
    number_of_restaurants = fields.Integer()
    check_in_out_times = fields.Text('Check-in and check-out times', translate=True)

    youtube_link = fields.Char()
    description = fields.Text(translate=True)

    rating_average = fields.Float(compute='_compute_rating_average')
    rating_count = fields.Integer(compute='_compute_rating_count')
    reservation_count = fields.Integer(compute='_compute_reservation_count')

    def _compute_rating_average(self):
        for shop in self:
            ratings = self.env['hotel.reservation.rating'].search([('shop_id', '=', shop.id)])
            rating_average = sum(ratings.mapped('total_rate')) / len(ratings) if ratings else 0
            shop.rating_average = rating_average

    def _compute_rating_count(self):
        for shop in self:
            rating_count = self.env['hotel.reservation.rating'].search_count([('shop_id', '=', shop.id)])
            shop.rating_count = rating_count

    def _compute_reservation_count(self):
        for shop in self:
            reservation_count = self.env['hotel.reservation'].search_count([('shop_id', '=', shop.id)])
            shop.reservation_count = reservation_count
