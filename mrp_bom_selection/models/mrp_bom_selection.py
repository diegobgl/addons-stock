# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import time
import datetime


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    

    @api.onchange('product_id', 'picking_type_id', 'company_id', 'product_qty', 'date_planned_start')
    def onchange_product_id(self):
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_selection(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id, product_qty=self.product_qty, date_planned_start=self.date_planned_start)
            if bom.type == 'normal':
                self.bom_id = bom.id
            else:
                self.bom_id = False
            self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    date_start = fields.Date(string='Validity Start Date', required=True, track_visibility='onchange', default=fields.Date.context_today)
    date_end = fields.Date(string='Validity End Date', required=True, track_visibility='onchange', default=time.strftime('%Y-12-31'))
    qty_min = fields.Float(string='Minimum Lot Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default="1.00")
    qty_max = fields.Float(string='Maximum Lot Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default="99999.00")


    @api.model
    def _bom_selection(self, product_tmpl=None, product=None, picking_type=None, company_id=False, product_qty=None, date_planned_start=None):
        """ Finds BoM for particular product, picking. company, quantity and date """
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = ['|', ('product_id', '=', product.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
        else:
            # neither product nor template, makes no sense to search
            return False
        if picking_type:
            #domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
            domain += [('picking_type_id', '=', picking_type.id)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + [('company_id', '=', company_id or self.env.context.get('company_id'))]
        domain = domain + [('qty_min', '<=', product_qty)] + [('qty_max', '>', product_qty)]
        domain = domain + [('date_start', '<=', date_planned_start)] + [('date_end', '>', date_planned_start)]
        # order to prioritize bom with product_id over the one without
        return self.search(domain, order='sequence, product_id', limit=1)





