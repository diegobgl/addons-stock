# -*- coding: utf-8 -*-


from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = "mrp.production"

    # 已入库数量
    qty_done_total = fields.Float('Inventory Done', compute="_compute_total",
                                  digits=dp.get_precision('Product Unit of Measure'), readonly=True, store=True, copy=False)
    # 已生产数量
    qty_finished_total = fields.Float('Produce Done', compute="_compute_total",
                                  digits=dp.get_precision('Product Unit of Measure'), readonly=True, store=True, copy=False)

    @api.depends('finished_move_line_ids.qty_done', 'finished_move_line_ids.done_move')
    def _compute_total(self):
        for rec in self:
            # 此处用一次遍历减少计算量
            qty_done_total = 0
            qty_finished_total = 0
            for line in rec.finished_move_line_ids:
                if line.done_move:
                    qty_done_total += line.qty_done
                qty_finished_total += line.qty_done
            rec.qty_done_total = qty_done_total
            rec.qty_finished_total = qty_finished_total

