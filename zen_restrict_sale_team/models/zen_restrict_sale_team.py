from odoo import models, api, _
from odoo.tools.safe_eval import safe_eval


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # @api.model
    # def _read_group_stage_ids(self, stages, domain, order):
    #     # Filter stages based on the Sales Team of the user
    #     user = self.env.user
    #     if not user.has_group('base.group_erp_manager'):
    #         domain += [('team_id', 'in', user.crm_team_ids.ids)]
    #     return super(CrmLead, self)._read_group_stage_ids(stages, domain, order)

    # @api.model
    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     # Restrict access to Sales Orders based on the Sales Team of the user
    #     user = self.env.user
    #     if not user.has_group('base.group_erp_manager'):
    #         args += [('team_id', 'in', user.crm_team_ids.ids)]
    #     return super(SaleOrder, self).search(args, offset, limit, order, count)


class Team(models.Model):
    _inherit = 'crm.team'

    #TODO JEM : refactor this stuff with xml action, proper customization,
    @api.model
    def action_your_pipeline(self):
        action = self.env["ir.actions.actions"]._for_xml_id("zen_restrict_sale_team.zen_crm_case_form_view_salesteams_opportunity")
        return self._action_update_to_pipeline(action)

    @api.model
    def _action_update_to_pipeline(self, action):
        user_team_id = self.env.user.crm_team_ids.ids
        if self.user_has_groups('sales_team.group_sale_salesman'):
            # To ensure that the team is readable in multi company
            if user_team_id:
                user_team_id = self.search([('id', 'in', user_team_id)]).ids
            else:
                my_team = self.env.user.sale_team_id.id
                user_team_id = self.search([('id', '=', my_team)], limit=1).id
        if self.user_has_groups('sales_team.group_sale_manager'):
            user_team_id = self.search([]).ids
            action['help'] = "<p class='o_view_nocontent_smiling_face'>%s</p><p>" % _("Create an Opportunity")
            if user_team_id:
                if self.user_has_groups('sales_team.group_sale_manager'):
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should <a name="%d" type="action" tabindex="-1">join a team.</a>""",
                                        self.env.ref('sales_team.crm_team_action_config').id)
                else:
                    action['help'] += "<p>%s</p>" % _("""As you are a member of no Sales Team, you are showed the Pipeline of the <b>first team by default.</b>
                                        To work with the CRM, you should join a team.""")
        action_context = safe_eval(action['context'], {'uid': self.env.uid, 'active_id': self.env.uid})
        if user_team_id:
            action['domain'] = [('team_id', 'in', user_team_id)]
        action['context'] = action_context
        return action