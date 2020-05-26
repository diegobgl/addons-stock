# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MrpChangeConfirm(models.TransientModel):
    _name = 'mrp.change.confirm.wizard'
    _description = 'Open Sales Details Report'

    workcenter_pool_id = fields.Many2one('mrp.workcenter.pool', 'Workcenter Pool', required=True)
    workcenter_pool_line_id = fields.Many2one('mrp.workcenter.pool.line', 'Work Center', required=True)
    workorder_id = fields.Many2one('mrp.workorder', 'Work Order', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True)

    # @api.model
    # def default_get(self, fields):
    #     import pdb; pdb.set_trace()
    #     res = super(MrpChangeConfirm, self).default_get(fields)
    #
    #
    #     return res
    @api.multi
    def write(self, values):
        """
        Overwrite the write method to put in the values dict the workcenter with the greater priority in the pool if the
        workcenter pool have been changed his workcenters priority orders.
        """
        if 'workcenter_pool_line_id' in values:
            workcenter_pool_line = self.env['mrp.workcenter.pool.line'].browse(values['workcenter_pool_line_id'])
        values['workcenter_id'] = workcenter_pool_line.workcenter_id.id

        return super(MrpChangeConfirm, self).write(values)

    def confirm_start_work(self):
        """
        Show a pop-up to confirm or change de workcenter to use in the workorder.
        """
        if self.workcenter_pool_line_id.workcenter_id.working_state in ['done', 'blocked']:
            raise UserError(_('The manual selected workcenter is currently in use, please select another one.'))
        self.workorder_id.write({'workcenter_id': self.workcenter_pool_line_id.workcenter_id.id})
        self.workorder_id.button_start_confirmed()

        return True
