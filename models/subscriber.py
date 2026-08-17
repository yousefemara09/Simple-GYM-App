from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Subscriber(models.Model):
    _name = 'subscriber'
    _description = 'Subscriber'

    ref = fields.Char(string='Reference', default='New', readonly=True)
    name = fields.Char(required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone Number')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    package_id = fields.Many2one('package', string='Package')
    price = fields.Float(string='Price', related='package_id.price')
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='active', compute='_compute_state', store=True)

    @api.onchange('start_date', 'package_id')
    def _onchange_start_date(self):
        for record in self:
            if record.start_date and record.package_id.durations:
                record.end_date = record.start_date + relativedelta(months=record.package_id.durations)
            else:
                record.end_date = False

    @api.depends('end_date')
    def _compute_state(self):
        for record in self:
            if record.end_date and record.end_date < fields.Datetime.now():
                record.state = 'expired'
            else:
                record.state = 'active'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'New') == 'New':
                vals['ref'] = self.env['ir.sequence'].next_by_code('sequence_subscriber')
        return super(Subscriber, self).create(vals_list)

    @api.constrains('start_date', 'end_date')
    def _check_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date > record.end_date:
                    raise ValidationError('Should Date Not Expired')

    def action_server_expire_subscriber(self):
        for record in self:
            if record.state == 'active':
                record.state = 'expired'

    def action_server_active_subscriber(self):
        for record in self:
            if record.state == 'expired':
                record.state = 'active'

    def button_call_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'renew.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_subscriber_id': self.id,
                'default_start_date': self.start_date,
                'default_end_date': self.end_date,
            }
        }
