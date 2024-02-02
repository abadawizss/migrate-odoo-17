import calendar
from datetime import datetime, date, time
from dateutil import relativedelta
from odoo import models,fields,api, _

class DeliveryForecastPDF(models.AbstractModel):
    _name = 'report.zen_delivery_forecast.delivery_forecast_pdf'
    _description = 'Delivery Forecast Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form'):
            return {'error': _("Form content is missing, this report cannot be printed.")}
        result = []
        number = 1
        start = data['form']['start_date']
        end = data['form']['end_date']
        start_date = fields.Date.from_string(data['form']['start_date'])
        end_date = fields.Date.from_string(data['form']['end_date'])

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        execution_plan = self.env['zen.sale.execution'].search([('date_schedule','>=', start_datetime), ('date_schedule','<=', end_datetime)], order="date_schedule desc")
        for execution in execution_plan:
            quantity_scheduled = 0
            if execution.status == 'scheduled':
                quantity_scheduled = execution.qty
            aggregated_quantity = execution.qty
            # Total Delayed Count
            if quantity_scheduled > 0:
                total_delayed_count = max(quantity_scheduled - aggregated_quantity, 0)
            else:
                total_delayed_count = 1

            total_on_track_count = min(quantity_scheduled, aggregated_quantity)

            result.append({
                'no': number,
                'product_name': execution.product_id.name or '',
                'aggregated_quantity': aggregated_quantity or 0,
                'dealer_name': execution.order_id.partner_id.name or '',
                'date_schedule': execution.date_schedule or '',
                'qty_schedule': quantity_scheduled or 0,
                'total_delayed': total_delayed_count or 0,
                'total_ontrack': total_on_track_count or 0,
            })
            number += 1
        periode = str(start) + ' ' + str(end)
        report_delivery_forecast = result
        return {
            'vals': report_delivery_forecast,
            'periode': periode
        }

class DeliveryForecastPDFView(models.Model):
    _name = 'report.zen_delivery_forecast.delivery.forecast.view'
    _description = 'Report Delivery Forecast View'

    product_name = fields.Many2one('product.product', string='Products')
    aggregated_quantity = fields.Float('Aggregated Quantity')
    dealer_name = fields.Many2one('res.partner', string='Dealer Name')
    date_schedule = fields.Date('Date Scheduled')
    qty_schedule = fields.Float('Qty Scheduled')
    total_delayed = fields.Float('Total Delayed Count')
    total_ontrack = fields.Float('Total On-Track Count')


    def _get_report_values_views(self, data=None):
        query = "DELETE FROM report_zen_delivery_forecast_delivery_forecast_view"
        self.env.cr.execute(query)
        start_date = fields.Date.from_string(data['start_date'])
        end_date = fields.Date.from_string(data['end_date'])

        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        execution_plan = self.env['zen.sale.execution'].search([('date_schedule','>=', start_datetime), ('date_schedule','<=', end_datetime)], order="date_schedule desc")
        for execution in execution_plan:
            quantity_scheduled = 0
            if execution.status == 'scheduled':
                quantity_scheduled = execution.qty
            aggregated_quantity = execution.qty
            # Total Delayed Count
            if quantity_scheduled > 0:
                total_delayed_count = max(quantity_scheduled - aggregated_quantity, 0)
            else:
                total_delayed_count = 1

            total_on_track_count = min(quantity_scheduled, aggregated_quantity)
            report_model = self.env['report.zen_delivery_forecast.delivery.forecast.view']
            report_model.create({
                'product_name': execution.product_id.id or '',
                'aggregated_quantity': aggregated_quantity or 0,
                'dealer_name': execution.order_id.partner_id.id or '',
                'date_schedule': execution.date_schedule or '',
                'qty_schedule': quantity_scheduled or 0,
                'total_delayed': total_delayed_count or 0,
                'total_ontrack': total_on_track_count or 0,
            })
           
        # periode = 'Delivery Forecast Report' + ' ' + str(start) + ' ' + str(end)
        # tree_id = self.env['ir.model.data'].check_object_reference('zen_delivery_forecast', 'delivery_report_view_tree')
        # print(tree_id)
        # tree_view_id = tree_id and tree_id[1] or False,
        # action = {
        #     'type': 'ir.actions.act_window',
        #     'name': periode,
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'report.zen_delivery_forecast.delivery.forecast.view',
        #     'view_mode': 'tree',
        #     'target': 'current',
        #     'view_ids': [(tree_view_id, 'tree')],
            
        #     }
        # return action
        # domain_loc = [('date_schedule','>=',str(start)),('date_schedule','<=',str(end))]
        action = self.env["ir.actions.actions"]._for_xml_id("zen_delivery_forecast.delivery_report_view_action")
        action['views'] = [
            (self.env.ref('zen_delivery_forecast.delivery_report_view_tree').id, 'tree'),
        ]
        action['context'] ={
            'search_default_group_by_dealer_name': True,
            'search_default_group_by_product_name': True,
        }
        # action['domain'] = domain_loc
        return action