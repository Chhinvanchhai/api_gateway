import json
from odoo import http
from odoo.http import request

class ApiFallback(http.Controller):

    @http.route(
        '/api_gateway/v1/<path:subpath>',
        type='http',
        auth='none',
        methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'],
        csrf=False
    )
    def api_not_found(self, subpath, **kwargs):
        return request.make_response(
            json.dumps({
                "error": "API endpoint not found",
                "path": f"/api_gateway/v1/{subpath}",
                "status": 404
            }),
            headers=[("Content-Type", "application/json")],
            status=404
        )
