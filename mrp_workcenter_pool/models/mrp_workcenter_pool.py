# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError

class MrpWorkcenterPool(models.Model):
    """
    mrp.workcenter.pool
    Model that is a group of workcenters that on the particular
    production (BOM) can do the job on the production Route
    """
    _name = 'mrp.workcenter.pool'
    _description = 'Workcenter Pool'

    name = fields.Char('Workcenter Pool Name', required=True)
    active = fields.Boolean('Active', default=True, help="If the active field is set to False, it will allow you to hide the routing without removing it.")
    # code = fields.Char('Reference', copy=False, default=lambda self: _('New'), readonly=True)
    # note = fields.Text('Description')
    line_ids = fields.One2many('mrp.workcenter.pool.line', 'workcenter_pool_id', 'Workcenters',)

    def get_prior_workcenter_id(self, flag=None):
        """
        This method get and retrun the id of the workcenter with the minor value of integer
        that meaning the workcenter has the greater prority.
        """
        wc_id = 0
        line_id = 0
        prior = 0

        if flag == 'line':
            for line in self.line_ids:
                if line_id == 0:
                    if line.workcenter_id.active and line.workcenter_id.working_state != 'done':
                        line_id = line.id
                        prior = line.priority_order
                elif line.priority_order < prior:
                    if line.workcenter_id.active and line.workcenter_id.working_state != 'done':
                        line_id = line.id
                        prior = line.priority_order
                result = line_id
        else:
            for line in self.line_ids:
                if wc_id == 0:
                    if line.workcenter_id.active:
                        wc_id = line.workcenter_id.id
                        prior = line.priority_order
                elif line.priority_order < prior:
                    if line.workcenter_id.active:
                        wc_id = line.workcenter_id.id
                        prior = line.priority_order
                result = wc_id

        return result

class MrpWorkcenterPoolLine(models.Model):
    """
    mrp.workcenter.pool.line
    Model to represente a line into de mrp.workcenter.pool model and that have a workcenter reference.
    """
    _name = 'mrp.workcenter.pool.line'
    _description = 'Workcenter Pool Line'

    name = fields.Char('Workcenter Pool Line Name', compute='_compute_line_name')
    state = fields.Char('Workcenter State', compute='_compute_line_state')
    # active = fields.Boolean('Active', compute='_compute_line_active')
    # code = fields.Char('Reference', copy=False, default=lambda self: _('New'), readonly=True)
    # note = fields.Text('Description')
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True)
    workcenter_pool_id = fields.Many2one('mrp.workcenter.pool', 'Workcenter Pool Parent', index=True,)
    priority_order = fields.Integer(string='Priority Order')

    @api.multi
    def _compute_line_name(self):
        for line in self:
            state = ''
            if line.workcenter_id.working_state == 'done':
                state = ' (In use)'
            line.name = line.workcenter_id.name + state

    @api.multi
    def _compute_line_state(self):
        for line in self:
            if line.workcenter_id.active:
                state = 'Enable'
            else:
                state = 'Disable'
            line.state = state

    @api.model
    def create(self, values):
        """
        Overwrite the create method to put in the values dict the workcenter pool line name with the workcenter name
        """
        if values['priority_order'] < 1:
            raise UserError(_('You can not set the priority order value less than zero.'))

        return super(MrpWorkcenterPoolLine, self).create(values)

    @api.model
    def write(self, values):
        """
        Overwrite the create method to put in the values dict the workcenter pool line name with the workcenter name
        """
        if values['priority_order'] < 1:
            raise UserError(_('You can not set the priority order value less than zero.'))

        return super(MrpWorkcenterPoolLine, self).write(values)

    def disable_wc(self):
        """
        Show a pop-up to confirm or change de workcenter to use in the workorder.
        """
        if self.workcenter_id:
            if self.workcenter_id.active:
                self.workcenter_id.write({'active': False})

        return True

    def enable_wc(self):
        """
        Show a pop-up to confirm or change de workcenter to use in the workorder.
        """
        if self.workcenter_id:
            if not self.workcenter_id.active:
                self.workcenter_id.write({'active': True})

        return True

# class MrpWorkcenter(models.Model):
#     """
#     mrp.workcenter inherit
#     Inherited from model mrp.workcenter for some reasons.
#     """
#     _inherit = 'mrp.workcenter'
#
#     workcenter_pool_id = fields.Many2one('mrp.routing', 'Workcenter Pool Parent', index=True,)

class MrpRoutingWorkcenter(models.Model):
    """
    mrp.routing.workcenter inherit
    Inherited from model mrp.routing.workcenter and change the required of the workcenter_id field to False.

    Fields Modified:
        - workcenter_id: Used to reference a workcenter.
    Fields Added:
        - workcenter_pool_id: Used to reference a pool of workcenters.
    """
    _inherit = 'mrp.routing.workcenter'

    workcenter_id = fields.Many2one(required=False)
    workcenter_pool_id = fields.Many2one('mrp.workcenter.pool', 'Workcenter Pool', required=True)

    @api.model
    def create(self, values):
        """
        Overwrite the create method to put in the values dict the workcenter with the greater priority in the pool
        """
        workcenter_pool = self.env['mrp.workcenter.pool'].browse(values['workcenter_pool_id'])
        values['workcenter_id'] = workcenter_pool.get_prior_workcenter_id()

        return super(MrpRoutingWorkcenter, self).create(values)

    @api.multi
    def write(self, values):
        """
        Overwrite the write method to put in the values dict the workcenter with the greater priority in the pool if the
        workcenter pool have been changed his workcenters priority orders.
        """
        workcenter_pool = self.workcenter_pool_id
        values['workcenter_id'] = workcenter_pool.get_prior_workcenter_id()

        return super(MrpRoutingWorkcenter, self).write(values)

class MrpWorkorder(models.Model):
    """
    mrp.routing.workcenter inherit
    Inherited from model mrp.routing.workcenter and change the required of the workcenter_id field to False.

    Fields Modified:
        - workcenter_id: Used to reference a workcenter.
    Fields Added:
        - workcenter_pool_id: Used to reference a pool of workcenters.
    """
    _inherit = 'mrp.workorder'

    @api.multi
    def button_start(self):
        workorder_id = self.id
        workcenter_pool_id = self.operation_id.workcenter_pool_id.id
        workcenter_pool_line_id = self.operation_id.workcenter_pool_id.get_prior_workcenter_id(flag='line')
        workcenter_id = self.operation_id.workcenter_pool_id.get_prior_workcenter_id()


        new_wizard = self.env['mrp.change.confirm.wizard'].create({'workcenter_pool_id': workcenter_pool_id,
                                                                    'workorder_id': workorder_id,
                                                                    'workcenter_pool_line_id': workcenter_pool_line_id,
                                                                    'workcenter_id': workcenter_id})
        view_id = self.env.ref('mrp_workcenter_pool.view_change_confirm').id

        return {
            'type': 'ir.actions.act_window',
            'name': 'Confirm or Change workcenter',
            'view_mode': 'form',
            'res_model': 'mrp.change.confirm.wizard',
            'target': 'new',
            'res_id': new_wizard.id,
            'views': [[view_id, 'form']],
        }

    @api.multi
    def button_start_confirmed(self):
        # TDE CLEANME
        timeline = self.env['mrp.workcenter.productivity']
        if self.duration < self.duration_expected:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','productive')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one productivity loss in the category 'Productivity'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        else:
            loss_id = self.env['mrp.workcenter.productivity.loss'].search([('loss_type','=','performance')], limit=1)
            if not len(loss_id):
                raise UserError(_("You need to define at least one productivity loss in the category 'Performance'. Create one from the Manufacturing app, menu: Configuration / Productivity Losses."))
        for workorder in self:
            if workorder.production_id.state != 'progress':
                workorder.production_id.write({
                    'state': 'progress',
                    'date_start': datetime.now(),
                })
            timeline.create({
                'workorder_id': workorder.id,
                'workcenter_id': workorder.workcenter_id.id,
                'description': _('Time Tracking: ')+self.env.user.name,
                'loss_id': loss_id[0].id,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })
        return self.write({'state': 'progress',
                    'date_start': datetime.now(),
        })

        # return super(MrpWorkorder, self).button_start(self)
