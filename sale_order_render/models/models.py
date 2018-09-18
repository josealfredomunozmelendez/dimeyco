# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
	_inherit = 'sale.order'
	
	render_ids = fields.Many2many(comodel_name='ir.attachment', string = "Render images")