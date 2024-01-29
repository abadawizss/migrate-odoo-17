from odoo import models, fields


class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    lat = fields.Float(string="Lattitude", digits=(10, 7), readonly=True)
    long = fields.Float(string="Longitude", digits=(10, 7), readonly=True)
    address = fields.Text(string="Address")