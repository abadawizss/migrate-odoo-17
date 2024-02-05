# -*- coding: utf-8 -*-
# import auditlog.registry
from odoo import models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _create_project_and_tasks(self):
        # Define the stages for the project
        stages = [{'name': 'Order Received', 'sequence': 1},
                  {'name': 'Order Review', 'sequence': 2},
                  {'name': 'New Project', 'sequence': 7},
                  {'name': 'Procurement', 'sequence': 2},
                  {'name': 'Fabrication', 'sequence': 3},
                  {'name': 'Done', 'sequence': 4},
                  {'name': 'Canceled', 'sequence': 5},
                  {'name': 'Power Coating', 'sequence': 6}]
        ProjectStage = self.env['project.project.stage']
        for stage_vals in stages:
            stage = ProjectStage.search([('name', '=', stage_vals['name'])])
            if stage:
                stage.name = stage_vals['name']
                # stage.write({'project_ids': [(4, project.id)]})
            else:
                # stage_vals.update({'project_ids': [(4, project.id)]})
                stage.create(stage_vals)
        # Create the project for the sale order
        project_name = "Project for Sale Order %s" % (self.name)
        project = self.env['project.project'].create({
            'name': project_name,
            'partner_id': self.partner_id.id,
            'sale_order_id': self.id,
            'stage_id': self.env['project.project.stage'].search([('name', '=', 'Order Received')], limit=1).id,
        })

        # Define the stages for the project
        stages = [{'name': 'Order Received', 'sequence': 1},{'name': 'Order Review', 'sequence': 2},{'name': 'Drawing Preparation', 'sequence': 9}, {'name': 'Internal Drawing Review', 'sequence': 10},{'name': 'Drawing Submission', 'sequence': 3},{'name': 'Drawing Revision', 'sequence': 4},
                  {'name': 'Drawing Approval', 'sequence': 5},{'name': 'WIP', 'sequence': 6},{'name': 'Fabrication', 'sequence': 7},{'name': 'Powder Coating', 'sequence': 8}]
                  # {'name': 'Done', 'sequence': 3}, ]
        TaskType = self.env['project.task.type']
        sale_order = self.env['sale.order'].search([('name', '=', self.name)])
        # sale_order.write({'project_id': [(4, project.id)]})
        sale_order.project_id = project.id
        for stage_vals in stages:
            stage = TaskType.search([('name', '=', stage_vals['name'])])
            if stage:
                stage.sudo().write({'project_ids': [(4, project.id)]})
            else:
                # stage_vals.update({'project_ids': [(4, project.id)]})
                TaskType.sudo().create(stage_vals)

        # Create a task for each order line
        task_vals = []
        for i, line in enumerate(self.order_line, 1):
            # task_name = f"{self.name} - Task {i} - Line {line.sequence} - {line.product_id.name}"
            task_name = f"Task {i} - {self.name}"
            task_vals.append({
                'name': task_name,
                # 'name': line.product_id.name,
                'project_id': project.id,
                'description': line.name,
                'planned_hours': line.product_uom_qty,
                'stage_id': self.env['project.task.type'].search([('name', '=', 'Order Received')], limit=1).id,
            })
        self.env['project.task'].create(task_vals)

    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if 'state' in vals and vals['state'] == 'sale':
            for order in self:
                order._create_project_and_tasks()
        return result