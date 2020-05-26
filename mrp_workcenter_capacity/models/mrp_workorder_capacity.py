# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    wo_capacity = fields.Float(string='WC Weekly Capacity (Hours)', related='workcenter_id.wc_capacity', store='True', group_operator="avg")
    duration_expected_hours = fields.Float(string='Expected Duration (Hours)', compute='expected_duration_hours', store='True')

    @api.multi
    @api.depends('duration_expected')
    def expected_duration_hours(self):
        duration_expected_hours = 0.0
        workorder = self
        for wo in workorder:
            wo.duration_expected_hours = (wo.duration_expected) / 60
        return True