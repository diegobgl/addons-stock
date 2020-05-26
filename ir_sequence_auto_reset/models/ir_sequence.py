from odoo import api, fields, models
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    auto_reset = fields.Boolean("Auto reset", default=False)
    reset_period_type = fields.Selection([('day', 'Day(s)'),
                                          ('month', 'Month(s)'),
                                          ('year', 'Year(s)')], string="Reset period type", default='day')
    reset_period_num = fields.Integer("Reset period num", default=1)
    reset_cron_id = fields.Many2one('ir.cron', string="Reset cron job")
    next_reset_call = fields.Datetime("Next reset call", compute='get_next_reset_call', inverse='set_next_reset_call')

    @api.depends('reset_cron_id')
    def get_next_reset_call(self):
        for seq in self:
            if seq.reset_cron_id:
                seq.next_reset_call = seq.reset_cron_id.nextcall

    def set_next_reset_call(self):
        for seq in self:
            if seq.reset_cron_id:
                seq.reset_cron_id.nextcall = seq.next_reset_call

    @api.onchange('use_date_range')
    def onchange_use_date_range(self):
        if self.use_date_range and self.auto_reset:
            self.auto_reset = False

    @api.onchange('auto_reset')
    def onchange_auto_reset(self):
        if self.auto_reset and self.use_date_range:
            self.use_date_range = False

    @api.constrains('reset_period_num')
    def _check_reset_period_num(self):
        if self.auto_reset and self.reset_period_num <= 0:
            raise ValidationError("Reset period number must be greater than 0!")

    @api.model
    def create(self, vals):
        print(vals)
        seq = super(IrSequence, self).create(vals)
        if seq.auto_reset and seq.reset_period_type and seq.reset_period_num and vals.get('next_reset_call'):
            reset_cron_id = seq.create_reset_cron(vals.get('next_reset_call'))
            seq.write({'reset_cron_id': reset_cron_id})
        return seq

    @api.multi
    def write(self, vals):
        print(vals)
        result = super(IrSequence, self).write(vals)
        for seq in self:
            if not seq.reset_cron_id and vals.get('auto_reset'):
                reset_cron_id = seq.create_reset_cron(vals.get('next_reset_call'))
                seq.write({'reset_cron_id': reset_cron_id})
            elif seq.reset_cron_id:
                if vals.get('auto_reset') != None or vals.get('reset_period_type') or vals.get('reset_period_num') \
                        or vals.get('next_reset_call'):
                    seq.update_reset_cron(vals.get('next_reset_call'))
        return result

    def create_reset_cron(self, next_call):
        if self.reset_period_type == 'day':
            interval_type = 'days'
            interval_number = self.reset_period_num
        elif self.reset_period_type == 'month':
            interval_type = 'months'
            interval_number = self.reset_period_num
        elif self.reset_period_type == 'year':
            interval_type = 'months'
            interval_number = self.reset_period_num * 12
        else:
            return False
        code = """
record = model.browse(%s)
record.sudo().write({'number_next_actual': 1})
""" % self.id

        cron_data = {
            'name': "Reset cron for " + self.name,
            'priority': 10,
            'active': True,
            'model_id': self.env.ref('base.model_ir_sequence').id,
            'state': 'code',
            'code': code,
            'interval_number': interval_number,
            'interval_type': interval_type,
            'numbercall': -1,
            'doall': True,
            'nextcall': next_call,
        }
        return self.env['ir.cron'].sudo().create(cron_data).id

    def update_reset_cron(self, next_call):
        if self.reset_period_type == 'day':
            interval_type = 'days'
            interval_number = self.reset_period_num
        elif self.reset_period_type == 'month':
            interval_type = 'months'
            interval_number = self.reset_period_num
        elif self.reset_period_type == 'year':
            interval_type = 'months'
            interval_number = self.reset_period_num * 12
        else:
            return False

        return self.reset_cron_id.sudo().write({
            'active': self.auto_reset,
            'interval_number': interval_number,
            'interval_type': interval_type,
            'nextcall': next_call or self.next_reset_call,
        })
