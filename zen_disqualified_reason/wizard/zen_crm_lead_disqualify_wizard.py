# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools.mail import is_html_empty


class CrmLeadLost(models.TransientModel):
    _name = 'crm.lead.disqualification'
    _description = 'Get Disqualification Reason'

    disqualify_reason_id = fields.Many2one('zen.crm.disqualify.reason', string='Disqualification Reason')
    disqualify_feedback = fields.Text('Closing Note', sanitize=True, required=True)

    def action_disqualify_reason_apply(self):
        self.ensure_one()
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        leads._track_set_log_message(
            '<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>' % (
                _('Disqualified Comment'),
                f"{self.disqualify_reason_id.name} - {self.disqualify_feedback}"
            )
        )
        stage = self.env['crm.stage'].search([('name','ilike', 'Disqualified')],limit=1)
        if stage:
            stage_disqualified = stage
        if not stage:
            stage_disqualified = self.env['crm.stage'].create({'name': 'Disqualified'})
        
        res = leads.write({'stage_id': stage_disqualified.id, 'probability': 0})
        return res
