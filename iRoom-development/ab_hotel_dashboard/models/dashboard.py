# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.tools.date_utils import start_of, end_of
from odoo.osv import expression


def convert_to_datetime(date_str):
    # Define the format of the date string
    date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    # Convert the string to a datetime object
    return datetime.strptime(date_str, date_format).date()


class Dashboard(models.AbstractModel):
    _name = 'ab.hotel.dashboard'
    _description = 'Reservation Dashboard'

    def get_additions_sql(self, **kwargs):
        """
        Add filtering conditions for date range and hotel_ids.
        """
        result = {'date_from':start_of(fields.Datetime.now(),'day'),'date_to':end_of(fields.Datetime.now(),'day')}
        if kwargs.get('dateFrom', False):
            result['date_from'] = start_of(fields.Datetime.to_datetime(convert_to_datetime(kwargs.get('dateFrom'))),
                                           'day')
        if kwargs.get('dateTo', False):
            result['date_to'] = end_of(fields.Datetime.to_datetime(convert_to_datetime(kwargs.get('dateTo'))), 'day')
        if kwargs.get('hotel_ids', []):
            result['hotel_ids'] = kwargs.get('hotel_ids', [])
        return result


    @api.model
    def get_total_adults_and_children_per_country(self, **kwargs):
        """
        Get total adults and children per country, with country name, and apply filter conditions if provided.
        """
        conditions = self.get_additions_sql(**kwargs)
        domain = []

        # Build the domain based on the conditions if any exist
        if conditions:
            if 'date_from' in conditions:
                domain.append(('reservation_id.date_order', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('reservation_id.date_order', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('reservation_id.shop_id', 'in', conditions['hotel_ids']))

        query = self.env['hotel.resv.id.details']._where_calc(domain)
        from_clause, where_clause, params = query.get_sql()
        # SQL Query with optional WHERE clause based on filters
        query = f"""
            SELECT rc.name AS country_name, 
                   SUM(res.adults) AS total_adults, 
                   SUM(res.childs) AS total_children
            FROM {from_clause}
            JOIN res_country AS rc ON {from_clause}.country_id = rc.id
            JOIN hotel_reservation AS res ON {from_clause}.reservation_id = res.id
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY rc.name
        """
        self._cr.execute(query, params if conditions else ())
        result = self._cr.fetchall()

        # Calculate totals for all countries
        total_adults_all = sum(total_adults or 0 for _, total_adults, _ in result)
        total_children_all = sum(total_children or 0 for _, _, total_children in result)

        # Format results by country
        country_totals = [{'country': country_name[self.env.user.lang] if country_name else 'Unknown',
                           'total_adults': total_adults or 0,
                           'total_children': total_children or 0}
                          for country_name, total_adults, total_children in result]

        # Append the overall totals
        country_totals.append({
            'country': 'Total (All)',
            'total_adults': total_adults_all,
            'total_children': total_children_all
        })
        return country_totals

    @api.model
    def get_current_bookings(self, **kwargs):  # Unused, repeated
        """
        Get current bookings filtered by check-in and check-out dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)

        # Check if there are any filtering conditions
        domain_checked_in = []
        if conditions:
            # if 'date_to' in conditions:
            #     domain_checked_in.append(('check_out', '<', conditions['date_to']))
            if 'date_from' in conditions:
                domain_checked_in.append(('check_in', '>', conditions['date_from']))
            if 'hotel_ids' in conditions:
                domain_checked_in.append(('booking_id.shop_id', 'in', conditions['hotel_ids']))

        query_checked_in = self.env['hotel.room.booking.history']._where_calc(domain_checked_in)
        from_clause, where_clause, params = query_checked_in.get_sql()

        query_checked_in = f"""
            SELECT {from_clause}.history_id, partner.name, {from_clause}.check_in, {from_clause}.check_out
            FROM {from_clause}
            JOIN res_partner partner ON {from_clause}.partner_id = partner.id
            JOIN hotel_reservation AS res ON {from_clause}.booking_id = res.id
            {f'WHERE {where_clause}' if conditions else ''}
        """
        self._cr.execute(query_checked_in, params if conditions else ())
        checked_in = self._cr.fetchall()
        # Similar logic for checked_out bookings
        domain_checked_out = []
        if conditions:
            if 'date_to' in conditions:
                domain_checked_out.append(('check_out', '<', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain_checked_out.append(('booking_id.shop_id', 'in', conditions['hotel_ids']))

        query_checked_out = self.env['hotel.room.booking.history']._where_calc(domain_checked_out)
        from_clause, where_clause, params = query_checked_out.get_sql()

        query_checked_out = f"""
            SELECT {from_clause}.history_id, partner.name, {from_clause}.check_in, {from_clause}.check_out
            FROM {from_clause}
            JOIN res_partner partner ON {from_clause}.partner_id = partner.id
            JOIN hotel_reservation AS res ON {from_clause}.booking_id = res.id
            {f'WHERE {where_clause}' if conditions else ''}
        """
        self._cr.execute(query_checked_out, params if conditions else ())
        checked_out = self._cr.fetchall()

        # Similar logic for in-house bookings
        domain_in_house = []
        if conditions:
            if 'date_from' in conditions:
                domain_in_house.append(('check_in', '<=', conditions['date_from']))
            if 'date_to' in conditions:
                domain_in_house.append(('check_out', '>', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain_in_house.append(('booking_id.shop_id', 'in', conditions['hotel_ids']))

        query_in_house = self.env['hotel.room.booking.history']._where_calc(domain_in_house)
        from_clause, where_clause, params = query_in_house.get_sql()

        query_in_house = f"""
            SELECT {from_clause}.history_id, partner.name, {from_clause}.check_in, {from_clause}.check_out
            FROM {from_clause}
            JOIN res_partner partner ON {from_clause}.partner_id = partner.id
            JOIN hotel_reservation AS res ON {from_clause}.booking_id = res.id
            {f'WHERE {where_clause}' if conditions else ''}
        """
        self._cr.execute(query_in_house, params if conditions else ())
        in_house = self._cr.fetchall()
        return {
            'checked_in': checked_in,
            'checked_out': checked_out,
            'in_house': in_house,
        }

    @api.model
    def get_current_bookings(self, **kwargs):
        """ Get current bookings filtered by check-in and check-out dates and hotel. """
        conditions = self.get_additions_sql(**kwargs)

        # Check if there are any filtering conditions
        domain_checked_in = [('line_id.state', 'in', ['confirm'])]
        if conditions:
            if 'date_from' in conditions:
                domain_checked_in.append(('checkin', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain_checked_in.append(('checkin', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain_checked_in.append(('line_id.shop_id', 'in', conditions['hotel_ids']))

        query_checked_in = self.env['hotel.reservation.line']._where_calc(domain_checked_in)
        from_clause, where_clause, params = query_checked_in.get_sql()

        query_checked_in = f"""
            SELECT {from_clause}.room_number, partner.name, {from_clause}.checkin, {from_clause}.checkout, hs.reservation_no
            FROM {from_clause}
            JOIN hotel_reservation AS hs ON {from_clause}.line_id = hs.id
            JOIN res_partner partner ON hs.partner_id = partner.id
            {f'WHERE {where_clause}' if conditions else ''}
        """
        self._cr.execute(query_checked_in, params if conditions else ())
        checked_in = self._cr.fetchall()
        # Similar logic for checked_out bookings
        domain_checked_out = [('line_id.state', 'in', ['done'])]
        if conditions:
            if 'date_from' in conditions:
                domain_checked_out.append(('checkout', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain_checked_out.append(('checkout', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain_checked_out.append(('line_id.shop_id', 'in', conditions['hotel_ids']))

        query_checked_out = self.env['hotel.reservation.line']._where_calc(domain_checked_out)
        from_clause, where_clause, params = query_checked_out.get_sql()

        query_checked_out = f"""
            SELECT {from_clause}.room_number, partner.name, {from_clause}.checkin, {from_clause}.checkout, hs.reservation_no
            FROM {from_clause}
            JOIN hotel_reservation AS hs ON {from_clause}.line_id = hs.id
            JOIN res_partner partner ON hs.partner_id = partner.id
            LEFT JOIN hotel_folio folio ON hs.id = folio.reservation_id
            WHERE folio.state != 'checkout' {f'AND {where_clause}' if conditions else ''}
        """
        self._cr.execute(query_checked_out, params if conditions else ())
        checked_out = self._cr.fetchall()

        # Similar logic for in-house bookings
        domain_in_house = [('line_id.state', 'not in', ['draft', 'cancel'])]
        check_in_domain = []
        check_out_domain = []
        if conditions:
            if 'date_from' in conditions:
                check_in_domain.append(('checkin', '>=', conditions['date_from']))
                check_out_domain.append(('checkout', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                check_in_domain.append(('checkin', '<=', conditions['date_to']))
                check_out_domain.append(('checkout', '<=', conditions['date_to']))
            dates_domain = expression.OR([check_in_domain, check_out_domain])
            domain_in_house = expression.AND([domain_in_house, dates_domain])
            if 'hotel_ids' in conditions:
                domain_in_house = expression.AND([domain_in_house, [('line_id.shop_id', 'in', conditions['hotel_ids'])]])

        query_in_house = self.env['hotel.reservation.line']._where_calc(domain_in_house)
        from_clause, where_clause, params = query_in_house.get_sql()

        query_in_house = f"""
            SELECT {from_clause}.room_number, partner.name, {from_clause}.checkin, {from_clause}.checkout, hs.reservation_no
            FROM {from_clause}
            JOIN hotel_reservation AS hs ON {from_clause}.line_id = hs.id
            JOIN res_partner partner ON hs.partner_id = partner.id
            LEFT JOIN hotel_folio folio ON hs.id = folio.reservation_id
            WHERE folio.state != 'checkout' {f'AND {where_clause}' if conditions else ''}
        """
        self._cr.execute(query_in_house, params if conditions else ())
        in_house = self._cr.fetchall()
        return {
            'checked_in': checked_in,
            'checked_out': checked_out,
            'in_house': in_house,
        }

    @api.model
    def count_reservations_by_status(self, **kwargs):
        """
        Count reservations by status, filtered by dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)
        domain = []
        if conditions:
            if 'date_from' in conditions:
                domain.append(('date_order', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('date_order', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('shop_id', 'in', conditions['hotel_ids']))

        query = self.env['hotel.reservation']._where_calc(domain)
        from_clause, where_clause, params = query.get_sql()

        query = f"""
            SELECT state, COUNT(*)
            FROM {from_clause}
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY state
        """
        self._cr.execute(query, params if conditions else ())
        result = self._cr.fetchall()

        status_counts = {status: count for status, count in result}
        return status_counts

    @api.model
    def count_reservations_by_via(self, **kwargs):
        """
        Count reservations by status, filtered by dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)
        domain = []
        if conditions:
            if 'date_from' in conditions:
                domain.append(('date_order', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('date_order', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('shop_id', 'in', conditions['hotel_ids']))

        query = self.env['hotel.reservation']._where_calc(domain)
        from_clause, where_clause, params = query.get_sql()

        query = f"""
            SELECT via, COUNT(*)
            FROM {from_clause}
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY via
        """
        self._cr.execute(query, params if conditions else ())
        result = self._cr.fetchall()

        via_counts = {via: count for via, count in result}
        return via_counts

    @api.model
    def count_reservations_by_source(self, **kwargs):
        """
        Count reservations by source, filtered by dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)
        domain = []
        if conditions:
            if 'date_from' in conditions:
                domain.append(('date_order', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('date_order', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('shop_id', 'in', conditions['hotel_ids']))

        query = self.env['hotel.reservation']._where_calc(domain)
        from_clause, where_clause, params = query.get_sql()

        query = f"""
            SELECT source, COUNT(*)
            FROM {from_clause}
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY source
        """
        self._cr.execute(query, params if conditions else ())
        result = self._cr.fetchall()

        sources_counts = {source: count for source, count in result}
        return sources_counts

    @api.model
    def get_gender_counts(self, **kwargs):
        """
        Count gender-based records, filtered by dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)
        domain = []
        if conditions:
            if 'date_from' in conditions:
                domain.append(('reservation_id.date_order', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('reservation_id.date_order', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('reservation_id.shop_id', 'in', conditions['hotel_ids']))

        query = self.env['hotel.resv.id.details']._where_calc(domain)
        from_clause, where_clause, params = query.get_sql()

        query = f"""
            SELECT {from_clause}.gender, COUNT(*)
            FROM {from_clause}
            JOIN hotel_reservation AS res ON {from_clause}.reservation_id = res.id
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY {from_clause}.gender
        """
        self._cr.execute(query, params if conditions else ())
        result = self._cr.fetchall()

        gender_counts = {gender: count for gender, count in result}
        return gender_counts

    @api.model
    def get_country_counts(self, **kwargs):
        """
        Count records by country, filtered by dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)
        domain = []
        if conditions:
            if 'date_from' in conditions:
                domain.append(('reservation_id.date_order', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('reservation_id.date_order', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('reservation_id.shop_id', 'in', conditions['hotel_ids']))

        query = self.env['hotel.resv.id.details']._where_calc(domain)
        from_clause, where_clause, params = query.get_sql()

        query = f"""
            SELECT c.name, COUNT(*)
            FROM {from_clause}
            LEFT JOIN res_country c ON {from_clause}.country_id = c.id
            JOIN hotel_reservation AS res ON {from_clause}.reservation_id = res.id
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY c.name
        """
        self._cr.execute(query, params if conditions else ())
        result = self._cr.fetchall()

        country_counts = {country_name[self.env.user.lang] if country_name else 'Unknown': count for country_name, count
                          in result}
        return country_counts

    @api.model
    def get_room_available(self, **kwargs):
        # Retrieve conditions with date_from and date_to
        conditions = self.get_additions_sql(**kwargs)
        date_from = conditions['date_from']
        date_to = conditions['date_to']
        shop_ids = conditions.get('shop_ids', [])

        # Dynamic shop_ids filter if provided
        shop_ids_condition = ""
        if shop_ids:
            shop_ids_condition = "AND l.shop_id IN %s"

        # Adjusted query to join product_template and use it in conditions
        query = f"""
            SELECT
                pc.name AS room_type,
                COUNT(DISTINCT(pp.id)) AS total_rooms,
                COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL THEN pp.id END)), 0) AS sold_rooms,
                (COUNT(DISTINCT(pt.id)) - COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL THEN pp.id END)), 0)) AS available_rooms,
                CASE 
                    WHEN 
                        (COUNT(DISTINCT(pt.id)) - COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL THEN pp.id END)), 0)) = COUNT(DISTINCT(pt.id)) 
                    THEN 
                        'Available' 
                    WHEN 
                        (COUNT(DISTINCT(pt.id)) - COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL THEN pp.id END)), 0)) > 0  
                    THEN 
                        'Partial Available' 
                    ELSE 
                        'Unavailable' 
                END AS status
            FROM
                product_category pc
            JOIN
                product_template pt ON pt.categ_id = pc.id
            JOIN
                product_product pp ON pp.product_tmpl_id = pt.id AND pp.isroom = TRUE
            LEFT JOIN
                hotel_reservation_line hrl ON hrl.room_number = pp.id
                AND ((hrl.checkin BETWEEN %s AND %s) OR (hrl.checkout BETWEEN %s AND %s))
            LEFT JOIN
                hotel_reservation l ON hrl.line_id = l.id
                {shop_ids_condition}
            GROUP BY
                pc.name;
        """

        params = [date_from, date_to, date_from, date_to]
        if shop_ids:
            params.append(tuple(shop_ids))

        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()

        # Format the result as a list of dictionaries
        room_availability = [{
            'room_type': row[0],
            'total_rooms': row[1],
            'sold_rooms': row[2],
            'available_rooms': row[3],
            'status': row[4],
        } for row in result]

        return room_availability

    @api.model
    def get_occupied_rooms(self, **kwargs):
        # Retrieve conditions with date_from and date_to
        conditions = self.get_additions_sql(**kwargs)
        date_from = conditions['date_from']
        date_to = conditions['date_to']
        shop_ids = conditions.get('shop_ids', [])

        # Dynamic shop_ids filter if provided
        shop_ids_condition = ""
        if shop_ids:
            shop_ids_condition = "AND l.shop_id IN %s"

        # Adjusted query to join product_template and use it in conditions
        query = f"""
            SELECT
                COUNT(DISTINCT(pp.id)) AS total_rooms,
                COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL AND hrl.checkin >= %s AND hrl.checkout <= %s THEN pp.id END)), 0) AS totally_sold_rooms,
                COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL AND (hrl.checkin < %s OR hrl.checkout > %s) THEN pp.id END)), 0) AS partially_sold_rooms,
                (COUNT(DISTINCT(pp.id)) - COALESCE(COUNT(DISTINCT(CASE WHEN hrl.id IS NOT NULL THEN pp.id END)), 0)) AS available_rooms
            FROM
                product_category pc
            JOIN
                product_template pt ON pt.categ_id = pc.id
            JOIN
                product_product pp ON pp.product_tmpl_id = pt.id AND pp.isroom = TRUE
            LEFT JOIN
                hotel_reservation_line hrl ON hrl.room_number = pp.id
                AND ((hrl.checkin BETWEEN %s AND %s) OR (hrl.checkout BETWEEN %s AND %s))
            LEFT JOIN
                hotel_reservation l ON hrl.line_id = l.id
                {shop_ids_condition}
        """

        params = [date_from, date_to,  # For Fully occupied
                  date_from, date_to,  # For Partially occupied
                  date_from, date_to,  # For Join
                  date_from, date_to  # For Join
                  ]
        if shop_ids:
            params.append(tuple(shop_ids))

        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()

        return {
            'Fully Occupied': result[0][1],
            'Partially Occupied': result[0][2],
            'Available': result[0][3],
        }

    @api.model
    def get_occupancy(self, **kwargs):
        # Retrieve 7-days occupancy, will use orm as the query will be complex
        # Retrieve conditions with date_from and date_to
        conditions = self.get_additions_sql(**kwargs)
        date_from = conditions['date_from']
        date_to = conditions['date_to']
        shop_ids = conditions.get('shop_ids', [])

        # Dynamic shop_ids filter if provided
        occupy_shop_condition = ""
        total_shop_condition = ""
        total_domain = []
        if shop_ids:
            total_domain += [('shop_id', 'in', shop_ids)]
            occupy_shop_condition = "AND l.shop_id IN %s"
            total_shop_condition = "JOIN pt.shop_id IN %s"

        query = f"""
                SELECT
                    COUNT(pt.id) AS total_rooms
                FROM
                    product_category pc
                JOIN
                    product_template pt ON pt.categ_id = pc.id
                JOIN
                    product_product pp ON pp.product_tmpl_id = pt.id AND pp.isroom = TRUE
                {total_shop_condition}
            """
        # self.env.cr.execute(query, [])
        total_rooms = len(self.env['hotel.room'].search(total_domain))

        query = f"""
            WITH date_range AS (
                SELECT generate_series(
                    %s::date, 
                    %s::date + interval '6 days', 
                    interval '1 day'
                )::date AS day
            )
            SELECT TO_CHAR(dr.day, 'Day') AS weekday, COUNT(hrl.id) AS occupied_rooms
            FROM
                date_range dr
            LEFT JOIN 
                hotel_reservation_line hrl ON dr.day BETWEEN hrl.checkin AND hrl.checkout
            LEFT JOIN
                hotel_reservation l ON hrl.line_id = l.id
                {occupy_shop_condition}
            GROUP BY dr.day, weekday
            ORDER BY dr.day;
    """

        params = [date_from, date_from]
        if shop_ids:
            params.append(tuple(shop_ids))

        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()
        result = dict(result)
        percentage_result = {key: round(value * 100 / total_rooms, 2) if total_rooms else 0 for key, value in result.items()}

        return percentage_result

    @api.model
    def get_house_keepings(self, **kwargs):
        """
        Get current bookings filtered by check-in and check-out dates and hotel.
        """
        conditions = self.get_additions_sql(**kwargs)

        # Check if there are any filtering conditions
        domain = [('state', '!=', 'cancel')]
        if conditions:
            # if 'date_to' in conditions:
            #     domain_checked_in.append(('check_out', '<', conditions['date_to']))
            if 'date_from' in conditions:
                domain.append(('current_date', '>=', conditions['date_from']))
            if 'date_to' in conditions:
                domain.append(('current_date', '<=', conditions['date_to']))
            if 'hotel_ids' in conditions:
                domain.append(('room_no.shop_id', 'in', conditions['hotel_ids']))

        query_house_keep = self.env['hotel.housekeeping']._where_calc(domain)
        from_clause, where_clause, params = query_house_keep.get_sql()

        query_house_keep = f"""
            SELECT state, COUNT(id)
            FROM {from_clause}
            {f'WHERE {where_clause}' if conditions else ''}
            GROUP BY state
        """
        self._cr.execute(query_house_keep, params if conditions else ())
        house_keepings = self._cr.fetchall()

        return dict(house_keepings)

    @api.model
    def get_services(self, **kwargs):
        # Retrieve conditions with date_from and date_to
        conditions = self.get_additions_sql(**kwargs)
        date_from = conditions['date_from']
        date_to = conditions['date_to']
        shop_ids = conditions.get('shop_ids', [])

        # Dynamic shop_ids filter if provided
        shop_ids_condition = ""
        if shop_ids:
            shop_ids_condition = "AND pp.shop_id IN %s"

        # Adjusted query to join product_template and use it in conditions
        query = f"""
                    SELECT
                        COALESCE(pt.name->>%s, pt.name->>'en_US')  AS service_name,
                        SUM(sol.product_uom_qty) AS count, 
                        ROUND(SUM(sol.price_total), 2) AS earning
                    FROM 
                        hotel_service_line hsl
                    JOIN 
                        sale_order_line sol ON sol.id = hsl.service_line_id  -- Delegation
                    JOIN
                        product_product pp ON pp.id = sol.product_id AND pp.isservice = TRUE
                        {shop_ids_condition}
                    JOIN
                        product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN
                        hotel_folio_line hfl
                    ON 
                        hfl.folio_id = hsl.folio_id 
                        AND 
                            NOT (hfl.checkout_date < %s OR hfl.checkin_date > %s)
                    GROUP BY 
                        pt.name
                """

        params = [self.env.lang or 'en_US', date_from, date_to]

        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()

        # Format the result as a list of dictionaries
        services = [{
            'service': row[0],
            'orders': row[1],
            'earnings': row[2],
        } for row in result]

        return {
            'services': services,
            'total_earnings': round(sum([s['earnings'] for s in services]), 2),
            'total_orders': sum([s['orders'] for s in services]),
        }

    @api.model
    def get_occupy_table_data(self, **kwargs):
        occupancy = self.get_occupancy(**kwargs)

        # Retrieve conditions with date_from and date_to
        conditions = self.get_additions_sql(**kwargs)
        date_from = conditions['date_from']
        date_to = conditions['date_to']
        shop_ids = conditions.get('shop_ids', [])

        # Dynamic shop_ids filter if provided
        shop_ids_condition = ""
        if shop_ids:
            shop_ids_condition = "AND l.shop_id IN %s"

        # Adjusted query to join product_template and use it in conditions
        query = f"""
            WITH date_range AS (
                SELECT generate_series(
                        %s::date, 
                        %s::date + interval '6 days', 
                        interval '1 day'
                    )::date AS day
                )
                SELECT 
                    TO_CHAR(dr.day, 'Day') AS weekday, 
                    SUM(CASE WHEN hrl.checkin = dr.day THEN 1 ELSE 0 END) AS arrivals,
                    SUM(CASE WHEN hrl.checkout = dr.day THEN 1 ELSE 0 END) AS departures,
                    SUM(CASE WHEN hrl.checkout > dr.day AND hrl.checkin < dr.day THEN 1 ELSE 0 END) AS stays
                FROM
                    date_range dr
                LEFT JOIN 
                    hotel_reservation_line hrl ON dr.day BETWEEN hrl.checkin AND hrl.checkout
                LEFT JOIN
                    hotel_reservation l ON hrl.line_id = l.id
                    {shop_ids_condition}
                GROUP BY dr.day, weekday
                ORDER BY dr.day;
            """

        params = [date_from, date_from]

        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()

        # Format the result as a list of dictionaries

        data_by_date = []
        for i, res in enumerate(result, 1):
            data_by_date += [{'index': i, 'day': res[0], 'occupy': occupancy[res[0]], 'arrivals': res[1], 'departures': res[2], 'stays': res[3]}]

        return data_by_date

    @api.model
    def get_rating_table_data(self, **kwargs):
        # Retrieve conditions with date_from and date_to
        conditions = self.get_additions_sql(**kwargs)
        date_from = conditions['date_from']
        date_to = conditions['date_to']
        shop_ids = conditions.get('shop_ids', [])

        # Dynamic shop_ids filter if provided
        shop_ids_condition = ""
        if shop_ids:
            shop_ids_condition = "AND hr.shop_id IN %s"

        # Adjusted query to join product_template and use it in conditions
        query = f"""
            SELECT
                hr.name AS reservation_name,
                partner.name AS guest_name,
                hr_rate.cleanliness AS cleanliness,
                hr_rate.comfort AS comfort,
                hr_rate.staff AS staff,
                hr_rate.facilities_and_services AS services,
                hr_rate.total_rate AS rate
            FROM
                hotel_reservation_rating hr_rate
            JOIN
                hotel_reservation hr
                ON hr.id = hr_rate.reservation_id
                {shop_ids_condition}
            JOIN
                hotel_reservation_line hrl
                ON hrl.line_id = hr.id
                AND ((hrl.checkin BETWEEN %s AND %s) OR (hrl.checkout BETWEEN %s AND %s))
            JOIN
                res_partner partner
                ON partner.id = hr.partner_id
            """

        params = [date_from, date_to, date_from, date_to]

        self.env.cr.execute(query, params)
        result = self.env.cr.fetchall()

        # Format the result as a list of dictionaries
        data_by_reserve = []
        for i, res in enumerate(result, 1):
            data_by_reserve += [
                {
                    'index': i,
                    'reservation_name': res[0],
                    'guest_name': res[1],
                    'cleanliness': res[2],
                    'comfort': res[3],
                    'staff': res[4],
                    'services': res[5],
                    'rate': res[6]
                }]

        return data_by_reserve
