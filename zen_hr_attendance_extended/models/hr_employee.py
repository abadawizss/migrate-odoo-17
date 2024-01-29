from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    device = fields.Char(string="Device")
    face_image = fields.Image()