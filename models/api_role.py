from odoo import models, fields

class ApiRole(models.Model):
    _name = "api.role"
    _description = "API Role"

    name = fields.Char(required=True)
    code = fields.Char(required=True, help="Unique code for the API role")
    allowed_all_models = fields.Boolean(default=False, help="If checked, this role applies to all models")
    model_ids = fields.Many2many(
        "ir.model",
        string="Model",
        help="Select the Odoo model this role applies to"
    )

    can_read = fields.Boolean(default=True)
    can_create = fields.Boolean(default=False)
    can_write = fields.Boolean(default=False)
    can_unlink = fields.Boolean(default=False)
