from odoo import models, fields, api
from geopy.geocoders import Nominatim


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_lat = fields.Float(string="Check in Lattitude", digits=(10, 7), readonly=True)
    check_out_lat = fields.Float(string="Check out Lattitude", digits=(10, 7), readonly=True)
    check_in_long = fields.Float(string="Check in Longitude", digits=(10, 7), readonly=True)
    check_out_long = fields.Float(string="Check out Longitude", digits=(10, 7), readonly=True)
    address = fields.Text(string="Address", compute='get_address_from_maps', readonly=True)
    location_link = fields.Char(string="Location Link", readonly=True)
    face_image = fields.Image()
    work_area_status_in = fields.Boolean(default=True, readonly=True)
    work_area_status_out = fields.Boolean(default=True, readonly=True)

    @api.depends('check_in_lat','check_in_long')
    def get_address_from_maps(self):
        geolocator = Nominatim(user_agent='my-app')
        # for rec in self:
        #     if rec.check_in_lat and rec.check_in_long:
                # rec.address = geolocator.reverse((rec.check_in_lat, rec.check_in_long), language='en').address
                # rec.address = geolocator.reverse(str(rec.check_in_lat) + ', ' + str(rec.check_in_long)).address
                # rec.location_link = f"https://www.google.com/maps/search/?api=1&query={rec.check_in_lat},{rec.check_in_long}"