from odoo.http import Controller, route, request


class Room(Controller):
    @route('/api/get_room_by_id', methods=['GET', 'POST'], type='json', auth='none', csrf=False)
    def get_room_by_id(self, room_id):
        room = request.env['hotel.room'].browse(room_id)
        data = {
            'name': room.name,
            'persons_number': room.max_adult + room.max_child,
            'area': room.area,
            'number_of_bathrooms': room.number_of_bathrooms,
            'unit_price': room.list_price,
            'description': room.description,
            'amenities': [{'name': amenity.name, 'icon': amenity.icon_code} for amenity in room.room_amenities]
        }
        return data
