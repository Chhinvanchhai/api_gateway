from odoo import models, fields, api, exceptions

class ApiConfig(models.Model):
    _name = "api.config"
    _description = "API Gateway Configuration"

    name = fields.Char("Config Name", required=True, default="Default API Config")
    api_enabled = fields.Boolean("Enable API Gateway", default=True)
    jwt_access_expire = fields.Integer("JWT Access Token Expire (minutes)", default=60)
    jwt_refresh_expire = fields.Integer("JWT Refresh Token Expire (minutes)", default=1440)
    default_api_role_id = fields.Many2one("api.role", string="Default API Role")
    allow_multiple_tokens = fields.Boolean("Allow Multiple Tokens Per User", default=False)
    active = fields.Boolean("Active", default=True)

    @api.model
    def get_singleton(self):
        """Return the single config record, create it if missing"""
        config = self.search([], limit=1)
        if not config:
            config = self.create({"name": "Default API Config"})
        return config

    @api.constrains('active')
    def _check_single_active(self):
        """Ensure only one active record exists"""
        if self.active:
            count = self.search_count([('active', '=', True), ('id', '!=', self.id)])
            if count:
                raise exceptions.ValidationError("Only one API Config can be active at a time.")
