# -*- coding: utf-8 -*-

import urllib
import json
from datetime import timedelta, datetime
from odoo import api, fields, models, _
import pytz


class IndiaMartConfiguration(models.Model):
    _name = "indiamart.configuration"
    _description = "Indiamart Configuration"

    name = fields.Char('Name')
    mobile_key = fields.Char('Mobile Key', required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], 'State', default='draft')
    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')

    def action_confirm(self):
        self.write({'state': 'confirm'})

    