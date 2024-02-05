# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
import json
# from odoo.addons.portal.controllers.portal import Task as PortalTask
#
#
# class Task(PortalTask):
#
#     @http.route(['/my_module/tasks'], type='http', auth="user", website=True)
#     def my_module_tasks(self, **kw):
#         domain = [('stage_id.name', '=', 'Drawing Approval')]
#         tasks = http.request.env['project.task'].sudo().search(domain)
#         return http.request.render('my_module.tasks', {'tasks': tasks})


class PortalController(http.Controller):

    @http.route('/update_task_stage', type='json', auth='user')
    def update_task_stage(self, **post):
        task_id = int(post.get('task_id'))
        stage_id = int(post.get('stage_id'))
        # Update the task stage using sudo method to bypass access rights
        task = http.request.env['project.task'].sudo().browse(task_id)
        task.stage_id = stage_id
        # Return a JSON response indicating success
        return json.dumps({'success': True})

    @http.route('/my/portal/page', type='http', auth="public", website=True)
    def my_portal_page(self, **kw):
        return request.render('my_module.my_portal_template', {})

    @http.route('/my/portal/menu', type='http', auth="public", website=True)
    def my_portal_menu(self, **kw):
        # Get all project tasks in the "Drawing Approval" stage
        tasks_list = http.request.env['project.task'].sudo().search([])
        # tasks = http.request.env['project.task'].search([('stage_id.name', '=', 'Drawing Approval')])

        # Prepare a list of dictionaries containing the relevant task information
        tasks = []
        for task in tasks_list:
            tasks.append({
                'id': task.id,
                'name': task.name,
                'description': task.description,
                'stage': task.stage_id.name,
                'attachments': task.attachment_ids,
            })
        # Render the template with the task dictionary
        return request.render('zen_sale_project.project_portal_task_list', {'tasks': tasks})