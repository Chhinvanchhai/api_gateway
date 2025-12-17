import json
from odoo import http
from odoo.http import request
from .base_api import BaseApi
from .decorators import require_auth
from .helpers import get_request_data

class DynamicModelApi(BaseApi):

    # ---------------- GET ----------------
    @http.route(
        "/api/v1/models/<string:model>",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False
    )
    @require_auth()
    def get_model_data(self, model, page=1, limit=20, fields=None, **kwargs):
        try:
            if model not in request.env:
                return self.response_error("Model not found", 404)

            if not self.check_model_permission(model, "read"):
                return self.response_error("Forbidden", 403)

            Model = request.env[model].sudo()

            if fields:
                fields = ["id"] + [f.strip() for f in fields.split(",")]
            else:
                fields = ["id", "display_name"]

            page = max(int(page), 1)
            limit = min(int(limit), 100)
            offset = (page - 1) * limit
            
            # Build domain from query params
            domain = []
            args = request.httprequest.args  # MultiDict
            domain_fields = args.getlist("domain_field")
            domain_ops = args.getlist("domain_operator")
            domain_vals = args.getlist("domain_value")

            for f, op, v in zip(domain_fields, domain_ops, domain_vals):
                # Convert "true"/"false" to boolean, numbers to int/float
                if v.lower() == "true":
                    v = True
                elif v.lower() == "false":
                    v = False
                else:
                    try:
                        v = int(v)
                    except ValueError:
                        try:
                            v = float(v)
                        except ValueError:
                            pass  # leave as string
                domain.append((f, op, v))

            total = Model.search_count(domain)
            records = Model.search(domain, offset=offset, limit=limit)
            data = records.read(fields)

            return self.response_ok({
                "model": model,
                "status": 200,
                "page": page,
                "limit": limit,
                "total": total,
                "result": data
            })

        except Exception as e:
            return self.response_error(str(e), 500)

    # ---------------- POST (Create) ----------------
    @http.route(
        "/api/v1/models/<string:model>",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False
    )
    @require_auth()
    def create_model_data(self, model, **kwargs):
        try:
            data = get_request_data()
            if model not in request.env:
                return self.response_error("Model not found", 404, type="json")

            if not self.check_model_permission(model, "create"):
                return self.response_error("Forbidden", 403, type="json")

            if not data or not isinstance(data, dict):
                return self.response_error("Missing or invalid 'data' payload", 400)

            Model = request.env[model].sudo()
            record = Model.create(data)
            return self.response_ok({"id": record.id, "status": 201, })

        except Exception as e:
            return self.response_error(str(e), 500)

    # ---------------- PUT/PATCH (Update) ----------------
    @http.route(
        "/api/v1/models/<string:model>/<int:record_id>",
        type="http",
        auth="none",
        methods=["PUT", "PATCH"],
        csrf=False
    )
    @require_auth()
    def update_model_data(self, model, record_id, **kwargs):
        try:
            if model not in request.env:
                return self.response_error("Model not found", 404)

            if not self.check_model_permission(model, "write"):
                return self.response_error("Forbidden", 403)

            data = get_request_data()
            if not data or not isinstance(data, dict):
                return self.response_error("Missing or invalid 'data' payload", 400)

            Model = request.env[model].sudo()
            record = Model.browse(record_id)
            if not record.exists():
                return self.response_error("Record not found", 404)

            result = record.write(data)
            return self.response_ok({"id": record.id, "message": "Update successful", "status": 200})

        except Exception as e:
            return self.response_error(str(e), 500)

    # ---------------- DELETE ----------------
    @http.route(
        "/api/v1/models/<string:model>/<int:record_id>",
        type="http",
        auth="none",
        methods=["DELETE"],
        csrf=False
    )
    @require_auth()
    def delete_model_data(self, model, record_id, **kwargs):
        try:
            if model not in request.env:
                return self.response_error("Model not found", 404)

            if not self.check_model_permission(model, "unlink"):
                return self.response_error("Forbidden", 403)

            Model = request.env[model].sudo()
            record = Model.browse(record_id)
            if not record.exists():
                return self.response_error("Record not found", 404)

            record.unlink()
            return self.response_ok({"id": record_id, "deleted": True})

        except Exception as e:
            return self.response_error(str(e), 500)
