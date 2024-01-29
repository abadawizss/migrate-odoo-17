from odoo import models, fields


class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    lat = fields.Float(string="Lattitude", digits=(10, 7))
    long = fields.Float(string="Longitude", digits=(10, 7))
    address = fields.Text(string="Address")