# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class OTRequest(models.Model):
    _name = 'ot.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'ot Request'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env.user.employee_ids)
    project_id = fields.Many2one('project.project', string='Project')
    manager_id = fields.Many2one('hr.employee', string='Manager', compute='_compute_manager_id')
    dl_manager_id = fields.Many2one('hr.employee', string='DL Manager')
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'), ('pm_approved', 'PM Approved'),
                              ('dl_approved', 'DL Approved'), ('refused', 'Refused')], default='draft')
    create_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    ot_month = fields.Selection(
        [("1", "January"),
         ("2", "February"),
         ("3", "March"),
         ("4", "April"),
         ("5", "May"),
         ("6", "June"),
         ("7", "July"),
         ("8", "August"),
         ("9", "September"),
         ("10", "October"),
         ("11", "November"),
         ("12", "December")], string='OT Month')
    ot_request_lines = fields.One2many('ot.request.line', 'ot_request_id', string='OT Request Lines')

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

    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def button_pm_approve(self):
        for rec in self:
            rec.state = 'pm_approved'

    def button_dl_approve(self):
        for rec in self:
            rec.state = 'dl_approved'

    def refuse_request(self):
        for rec in self:
            rec.state = 'refused'


class OTRequestLine(models.Model):
    _name = 'ot.request.line'
    _description = 'ot Request Line'

    ot_request_id = fields.Many2one('ot.request', string='ot Request', ondelete='cascade')
    from_time = fields.Datetime(string='From Time')
    to_time = fields.Datetime(string='To Time')
    ot_category = fields.Selection(
        [('saturday', 'Saturday'), ('sunday', 'Sunday'), ('normal_day', 'Normal Day'),
         ('normal_day_morning', 'Normal Day Morning'), ('normal_day_night', 'Normal Day Night'),
         ('weekend_day_night', 'Weekend Day Night'), ('unknown', 'Unknown')],
        string='OT Category', compute='_compute_ot_category', store=True)
    wfh = fields.Boolean(string='WFH')
    job_taken = fields.Char(string='Job Taken')
    ot_hours = fields.Float(string='OT Hours', compute='_compute_ot_hours', store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('pm_approved', 'PM Approved'), ('dl_approved', 'DL Approved'), ('refused', 'Refused')],
        default='draft')
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
                if record.from_time.hour >= 22 or record.from_time.hour < 6:
                    record.ot_category = 'normal_day_night'
                elif 6 <= record.from_time.hour < 8 and record.from_time.minute < 30:
                    record.ot_category = 'normal_day_morning'
                else:
                    record.ot_category = 'normal_day'
            elif record.from_time.weekday() >= 5 and 6 <= record.from_time.hour < 8 and record.from_time.minute < 30:
                record.ot_category = 'weekend_day_night'
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


