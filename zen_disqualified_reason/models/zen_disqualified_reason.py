# -*- coding: utf-8 -*-
from odoo import models, fields,_


class ZenCRMLeads(models.Model):
    _inherit = 'crm.lead'
    _description = 'CRM Lead'

    show_button_disualify = fields.Boolean(compute='_show_button_disqualify')

    def _show_button_disqualify(self):
        for rec in self:
            if rec.stage_id.name != 'Disqualified':
                rec.show_button_disualify = True
            else:
                rec.show_button_disualify = False
    
    def action_disqualification(self):
        form_view_id = self.env.ref('zen_disqualified_reason.crm_lead_disqualify_view_form').id
        action =  {
            'name': _('Disqualification Reason'),
            'view_mode': 'form',
            'res_model': 'crm.lead.disqualification',
            'view_id': form_view_id,
            'views': [(form_view_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return action


class ZenCRMLeadsDisqualifyReason(models.Model):
    _name = 'zen.crm.disqualify.reason'
    _description = 'Disqualify Reasons'

    name = fields.Char('Description') 