# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class HelpdeskTicketConvertWizard(models.TransientModel):
    _name = 'helpdesk.ticket.convert.wizard'
    _description = 'Convert Helpdesk Tickets to Tasks'

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if 'project_id' in field_list and not result.get('project_id'):
            result['project_id'] = self._default_project_id() or self.env['project.project'].search([], limit=1).id
        return result

    def _default_project_id(self):
        # This method is meant to be overridden.
        return False

    project_id = fields.Many2one('project.project', string='Project')
    stage_id = fields.Many2one('project.task.type', string='Stage', domain="[('project_ids', 'in', project_id)]",
        compute='_compute_default_stage', readonly=False, store=True, required=True)

    @api.depends('project_id')
    def _compute_default_stage(self):
        self.stage_id = self.project_id.type_ids[0].id if self.project_id.type_ids else False

    def action_convert(self):
        tickets_to_convert = self._get_tickets_to_convert()
        subtype_id = self.env.ref('project.mt_task_new').id

        created_tasks = self.env['project.task'].with_context(mail_create_nolog=True).create(
            [self._get_task_values(ticket) for ticket in tickets_to_convert]
        )

        for ticket, task in zip(tickets_to_convert, created_tasks):
            ticket.active = False

            ticket.sudo().message_post(body=f"Ticket converted into task <a href='#' data-oe-model='project.task' data-oe-id='{task.id}'>{task.name}</a>")
            task_message = task.sudo().message_post(
                body=f"Task created from ticket <a href='#' data-oe-model='helpdesk.ticket' data-oe-id='{ticket.id}'>{ticket.name}</a>",
                is_internal=True,
            )
            task._notify_thread(task_message, {'subtype_id': subtype_id})

        if len(created_tasks) == 1:
            return {
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id': created_tasks[0].id,
                'views': [(self.env.ref('project.view_task_form2').id, 'form')],
                'type': 'ir.actions.act_window',
            }
        return {
            'name': _('Converted Tasks'),
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'views': [(self.env.ref('project.view_task_tree2').id, 'tree'), (self.env.ref('project.view_task_form2').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', created_tasks.ids)],
        }

    def _get_tickets_to_convert(self):
        to_convert_ids = self.env.context.get('to_convert', [])
        return self.env['helpdesk.ticket'].browse(to_convert_ids)

    def _get_task_values(self, ticket):
        return {
            'name': ticket.name,
            'description': ticket.description,
            'project_id': self.project_id.id,
            'stage_id': self.stage_id.id,
            'partner_id': ticket.partner_id.id,
        }
