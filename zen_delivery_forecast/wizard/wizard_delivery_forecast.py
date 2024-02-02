
from odoo import fields, models, _
from odoo.tools.mail import is_html_empty


class DeliveryForecast(models.TransientModel):
    _name = 'wizard.delivery.forecast'
    _description = 'Get Disqualification Reason'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    report_type = fields.Selection([
        ('pdf', 'PDF'),
        ('onscreen', 'On Screen')
    ], string='Report Type')

    def show_report(self):
        if self.report_type == 'pdf':
            self.ensure_one()
            [data] = self.read()
            data = {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'ids': self.ids,
                'model': self._name,
                'form': data
            }
            return self.env.ref('zen_delivery_forecast.action_delivery_forecast_pdf').report_action(self, data=data)
        elif self.report_type == 'onscreen':
            data = {
                'start_date': self.start_date,
                'end_date': self.end_date
            }
            report = self.env['report.zen_delivery_forecast.delivery.forecast.view']._get_report_values_views(data)
            return report


    

    