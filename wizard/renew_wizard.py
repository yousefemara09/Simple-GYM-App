from odoo import api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class RenewWizard(models.TransientModel):
    _name = 'renew.wizard'
    _description = 'Renew Wizard'

    name = fields.Char(required=True)
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='active')
    months = fields.Integer(
        string='Additional Months',
        required=True
    )
    subscriber_id = fields.Many2one(
        'subscriber',
        string='Subscriber',
        required=True
    )

    @api.constrains('months')
    def _check_months(self):
        for wizard in self:
            if wizard.months <= 0:
                raise ValidationError('Additional Months must be greater than 0')

    def action_confirm(self):
        for wizard in self:
            start_date = wizard.start_date or fields.Datetime.now()
            end_date = start_date + relativedelta(months=wizard.months)

            wizard.subscriber_id.start_date = start_date
            wizard.subscriber_id.end_date = end_date
            wizard.subscriber_id.state = 'active'

            wizard.start_date = start_date
            wizard.end_date = end_date
