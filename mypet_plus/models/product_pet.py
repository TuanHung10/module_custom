# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ProductPet(models.Model):
    _name = "product.pet"
    _inherits = {'my.pet': 'my_pet_id'}
    _description = "Product Pet"

    my_pet_id = fields.Many2one(
        'my.pet', 'My Pet',
        auto_join=True, index=True, ondelete="cascade", required=True)

    pet_type = fields.Selection([
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('vip', 'VIP'),
        ('cute', 'Cute'),
    ], string='Pet Type', default='basic')

    pet_color = fields.Selection([
        ('white', 'White'),
        ('black', 'Black'),
        ('grey', 'Grey'),
        ('yellow', 'Yellow'),
    ], string='Pet Color', default='white')

    bonus_price = fields.Float("Bonus Price", default=0)

    final_price = fields.Float("Final Price", compute='_compute_final_price')

    def _compute_final_price(self):
        for record in self:
            record.final_price = record.basic_price + record.bonus_price