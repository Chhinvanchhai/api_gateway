import json
from odoo import http
from odoo.http import request
from .base_api import BaseApi
from .decorators import require_auth
from .helpers import get_request_data
import base64


class DynamicModelApi(BaseApi):

    # ---------------- GET ----------------
    @http.route(
        "/api/v1/models/<string:model>/<int:record_id>",
        type="http",
        auth="none",
        methods=["GET"],
        csrf=False
    )
    @require_auth()
    def get_model_data_one(self, model, record_id, fields=None, **kwargs):
        try:
            # 1️⃣ Validate model
            if model not in request.env:
                return self.response_error("Model not found", 404)

            if not self.check_model_permission(model, "read"):
                return self.response_error("Forbidden", 403)

            Model = request.env[model].sudo()

            # 2️⃣ Parse fields
            if fields:
                fields = ["id"] + [f.strip() for f in fields.split(",")]
            else:
                fields = ["id", "display_name"]

            args = request.httprequest.args
            domain = []
            try:
                domain = self.build_domain_from_request()
            except ValueError as e:
                return self.response_error(str(e), 400)
            # 5️⃣ Search
            records = Model.browse(record_id)
            data = records.read(fields)
            
            expand = request.params.get("expand")
            if  expand == 'true' or expand == 'True':
                data = self._expand_relations(records, data)

            return self.response_ok({
                "model": model,
                "status": 200,
                "result": data[0] or {}
            })

        except Exception as e:
            return self.response_error(str(e), 500)


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
            # 1️⃣ Validate model
            if model not in request.env:
                return self.response_error("Model not found", 404)

            if not self.check_model_permission(model, "read"):
                return self.response_error("Forbidden", 403)

            Model = request.env[model].sudo()

            # 2️⃣ Parse fields
            if fields:
                fields = ["id"] + [f.strip() for f in fields.split(",")]
            else:
                fields = ["id", "display_name"]

            # 3️⃣ Pagination
            page = max(int(page), 1)
            limit = min(int(limit), 100)
            offset = (page - 1) * limit

            # 4️⃣ Domain builder
            args = request.httprequest.args
            domain = []
            try:
                domain = self.build_domain_from_request()
            except ValueError as e:
                return self.response_error(str(e), 400)
            # 5️⃣ Search
            total = Model.search_count(domain)
            records = Model.search(domain, offset=offset, limit=limit)
            data = records.read(fields)
            
            expand = request.params.get("expand")
            if  expand == 'true' or expand == 'True':
                data = self._expand_relations(records, data)

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
        

    @http.route(
        "/api/v1/models/<string:model>/<int:record_id>/attachment",
        type="http",
        auth="none",
        methods=["POST"],
        csrf=False
    )
    @require_auth()
    def add_attachment(self, model, record_id, **kwargs):
        try:
            if model not in request.env:
                return self.response_error("Model not found", 404)

            if not self.check_model_permission(model, "write"):
                return self.response_error("Forbidden", 403)

            Model = request.env[model].sudo()
            record = Model.browse(record_id)
            if not record.exists():
                return self.response_error("Record not found", 404)

            req = request.httprequest
            if not req.content_type or "multipart/form-data" not in req.content_type:
                return self.response_error("multipart/form-data required", 400)

            # Collect all uploaded files, grouped by field name
            files_by_field = {}
            for key in req.files:
                files_by_field[key] = req.files.getlist(key)

            if not files_by_field:
                return self.response_error("No file uploaded", 400)

            Attachment = request.env["ir.attachment"].sudo()
            result = {}

            # Iterate over each field
            for field_name, files in files_by_field.items():
                field = record._fields.get(field_name)
                if not field:
                    result[field_name] = {"error": "Field not found"}
                    continue

                # Binary field (take the first file)
                if field.type == "binary":
                    file = files[0]
                    record.write({field_name: base64.b64encode(file.read())})
                    result[field_name] = {
                        "type": "binary",
                        "filename": file.filename,
                        "message": "Binary field updated"
                    }

                # Many2many to ir.attachment
                elif field.type == "many2many" and field.comodel_name == "ir.attachment":
                    attachment_ids = []
                    for file in files:
                        attachment = Attachment.create({
                            "name": file.filename,
                            "datas": base64.b64encode(file.read()),
                            "res_model": model,
                            "res_id": record.id,
                            "mimetype": file.mimetype,
                        })
                        attachment_ids.append(attachment.id)

                    record.write({field_name: [(4, att_id) for att_id in attachment_ids]})
                    result[field_name] = {
                        "type": "many2many",
                        "attachments": attachment_ids,
                        "message": "Attachments added"
                    }
                else:
                    result[field_name] = {"error": "Unsupported field type"}

            return self.response_ok({
                "id": record.id,
                "uploaded": result
            })

        except Exception as e:
            return self.response_error(str(e), 500)
