from odoo import models, fields, api
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    check_in_lat = fields.Float(string="Check in Lattitude", default=0.0, digits=(10, 7), readonly=True)
    check_out_lat = fields.Float(string="Check out Lattitude", default=0.0, digits=(10, 7), readonly=True)
    check_in_long = fields.Float(string="Check in Longitude", default=0.0, digits=(10, 7), readonly=True)
    check_out_long = fields.Float(string="Check out Longitude", default=0.0, digits=(10, 7), readonly=True)
    geotag = fields.Char(string="Geotag", compute='_compute_geotag', store=True)
    out_geotag = fields.Char(string="Out geotag", compute='_compute_geotag', store=True)
    address = fields.Text(string="Address", compute='get_address_from_maps')
    out_address = fields.Text(string="Out Address", compute='get_address_out_from_maps')
    location_url = fields.Char(string="Location url", readonly=True)
    out_location_url = fields.Char(string="Out Location url", readonly=True)
    face_image = fields.Image()
    work_area_status_in = fields.Boolean(default=True, readonly=True)
    work_area_status_out = fields.Boolean(default=True, readonly=True)

    @api.depends('check_in_lat','check_in_long','check_out_lat','check_out_long')
    def _compute_geotag(self):
        for rec in self:
            rec.geotag=f'{rec.check_in_lat},{rec.check_in_long}'
            rec.out_geotag=f'{rec.check_out_lat},{rec.check_out_long}'

    @api.depends('check_in_lat', 'check_in_long')
    def get_address_from_maps(self):
        geolocator = Nominatim(user_agent='my-app')
        for rec in self:
            rec.address = ''
            rec.location_url = ''
            if rec.check_in_lat != 0 and rec.check_in_long != 0:
                try:
                    location = geolocator.reverse((rec.check_in_lat, rec.check_in_long), language='en')
                    if location and location.address:
                        rec.address = location.address
                        rec.location_url = f"https://www.google.com/maps/search/?api=1&query={rec.check_in_lat},{rec.check_in_long}"
                except GeocoderTimedOut:
                    pass

    @api.depends('check_out_lat', 'check_out_long')
    def get_address_out_from_maps(self):
        geolocator = Nominatim(user_agent='my-app')
        for rec in self:
            rec.out_address = ''
            rec.out_location_url = ''
            if rec.check_out_lat != 0 and rec.check_out_long != 0:
                try:
                    location = geolocator.reverse((rec.check_out_lat, rec.check_out_long), language='en')
                    if location and location.address:
                        rec.out_address = location.address
                        rec.out_location_url = f"https://www.google.com/maps/search/?api=1&query={rec.check_out_lat},{rec.check_out_long}"
                except GeocoderTimedOut:
                    pass