# -*- coding: utf-8 -*-
import logging
from odoo import models, tools
from odoo.tools import  email_normalize, email_domain_extract, email_domain_normalize
_logger = logging.getLogger(__name__)


class ZenEmailOutgoingServer(models.Model):
    _inherit = 'ir.mail_server'

    def _find_mail_server(self, email_from, mail_servers=None, match_domain=False):
        """Find the appropriate mail server for the given email address.

        Returns: Record<ir.mail_server>, email_from
        - Mail server to use to send the email (None if we use the odoo-bin arguments)
        - Email FROM to use to send the email (in some case, it might be impossible
          to use the given email address directly if no mail server is configured for)
        """
        email_from_normalized = email_normalize(email_from)
        email_from_domain = email_domain_extract(email_from_normalized)
        notifications_email = email_normalize(self._get_default_from_address())
        notifications_domain = email_domain_extract(notifications_email)

        if mail_servers is None:
            mail_servers = self.sudo().search([], order='sequence')
            _logger.info("==== 1 ======")
            _logger.info("mail_servers: %s", mail_servers)

        # 0. Archived mail server should never be used, this gets all active mail servers
        mail_servers = mail_servers.filtered('active')

        # 1. Try to find a mail server for the right mail from
        mail_server = mail_servers.filtered(lambda m: email_normalize(m.from_filter) == email_from_normalized)
        if mail_server:
            _logger.info("==== 2 ======")
            _logger.info("mail_servers: %s", mail_server[0], "email_from: %s", email_from)
            return mail_server[0], email_from

        _logger.info("match_domain: %s", match_domain)
        if match_domain:
            mail_server = mail_servers.filtered(lambda m: email_domain_normalize(m.from_filter) == email_from_domain)
            if mail_server:
                _logger.info("==== 3 ======")
                _logger.info("mail_servers: %s", mail_server[0], "email_from: %s", email_from)
                return mail_server[0], email_from

        # 2. Try to find a mail server for <notifications@domain.com>
        if notifications_email:
            mail_server = mail_servers.filtered(lambda m: email_normalize(m.from_filter) == notifications_email)
            if mail_server:
                _logger.info("==== 4 ======")
                _logger.info("mail_servers: %s", mail_server[0], "notification_email: %s", notifications_email)
                return mail_server[0], notifications_email

            # if match_domain:
            mail_server = mail_servers.filtered(lambda m: email_domain_normalize(m.from_filter) == notifications_domain)
            if mail_server:
                _logger.info("==== 5 ======")
                _logger.info("mail_servers: %s", mail_server[0], "notification_email: %s", notifications_email)
                return mail_server[0], notifications_email

        # 3. Take the first mail server without "from_filter" because
        # nothing else has been found... Will spoof the FROM because
        # we have no other choices
        mail_server = mail_servers.filtered(lambda m: not m.from_filter)
        if mail_server:
            _logger.info("==== 6 ======")
            _logger.info("mail_servers: %s", mail_server[0], "notification_email: %s", email_from)
            return mail_server[0], email_from

        # 4. Return the first mail server even if it was configured for another domain
        # if mail_servers:
        #     _logger.info("==== 7 ======")
        #     _logger.info("mail_servers: %s", mail_servers[0], "notification_email: %s", email_from)
        #     return mail_servers[0], email_from

        # 5: SMTP config in odoo-bin arguments
        from_filter = self.env['ir.config_parameter'].sudo().get_param(
            'mail.default.from_filter', tools.config.get('from_filter'))
        _logger.info("==== 8 ======")
        _logger.info("from_filter: %s", from_filter)
        if self._match_from_filter(email_from, from_filter):
            _logger.info("==== 9 ======")
            _logger.info("email_from: %s", email_from)
            return None, email_from

        if notifications_email and self._match_from_filter(notifications_email, from_filter):
            _logger.info("==== 10 ======")
            _logger.info("notifications_email: %s", notifications_email)
            return None, notifications_email

        _logger.info("==== Finish ======")
        _logger.info("email_from: %s", email_from)
        return None, email_from