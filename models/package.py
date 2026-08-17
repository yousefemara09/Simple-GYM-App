from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Package(models.Model):
    _name = 'package'
    _description = 'Package'

    name = fields.Char(required=True)
    price = fields.Float(required=True, string='Price', store=True)
    subscriber_ids = fields.One2many('subscriber', inverse_name='package_id', string='Subscribers')
    count_subscribers = fields.Integer(compute='_compute_count_subscribers')
    months = fields.Selection([
        ('monthly', 'Monthly'),
        ('3-months', '3-Months'),
        ('6-months', '6-Months'),
    ], required=True)

    durations = fields.Integer(string='Duration', compute='_compute_duration', store=True)

    @api.depends('months')
    def _compute_duration(self):
        for record in self:
            if record.months == 'monthly':
                record.durations = 1
            elif record.months == '3-months':
                record.durations = 3
            elif record.months == '6-months':
                record.durations = 6
            else:
                record.durations = 0

    def get_all_sub(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'subscriber',
            'view_mode': 'tree',
            'domain': [('package_id', '=', self.id)]
        }

    @api.depends('subscriber_ids')
    def _compute_count_subscribers(self):
        for record in self:
            record.count_subscribers = len(record.subscriber_ids)

    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if record.price <= 0:
                raise ValidationError('Price must be greater than 0')

    @api.constrains('durations')
    def _check_durations(self):
        for record in self:
            if record.durations <= 0:
                raise ValidationError('Durations must be greater than 0')
