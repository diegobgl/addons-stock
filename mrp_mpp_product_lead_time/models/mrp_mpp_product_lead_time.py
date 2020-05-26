# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate (models.Model):
    _inherit = 'product.template'
    
    lead_time = fields.Integer(string='Total Replenishment Lead Time',
    help="The total replenishment lead time is the time needed before the product is completely available again, that is, after all BOM levels have been procured or produced. It is not calculated by the system, but defined in this field as the total of the in-house production time(s) and/or the planned delivery time(s) of the longest production path. For materials produced in-house, the replenishment lead time is to be taken into account in performing material availability checks in Master Production Plan Management. In an availability check where the system takes the replenishment lead time into consideration. The 'Total replenishment lead time' is defined at product's template level.")


class ProductProduct (models.Model):
    _inherit = 'product.product'
    
    lead_time = fields.Integer(string='Total Replenishment Lead Time', 
    readonly='1',
    related='product_tmpl_id.lead_time', 
    store='True',
    help="The total replenishment lead time is the time needed before the product is completely available again, that is, after all BOM levels have been procured or produced. It is not calculated by the system, but defined in this field as the total of the in-house production time(s) and/or the planned delivery time(s) of the longest production path. For materials produced in-house, the replenishment lead time is to be taken into account in performing material availability checks in Master Production Plan Management. In an availability check where the system takes the replenishment lead time into consideration. The 'Total replenishment lead time' is defined at product's template level.")