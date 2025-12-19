import json
from odoo.http import request
import ipaddress

def get_request_data():
    """
    Extract request data for type='http' routes.

    Supports:
    - application/json
    - application/x-www-form-urlencoded
    - multipart/form-data (files + fields)
    - query params
    """
    req = request.httprequest
    data = {}

    # --------------------
    # JSON body
    # --------------------
    if req.content_type and "application/json" in req.content_type:
        try:
            return json.loads(req.data.decode("utf-8") or "{}")
        except Exception:
            return {}

    # --------------------
    # multipart/form-data
    # --------------------
    if req.content_type and "multipart/form-data" in req.content_type:
        # normal fields
        data.update(req.form.to_dict())

        # files
        for field, file in req.files.items():
            data[field] = {
                "filename": file.filename,
                "content": base64.b64encode(file.read()).decode("utf-8"),
                "mimetype": file.mimetype,
            }
        return data

    # --------------------
    # application/x-www-form-urlencoded
    # --------------------
    if req.form:
        return req.form.to_dict()

    # --------------------
    # query params
    # --------------------
    return request.params


def get_client_ip():
    """
    Get real client IP (supports proxy headers)
    """
    headers = request.httprequest.headers

    if headers.get("X-Forwarded-For"):
        return headers.get("X-Forwarded-For").split(",")[0].strip()

    return request.httprequest.remote_addr


def get_request_domain():
    """
    Extract domain from Origin or Host
    """
    headers = request.httprequest.headers

    origin = headers.get("Origin")
    if origin:
        return origin.replace("https://", "").replace("http://", "").split("/")[0]

    return headers.get("Host")

def is_ip_allowed(client_ip, allowed_ips):
    if not allowed_ips:
        return True  # no restriction

    for ip in allowed_ips.split(","):
        ip = ip.strip()
        try:
            if "/" in ip:
                if ipaddress.ip_address(client_ip) in ipaddress.ip_network(ip):
                    return True
            else:
                if client_ip == ip:
                    return True
        except Exception:
            continue

    return False


def is_domain_allowed(domain, allowed_domains):
    if not allowed_domains:
        return True  # no restriction

    for d in allowed_domains.split(","):
        d = d.strip().lower()
        if domain and domain.lower().endswith(d):
            return True

    return False


def get_api_config():
    """Return the singleton API config"""
    config = request.env["api.config"].sudo().search([("active","=",True)], limit=1)
    if not config:
        # auto-create default if missing
        config = request.env["api.config"].sudo().create({"name": "Default API Config"})
    return config


