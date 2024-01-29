import logging
import json
import requests
import binascii
from passlib.context import CryptContext
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.http import request, DEFAULT_LANG
from odoo import api, fields, models,_
_logger = logging.getLogger(__name__)
import os

API_KEY_SIZE = 20 # in bytes
INDEX_SIZE = 8 # in hex digits, so 4 bytes, or 20% of the key
KEY_CRYPT_CONTEXT = CryptContext(
    # default is 29000 rounds which is 25~50ms, which is probably unnecessary
    # given in this case all the keys are completely random data: dictionary
    # attacks on API keys isn't much of a concern
    ['pbkdf2_sha512'], pbkdf2_sha512__rounds=6000,
)

class ZenResUsers(models.Model):
    _inherit = 'res.users'
    
    def _change_password(self, new_passwd):
        new_passwd = new_passwd.strip()
        if not new_passwd:
            raise UserError(_("Setting empty passwords is not allowed for security reasons!"))

        ip = request.httprequest.environ['REMOTE_ADDR'] if request else 'n/a'
        _logger.info(
            "Password change for %r (#%d) by %r (#%d) from %s",
             self.login, self.id,
             self.env.user.login, self.env.user.id,
             ip
        )

        self.password = new_passwd
        
        #FUNCTION INTEGRATION
        self.create_api_key(new_passwd)
        
        
    
    def create_api_key(self, password):
         #POST API TO DB 
        if isinstance(password, dict):
            password = password.get('password')
            
        user_ids = self.env['res.users'].sudo().search([('id','=', self.id)]).id
        
        #DETAIL POST TO DATABASE ZEN AUTH API
        username = self.env['res.users'].sudo().search([('id','=', self.id)]).login
        password = password
        org_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        org = request.session.db
        uid = user_ids
        state = self.state
        # url_post = 'http://localhost:5000/attendance/user'
        url_post = 'https://api.zentechsoft.com/attendance/user'
        try:
            payload = json.dumps({
                "username": username,
                "password": password,
                "org": org,
                "org_url": org_url,
                "uid_org": uid,
                "state": state
            })
            headers = {
                'Content-Type': 'application/json'
            }

            response = requests.request("POST", url_post, headers=headers, data=payload)
            print(response)
        except Exception as e:
            pass

        return response