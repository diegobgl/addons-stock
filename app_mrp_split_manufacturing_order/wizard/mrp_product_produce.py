# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_round


class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    auto_post = fields.Boolean('Auto Post Inventory', default=True)
    auto_material = fields.Boolean('Auto Material Done', default=True)
    post_date = fields.Datetime(
        'Date', default=fields.Datetime.now,
        help="Move date: scheduled date until move is done, then date of actual move processing")

    @api.multi
    def do_produce(self):
        if self.auto_material:
            # todo: get qty
            pass
        super(MrpProductProduce, self).do_produce()

        if self.auto_post:
            self.production_id.post_inventory()


    # todo: 用继承优化
    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])
            serial_finished = (production.product_id.tracking == 'serial')
            if serial_finished:
                todo_quantity = 1.0
            else:
                main_product_moves = production.move_finished_ids.filtered(
                    lambda x: x.product_id.id == production.product_id.id)
                todo_quantity = production.product_qty - sum(main_product_moves.mapped('quantity_done'))
                todo_quantity = todo_quantity if (todo_quantity > 0) else 0
            if 'production_id' in fields:
                res['production_id'] = production.id
            if 'product_id' in fields:
                res['product_id'] = production.product_id.id
            if 'product_uom_id' in fields:
                res['product_uom_id'] = production.product_uom_id.id
            if 'serial' in fields:
                res['serial'] = bool(serial_finished)
            if 'product_qty' in fields:
                res['product_qty'] = todo_quantity
            if 'produce_line_ids' in fields:
                lines = []
                for move in production.move_raw_ids.filtered(
                        lambda x: (x.product_id.tracking != 'none') and x.state not in (
                        'done', 'cancel') and x.bom_line_id):
                    qty_to_consume = todo_quantity / move.bom_line_id.bom_id.product_qty * move.bom_line_id.product_qty
                    for move_line in move.move_line_ids:
                        if float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) <= 0:
                            break
                        if move_line.lot_produced_id or float_compare(move_line.product_uom_qty, move_line.qty_done,
                                                                      precision_rounding=move.product_uom.rounding) <= 0:
                            continue
                        to_consume_in_line = min(qty_to_consume, move_line.product_uom_qty)
                        lines.append({
                            'move_id': move.id,
                            'qty_to_consume': to_consume_in_line,
                            'qty_done': to_consume_in_line,
                            'lot_id': move_line.lot_id.id,
                            'product_uom_id': move.product_uom.id,
                            'product_id': move.product_id.id,
                        })
                        qty_to_consume -= to_consume_in_line
                    if float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                        if move.product_id.tracking == 'serial':
                            while float_compare(qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding) > 0:
                                lines.append({
                                    'move_id': move.id,
                                    'qty_to_consume': 1,
                                    'qty_done': 1,
                                    'product_uom_id': move.product_uom.id,
                                    'product_id': move.product_id.id,
                                })
                                qty_to_consume -= 1
                        else:
                            lines.append({
                                'move_id': move.id,
                                'qty_to_consume': qty_to_consume,
                                'qty_done': qty_to_consume,
                                'product_uom_id': move.product_uom.id,
                                'product_id': move.product_id.id,
                            })

                res['produce_line_ids'] = [(0, 0, x) for x in lines]
        return res
