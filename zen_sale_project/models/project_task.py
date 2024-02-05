from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    name = fields.Char(string="Task Name")
    # Define a Many2many field for the task followers
    follower_ids = fields.Many2many('res.partner', 'project_task_followers_rel', 'task_id', 'partner_id', string='Followers')

    def write(self, vals):
        # Check if the stage is being changed to "Drawing Approval"
        if 'stage_id' in vals and vals['stage_id'] == self.env['project.task.type'].search([('name', '=', 'Drawing Approval')]).id:
            # Add the follower to the task
            res = self.env['mail.followers'].create({'res_id': self.id, 'res_model': 'project.task', 'partner_id': self.partner_id.id})
        else:
            res = self.env['mail.followers'].search([('res_id', '=', self.id),('res_model', '=', 'project.task'),('partner_id', '=', self.partner_id.id)])
            for x in res:
                x.unlink()
        return super(ProjectTask, self).write(vals)

    def approve_task(self):
        for task in self:
            if task.stage_id.name == 'Drawing Preparation':
                task.stage_id = self.env.ref('project.task_stage_in_progress')