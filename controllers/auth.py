
import datetime, uuid
from odoo import http
from odoo.http import request
from odoo.addons.api_gateway.lib.jwt import api_jwt
import json
from functools import wraps
SECRET = "CHANGE_ME"
from .decorators import require_auth 
from .base_api import BaseApi
from .helpers import get_request_data, get_api_config


class AuthApi(BaseApi):
    API_PREFIX = "/api_gateway/v1/auth"
    
    @http.route(f"{API_PREFIX}/login", type="http", auth="none", methods=["POST"], csrf=False)
    def login(self, **kwargs):
        try:
            data = get_request_data()
            login = data.get("login")
            password = data.get("password")

            if not login or not password:
                return self.response_400("Missing login or password")

            db_name = request.env.cr.dbname
            credential = {'login': login, 'password': password, 'type': 'password'}
            auth_info = request.session.authenticate(db_name, credential)

            if not auth_info or not auth_info.get("uid"):
                return self.response_error("Invalid credentials", 401)

            uid = auth_info["uid"]
            user = request.env["res.users"].sudo().browse(uid)

            # Fetch config
            config = get_api_config()

            # JWT expiry from config
            exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=config.jwt_access_expire)
            access_token = api_jwt.encode(
                {"uid": uid, "exp": exp},
                SECRET,
                algorithm="HS256"
            )
            refresh_token = api_jwt.encode(
                {"uid": uid, "jti": uuid.uuid4().hex},
                SECRET,
                algorithm="HS256"
            )

            # Use default role from config
            existing_tokens = request.env["api.token"].sudo().search([("user_id", "=", uid)], limit=1)

            if existing_tokens and config.allow_multiple_tokens:
                # Create a new token
                token = request.env["api.token"].sudo().create({
                    "user_id": uid,
                    "role_ids": [(6, 0, [config.default_api_role_id.id])],
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expire_at": exp,
                    "active": True
                })
            else:
                # Update the existing token (or the deactivated one)
                token = existing_tokens[:1]  # pick first one
                # Merge default role with existing roles
                existing_role_ids = token.role_ids.ids
                if config.default_api_role_id.id not in existing_role_ids:
                    existing_role_ids.append(config.default_api_role_id.id)

                token.write({
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expire_at": exp,
                    "active": True,
                    "role_ids": [(6, 0, existing_role_ids)]  # assign all roles back
                })



            response = {
                "status": 200,
                "result": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": config.jwt_access_expire * 60,  # in seconds
                }
            }
            return self.response_ok(response)

        except Exception as e:
            return self.response_error(str(e), 500)


    @http.route(f"{API_PREFIX}/refresh", type="http", auth="none", methods=["POST"], csrf=False)
    def refresh(self, **kwargs):
        try:
            data = get_request_data()
            refresh_token = data.get("refresh_token")
            try:
                payload = api_jwt.decode(refresh_token, SECRET, algorithms=["HS256"])
            except Exception:
                return {"error": "Invalid refresh token"}

            token = request.env["api.token"].sudo().search([
                ("refresh_token", "=", refresh_token),
                ("active", "=", True)
            ], limit=1)
            if not token:
                return {"error": "Token revoked"}

            # Fetch config
            config = get_api_config()
            new_payload = {
                "uid": payload["uid"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=config.jwt_access_expire)
            }
            new_access = api_jwt.encode(new_payload, SECRET, algorithm="HS256")
            token.write({
                "access_token": new_access,
                "expire_at": new_payload["exp"]
            })

            response = {
                "status": 200,
                "result": {
                    "access_token": new_access,
                    "expires_in": config.jwt_access_expire * 60
                }
            }
            return self.response_ok(response)
        except Exception as e:
            return self.response_error(str(e), 500)


