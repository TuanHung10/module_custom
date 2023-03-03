# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class SuperPet(models.Model):
    _name = "super.pet"  # <- new model name
    _inherit = "my.pet"  # <- inherit fields and methods from model "my.pet"
    _description = "Prototype inheritance"

    # add new field
    is_super_strength = fields.Boolean("Is Super Strength", default=False)
    is_fly = fields.Boolean("Is Super Strength", default=False)
    planet = fields.Char("Planet")

    # avoid error: TypeError: Many2many fields super.pet.product_ids and my.pet.product_ids use the same table and columns
    product_ids = fields.Many2many(comodel_name='product.product',
                                   string="Related Products",
                                   relation='super_pet_product_rel',  # <- change this relation name!
                                   column1='col_pet_id',
                                   column2='col_product_id')