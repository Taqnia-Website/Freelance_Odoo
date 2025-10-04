from odoo.http import Controller, route, request

import re


class OnlineReservation(Controller):
    @route('/api/get_states', methods=['GET', 'POST'], type='json', auth='none', csrf=False)
    def get_states(self, **kwargs):
        states = request.env['res.country.state'].sudo().with_context(lang=request.context['lang']).search([])
        return [{'id': state.id, 'country_id': state.country_id.id, 'name': state.name} for state in states]

    def validate_data(self, **data):
        errors = []

        if not data.get('user_id') and not data.get('email'):
            errors.append('You have to set email.')
        elif re.match(r'^[a-zA-Z0-9_.+-]@[a-zA-Z0-9-]\.[a-zA-Z0-9-.]$', data['email']):
            errors.append('Inserted email is not valid. ')
        elif data.get('email'):
            user = request.env['res.users'].sudo().search([('login', '=', data['email'])])
            if user:
                errors.append('Email is already signed up before!')
                return {'valid': False, 'message': errors}

        if not data.get('first_name'):
            errors.append('You have to set first name.')
        if not data.get('last_name'):
            errors.append('You have to set last name.')
        if not data.get('user_id') and not data.get('password'):
            errors.append('You have to set password.')
        # if not data.get('mobile'):
        #     errors.append('You have to set mobile.')
        # if not data.get('terms_and_conditions') or data['terms_and_conditions'] != 'on':
        #     errors.append('You have to to approve terms and conditions.')
        # if not data.get('country_id'):
        #     errors.append('You have to set country.')
        # if not data.get('country_id'):
        #     errors.append('You have to set country.')
        # if not data.get('card_owner'):
        #     errors.append('You have to set name of card owner.')
        # if not data.get('card_number'):
        #     errors.append('You have to set card number.')
        # if not data.get('card_month'):
        #     errors.append('You have to set expiration month.')
        # if not data.get('card_year'):
        #     errors.append('You have to set expiration year.')
        # if not data.get('card_cvv_cvc'):
        #     errors.append('You have to set CVV/CVC.')

        return {'valid': False if errors else True, 'message': errors}

    def get_user(self, **data):
        if not data.get('user_id'):
            name = data['first_name'] + ' ' + data['last_name']
            login, password = request.env['res.users'].sudo().signup({
                'login': data['email'],
                'name': name,
                'password': data['password'],
                'lang': 'en_GB'
            }, '')
            request.env.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
            user = request.env['res.users'].sudo().search([('login', '=', data['email'])])
            return user
        else:
            user = request.env['res.users'].sudo().browse(data['user_id'])
            return user

    @route('/api/create_reservation', methods=['GET', 'POST'], type='json', auth='none', csrf=False)
    def create_reservation(self, **kwargs):
        validation = self.validate_data(**kwargs)
        if not validation['valid']:
            return {'error': True, 'message': validation['message']}

        if not kwargs.get('user_id'):
            user = self.get_user(**kwargs)
            x = user

    @route('/api/create_user', methods=['GET', 'POST'], type='json', auth='none', csrf=False)
    def create_user(self, **kwargs):
        errors = []
        if not kwargs['name']:
            errors.append('You have to set name')
        if not kwargs['email']:
            errors.append('You have to set email')
        if not kwargs['password']:
            errors.append('You have to set password')
        if errors:
            return {'error': True, 'message': errors}
        company = request.env['res.company'].sudo().search([], limit=1)
        user = request.env['res.users'].sudo().create({
            'name': kwargs['name'],
            'login': kwargs['email'],
            'email': kwargs['email'],
            'company_id': company.id,
            'company_ids': [(4, company.id)],
            'groups_id': [(6, 0, [request.env.ref('base.group_public').id])]
        })
        country_id = int(kwargs['country_id']) if kwargs['country_id'] else False
        state_id = int(kwargs['state_id']) if kwargs['state_id'] else False
        user.partner_id.mobile = kwargs['mobile']
        user.partner_id.country_id = country_id
        user.partner_id.state_id = state_id
        user.partner_id.city = kwargs['city']
        user.partner_id.zip = kwargs['zip']
        user.partner_id.comment = kwargs['comment']
        return {
            'signup': True,
            'user_id': user.id,
            'password': kwargs['password']
        }

    @route('/api/update_user_password', methods=['GET', 'POST'], type='json', auth='none', csrf=False)
    def update_user_password(self, **kwargs):
        user = request.env['res.users'].sudo().browse(int(kwargs['user_id']))
        user._change_password(kwargs['password'])
        return True
