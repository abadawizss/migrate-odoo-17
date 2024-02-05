from odoo import models, fields, api


class HrWorkLocation(models.Model):
    _inherit = 'hr.work.location'

    lat = fields.Float(string="Lattitude", digits=(10, 7))
    long = fields.Float(string="Longitude", digits=(10, 7))
    geotag = fields.Char(string="Geotag", compute='_compute_geotag', store=True)
    address = fields.Text(string="Address")

    @api.depends('lat','long')
    def _compute_geotag(self):
        for rec in self:
            rec.geotag=f'{rec.lat},{rec.long}'