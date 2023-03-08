# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OTRequest(models.Model):
    _name = 'ot.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'OT Request'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env.user.employee_ids)
    project_id = fields.Many2one('project.project', string='Project', required=True)
    manager_id = fields.Many2one('hr.employee', string='Manager', compute='_compute_manager_id')
    dl_manager_id = fields.Many2one('hr.employee', string='DL Manager', required=True)
    total_hours = fields.Float(string='Total Hours', compute='_compute_total_hours', store=True)
    state = fields.Selection([('draft', 'Draft'), ('to_approve', 'To Approve'), ('pm_approved', 'PM Approved'),
                              ('dl_approved', 'DL Approved'), ('refused', 'Refused')], default='draft')
    create_date = fields.Datetime(string='Created Date', default=fields.Datetime.now)
    ot_month = fields.Date(string='OT Month', store=True, readonly=True, compute='_compute_ot_month')
    ot_request_lines = fields.One2many('ot.request.line', 'ot_request_id', string='OT Request Lines')

    @api.depends('ot_request_lines.from_time')
    def _compute_ot_month(self):
        for rec in self:
            latest_from_time = max(rec.ot_request_lines.mapped('from_time'), default=False)
            if latest_from_time:
                rec.ot_month = latest_from_time.date()
            else:
                rec.ot_month = False

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

    def submit_request(self):
        for rec in self:
            rec.state = 'to_approve'
            rec.send_pm_notification()
            rec.send_employee_notification()

    def button_pm_approve(self):
        for rec in self:
            rec.state = 'pm_approved'
            rec.send_dl_notification()
            rec.send_employee_notification()

    def button_dl_approve(self):
        for rec in self:
            rec.state = 'dl_approved'
            rec.send_employee_notification()

    def refuse_request(self):
        for rec in self:
            rec.state = 'refused'
            rec.send_employee_notification()

    @api.multi
    def send_pm_notification(self):
        pm = self.env['hr.employee'].search([('job_id', '=', 9)])
        if pm:
            mail_template = self.env.ref('ot.mail_template_pm_notification')
            mail_template.write({'email_to': pm.work_email})
            mail_template.send_mail(self.id, force_send=True)

    @api.multi
    def send_dl_notification(self):
        dl = self.env['hr.employee'].search([('job_id', '=', 10)])
        if dl:
            mail_template = self.env.ref('ot.mail_template_pm_notification')
            mail_template.write({'email_to': dl.work_email})
            mail_template.send_mail(self.id, force_send=True)

    @api.multi
    def send_employee_notification(self):
        mail_template = self.env.ref('ot.mail_template_employee_notification')
        mail_template.write({'email_to': self.employee_id.work_email})
        mail_template.send_mail(self.id, force_send=True)


class OTRequestLine(models.Model):
    _name = 'ot.request.line'
    _description = 'OT Request Line'

    ot_request_id = fields.Many2one('ot.request', string='ot Request', ondelete='cascade')
    from_time = fields.Datetime(string='From Time', required=True)
    to_time = fields.Datetime(string='To Time', required=True)
    ot_category = fields.Selection(
        [('saturday', 'Saturday'), ('sunday', 'Sunday'), ('normal_day', 'Normal Day'),
         ('normal_day_morning', 'Normal Day Morning'), ('normal_day_night', 'Normal Day Night'),
         ('weekend_day_night', 'Weekend Day Night'), ('unknown', 'Unknown')],
        string='OT Category', compute='_compute_ot_category', store=True)
    wfh = fields.Boolean(string='WFH')
    job_taken = fields.Char(string='Job Taken')
    ot_hours = fields.Float(string='OT Hours', compute='_compute_ot_hours', store=True)
    state = fields.Selection(
        related='ot_request_id.state',
        string='State',
        readonly=True
    )
    late_approved = fields.Boolean(string='Late Approved')
    notes = fields.Text(string='Notes')

    @api.depends('ot_request.state')
    def _compute_state(self):
        for request in self:
            states = request.ot_request.mapped('state')
            if 'refused' in states:
                request.state = 'refused'
            elif 'to_approve' in states:
                request.state = 'to_approve'
            elif 'pm_approved' in states:
                request.state = 'pm_approved'
            elif 'dl_approved' in states:
                request.state = 'dl_approved'
            else:
                request.state = 'draft'

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

        # Xu li OT category

        # Phan quyen, button hien thi: PM, DL can not create,edit, delete request

        # @api.model tao 1 lan 1 record, @api.model_create_multi tao 1 lan nhieu records (moi lan goi ham)
        # record la object, model la class
        #sql_constraints = [
        # dau tien la id cua constraints ('code_company_uniq', thu 2 la rang buoc ,code voi company_id la truowng 'unique (code, company_id)'), thu 3 la thanh phan thong bao loi~ ('The code must be...')
        # ]


