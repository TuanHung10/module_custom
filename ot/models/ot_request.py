# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
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
    ot_month = fields.Char(string='OT Month', store=True)
    ot_request_lines = fields.One2many('ot.request.line', 'ot_request_id', string='OT Request Lines')

    @api.depends('ot_request_lines.ot_hours')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = sum(record.ot_request_lines.mapped('ot_hours'))

    # @api.depends('ot_request_lines.from_time')
    # def _compute_month(self):
    #     for rec in self:
    #         month = ''
    #         if rec.ot_request_lines:
    #             from_time = fields.Datetime.from_string(rec.ot_request_lines[0].from_time)
    #             month = from_time.strftime('%B %Y')
    #         rec.ot_month = month


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
            rec.send_pm_notification()
            rec.send_employee_notification()

    def button_dl_approve(self):
        for rec in self:
            rec.state = 'dl_approved'
            rec.send_dl_notification()
            rec.send_employee_notification()

    def refuse_request(self):
        for rec in self:
            rec.state = 'refused'

    @api.multi
    def send_pm_notification(self):
        # pm = self.env['hr.employee'].search([('is_pm', '=', True)])
        # if pm:
        #     mail_template = self.env.ref('ot.mail_template_pm_notification')
        #     mail_template.write({'email_to': pm.work_email})
        #     mail_template.send_mail(self.id, force_send=True)
        print('send pm')

    @api.multi
    def send_dl_notification(self):
        # pm = self.env['hr.employee'].search([('is_pm', '=', True)])
        # if pm:
        #     mail_template = self.env.ref('ot.mail_template_pm_notification')
        #     mail_template.write({'email_to': pm.work_email})
        #     mail_template.send_mail(self.id, force_send=True)
        print('send dl')

    @api.multi
    def send_employee_notification(self):
        # mail_template = self.env.ref('your_module.mail_template_employee_notification')
        # mail_template.write({'email_to': self.employee_id.work_email})
        # mail_template.send_mail(self.id, force_send=True)
        print('send employee')


class OTRequestLine(models.Model):
    _name = 'ot.request.line'
    _description = 'OT Request Line'

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


    #Viet ham late approved se duoc auto tick khi: ban ghi duoc approve vao thoi diem month now != from_time month
    #Thang state o ca 2 class phai khop voi nhau tren record
    #Xu li thang OT month
    #Phan quyen, button hien thi
    #Xu li OT category
    #Phai send duoc mail nhu tren youtube odoomate sau khi an vao 1 action


