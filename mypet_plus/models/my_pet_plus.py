# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class MyPetPlus(models.Model):
    _name = "my.pet"
    _inherit = "my.pet"
    _description = "Extend mypet model"

    # add new field
    toy = fields.Char('Pet Toy', required=False)

    # modify old fields
    age = fields.Integer('Pet Age', default=2)  # change default age from 1 to 2
    gender = fields.Selection(selection_add=[('sterilization', 'Sterilization')])  # add one more selection