
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class InheritMrpProductProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    @api.multi
    def get_per_unit_qty(self,bom_id,product_id):
        self.env.cr.execute("""select product_qty from mrp_bom_line where bom_id =%s and product_id=%s """%(bom_id,product_id))
        res = self.env.cr.dictfetchall()[0]
        if res['product_qty'] == None:
            return 0.0
        return res['product_qty']

    @api.multi
    def do_produce(self):
        for raw_material in self.production_id.move_raw_ids:
            if self.product_qty > self.production_id.product_qty:
                raise ValidationError("You cannot produce more quantity of finished product than quantity selected on MO")
            if raw_material.quantity_available < raw_material.product_uom_qty and self.product_qty*self.get_per_unit_qty(self.production_id.bom_id.id, raw_material.product_id.id) > raw_material.quantity_available:
                raise ValidationError("You cannot produce more quantity of finished product than quantity available of raw materials in stock")
        res = super(InheritMrpProductProduce, self).do_produce()
        return res
