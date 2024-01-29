from odoo import models, fields


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_lat = fields.Float(string="Check in Lattitude", digits=(10, 7), readonly=True)
    check_out_lat = fields.Float(string="Check out Lattitude", digits=(10, 7), readonly=True)
    check_in_long = fields.Float(string="Check in Longitude", digits=(10, 7), readonly=True)
    check_out_long = fields.Float(string="Check out Longitude", digits=(10, 7), readonly=True)
    address = fields.Text(string="Address")
    location_link = fields.Text(string="Location Link")
    face_image = fields.Image()