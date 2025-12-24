from odoo import http
from odoo.http import request
import os
import json
from odoo.modules import get_module_path  # <-- correct import

class APIDocs(http.Controller):

    @http.route('/api_gateway/v1/docs', type='http', auth='none', website=True)
    def swagger_ui(self):
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Odoo API Gateway Docs</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist/swagger-ui-bundle.js"></script>
            <script>
                const ui = SwaggerUIBundle({
                    url: '/api_gateway/v1/swagger.json',
                    dom_id: '#swagger-ui',
                });
            </script>
        </body>
        </html>
        """

    @http.route('/api_gateway/v1/swagger.json', type='http', auth='none', website=True)
    def swagger_json(self):
        """Serve swagger.json with dynamic server URL"""
        module_path = get_module_path('api_gateway')
        file_path = os.path.join(module_path, 'docs', 'swagger.json')
        
        # Load static JSON first
        with open(file_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        
        # Dynamically set the server URL based on current request
        scheme = request.httprequest.scheme  # http or https
        host = request.httprequest.host      # domain + port
        spec['servers'] = [{"url": f"{scheme}://{host}", "description": "Dynamic Odoo server"}]

        return request.make_response(
            json.dumps(spec),
            headers=[('Content-Type', 'application/json')]
        )
