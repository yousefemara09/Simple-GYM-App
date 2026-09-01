from urllib.parse import parse_qs

from psycopg2 import sql

from odoo import http
from odoo.http import request

# Only these subscriber fields may be written through the raw-SQL endpoint.
# This whitelist is what prevents arbitrary column names being injected
# through the JSON payload's keys.
SQL_ALLOWED_COLUMNS = {'name', 'email', 'phone', 'start_date', 'end_date', 'package_id'}


def valid_response(data, status, pagination=""):
    data_come = {
        'data': data
    }
    if pagination:
        data_come['pagination'] = pagination
    return request.make_json_response(data_come, status=status)


def invalid_response(data, status):
    data_come = {
        'Error': data
    }
    return request.make_json_response(data_come, status=status)


def _is_authorized():
    """Very light API-key gate for the write endpoints.

    If no key is configured in System Parameters (gym_app.api_key), the
    endpoints stay open exactly as before (useful for local testing).
    Once you set that parameter, callers must send it back in the
    X-API-KEY header, otherwise the request is rejected.
    """
    configured_key = request.env['ir.config_parameter'].sudo().get_param('gym_app.api_key')
    if not configured_key:
        return True
    provided_key = request.httprequest.headers.get('X-API-KEY')
    return provided_key == configured_key


class GymController(http.Controller):

    @http.route(['/gym/controllers'], methods=['POST'], type='http', auth="public", csrf=False)
    def create_data_gym(self):
        if not _is_authorized():
            return invalid_response({'message': 'Unauthorized'}, status=401)
        try:
            vals = request.get_json_data()
            if not vals.get('name'):
                return request.make_json_response({
                    'error': 'No name provided'
                }, status=404)
            data_create = request.env['subscriber'].sudo().create(vals)
            return valid_response({
                "message": "Subscriber added successfully",
                "id": data_create.id
            }, status=200)
        except Exception as e:
            return invalid_response({
                'Message': str(e)
            }, status=404)

    ##################################################################################################
    @http.route(['/gym/controllers/<int:subscriber_id>'], methods=['GET'], type='http', auth="public", csrf=False)
    def read_data_gym(self, subscriber_id):
        try:
            data_read = request.env['subscriber'].sudo().browse(subscriber_id)
            if not data_read.exists():
                return invalid_response({
                    'error': 'No data provided'
                }, status=404)
            return valid_response({
                'name': data_read.name,
                'phone': data_read.phone,
                'id': data_read.id
            }, status=200)
        except Exception as e:
            return invalid_response({
                'error': str(e)
            }, status=404)

    ##################################################################################################
    @http.route(['/gym/controllers/<int:subscriber_id>'], methods=['PUT'], type='http', auth="public", csrf=False)
    def update_data_gym(self, subscriber_id):
        if not _is_authorized():
            return invalid_response({'message': 'Unauthorized'}, status=401)
        data_update = request.env['subscriber'].sudo().browse(subscriber_id)
        if not data_update.exists():
            return request.make_json_response({
                'error': 'No data provided'
            }, status=404)
        vals = request.get_json_data()
        if not vals.get('name'):
            return request.make_json_response({
                'error': 'No name provided'
            }, status=404)
        data_update.write(vals)
        return request.make_json_response({
            'message': 'Data updated successfully',
            'name': data_update.name,
            'phone': data_update.phone,
            'id': data_update.id
        }, status=200)

    ##################################################################################################
    @http.route(['/gym/controllers/<int:subscriber_id>'], methods=['DELETE'], type='http', auth="public", csrf=False)
    def delete_data_gym(self, subscriber_id):
        if not _is_authorized():
            return invalid_response({'message': 'Unauthorized'}, status=401)
        data_update = request.env['subscriber'].sudo().browse(subscriber_id)
        if not data_update.exists():
            return request.make_json_response({
                'error': 'No data provided'
            }, status=404)
        data_update.unlink()
        return request.make_json_response({
            'message': 'Data Delete successfully',
        }, status=200)

    ##################################################################################################
    @http.route(['/gym/controllers/records'], methods=['GET'], type='http', auth="public", csrf=False)
    def read_all_data_gym(self):
        params = parse_qs(request.httprequest.query_string.decode('utf-8'))
        domain = []
        price = params.get('price')
        if price:
            domain.append(('price', '=', float(price[0])))
        data_read = request.env['subscriber'].sudo().search(domain)
        return request.make_json_response([{
            'name': record.name,
            'phone': record.phone,
            'price': record.price
        } for record in data_read], status=200)

    ##################################################################################################
    @http.route(['/gym/pagination/records'], methods=['GET'], type='http', auth="public", csrf=False)
    def read_pagination_data_gym(self):
        page = 1
        limit = 3
        params = parse_qs(request.httprequest.query_string.decode('utf-8'))
        if params.get('page'):
            page = int(params.get('page')[0])
            if page < 1:
                page = 1
        if params.get('limit'):
            limit = int(params.get('limit')[0])
            if limit < 1:
                return request.make_json_response({
                    'error': 'Limit must be greater than 0'
                }, status=404)
            if limit > 100:
                return request.make_json_response({
                    'error': 'Limit must be less than 100'
                }, status=404)

        offset = (page - 1) * limit

        domain = []
        price = params.get('price')
        if price:
            domain.append(('price', '=', float(price[0])))

        data_read = request.env['subscriber'].sudo().search(domain, offset=offset, limit=limit)
        return valid_response([{
            'name': record.name,
            'phone': record.phone,
            'price': record.price
        } for record in data_read], pagination={
            'limit': limit,
            'page': page,
            'offset': offset
        }, status=200)

    ##############################################################################################
    @http.route(['/gym/sql/records'], methods=['POST'], auth='none', type='http', csrf=False)
    def create_sql_data(self):
        if not _is_authorized():
            return invalid_response({'message': 'Unauthorized'}, status=401)

        vals = request.get_json_data()
        if not vals.get('name'):
            return request.make_json_response({
                "message": "Name is required",
            }, status=400)

        # SECURITY: column names were previously interpolated directly into
        # the query string, which let a caller inject arbitrary SQL through
        # the JSON payload's keys (e.g. a key containing "); DROP TABLE ...").
        # We now (1) whitelist which columns may ever be targeted and
        # (2) let psycopg2 safely quote every identifier via sql.Identifier,
        # instead of building the query with plain string formatting.
        unknown_fields = set(vals.keys()) - SQL_ALLOWED_COLUMNS
        if unknown_fields:
            return request.make_json_response({
                "message": f"Unsupported field(s): {', '.join(sorted(unknown_fields))}"
            }, status=400)

        cr = request.env.cr
        columns = list(vals.keys())
        query = sql.SQL("INSERT INTO subscriber ({fields}) VALUES ({values}) RETURNING name, phone").format(
            fields=sql.SQL(', ').join(sql.Identifier(col) for col in columns),
            values=sql.SQL(', ').join(sql.Placeholder() for _ in columns),
        )
        cr.execute(query, tuple(vals.values()))
        result = cr.fetchone()
        if result:
            return valid_response({
                'name': result[0],
                'phone': result[1],
            }, status=200)
        return invalid_response({'message': 'Insert failed'}, status=400)
    ###################################################################################################
