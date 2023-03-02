# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OTRequest(models.Model):
    _name = 'ot.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ot Request'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env.user.employee_ids)
    project_id = fields.Many2one('project.project', string='Project')
    manager_id = fields.Many2one('hr.employee', string='Manager', compute='_compute_manager_id')
    dl_manager_id = fields.Many2one('hr.employee', string='DL Manager')
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'), ('pm_approved', 'PM Approved'),
                              ('dl_approved', 'DL Approved'), ('refused', 'Refused')], default='draft')
    create_date = fields.Datetime(string='Create Date', default=fields.Datetime.now)
    ot_request_lines = fields.One2many('ot.request.line', 'ot_request_id', string='ot Request Lines')

    @api.depends('ot_request_lines.ot_hours')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(record.ot_request_lines.mapped('ot_hours'))

    @api.depends('employee_id')
    def _compute_manager_id(self):
        for request in self:
            department_id = request.employee_id.department_id
            manager = self.env['hr.employee'].search(
                [('department_id', '=', department_id.id), ('job_id.name', '=', 'Manager')], limit=1)
            request.manager_id = manager.id if manager else False


class OTRequestLine(models.Model):
    _name = 'ot.request.line'
    _description = 'ot Request Line'

    ot_request_id = fields.Many2one('ot.request', string='ot Request', ondelete='cascade')
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    ot_category = fields.Selection([('saturday', 'Saturday'), ('sunday', 'Sunday'), ('normal_day', 'Normal Day'), ('unknown', 'Unknown')], string='ot Category', compute='_compute_ot_category', store=True)
    wfh = fields.Boolean(string='WFH')
    job_taken = fields.Char(string='Job Taken')
    ot_hours = fields.Float(string='ot Hours', compute='_compute_ot_hours', store=True)
    state = fields.Selection([('draft', 'Draft'), ('pm_approved', 'PM Approved'), ('dl_approved', 'DL Approved'), ('refused', 'Refused')], default='draft')
    late_approved = fields.Boolean(string='Late Approved')
    notes = fields.Text(string='Notes')

    @api.depends('from_time', 'to_time')
    def _compute_ot_category(self):
        for record in self:
            if not record.from_time or not record.to_time:
                record.ot_category = 'unknown'
            elif record.from_time.weekday() == 5:
                record.ot_category = 'saturday'
            elif record.from_time.weekday() == 6:
                record.ot_category = 'sunday'
            elif record.from_time.weekday() < 5 and record.from_time.hour >= 18 and record.from_time.minute >= 30:
                record.ot_category = 'normal_day'
            else:
                record.ot_category = 'unknown'

    @api.depends('from_time', 'to_time')
    def _compute_ot_hours(self):
        for record in self:
            if not record.from_time or not record.to_time:
                record.ot_hours = 0.0
            else:
                delta = record.to_time - record.from_time
                record.ot_hours = delta.total_seconds() / 3600

