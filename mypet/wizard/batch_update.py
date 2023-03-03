# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class BatchUpdateWizard(models.TransientModel):
    _name = "my.pet.batchupdate.wizard"
    _description = "Batch update for my.pet model"

    #fields copy from my.pet model
    #Khi lam nghiep vu, co the tao them cac field khac tuy y, khong can giong vi du nay
    dob = fields.Date('DOB', required=False, default=False)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female')
    ], string='Gender', default=False)
    owner_id = fields.Many2one('res.partner', string='Owner', default=False)
    basic_price = fields.Float('Basic Price', default=0)

    def multi_update(self):
        ids = self.env.context['active_ids']  # selected record ids
        my_pets = self.env["my.pet"].browse(ids)
        new_data = {}

        if self.dob:
            new_data["dob"] = self.dob
        if self.gender:
            new_data["gender"] = self.gender
        if self.owner_id:
            new_data["owner_id"] = self.owner_id
        if self.basic_price > 0:
            new_data["basic_price"] = self.basic_price

        my_pets.write(new_data)


    #IDs các record được chọn trong bảng my.pet sẽ được truyền vào context -> truy xuất ra bằng cách ids = self.env.context['active_ids'].
    #Ta chỉ overwrite giá trị khi field điền lên form khác False (mặc định) -> logic Minh quy định trong ví dụ này là vậy