import string
from odoo import models, fields, api, _

class CarVehicleCost(models.Model):
    _name = 'car.vehicle.cost'
    _description = 'Cost related to a vehicle'

    vehicle_id = fields.Many2one('car.vehicle', 'Vehicle', required=True)
    cost_type_id = fields.Many2one('car.service.type', string='Type')
    date = fields.Date()
    amount = fields.Float('Total Price')
    description = fields.Text(string='Cost Description')
    # For get Currency
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

class CarVehicleFuelLog(models.Model):
    _name = 'car.vehicle.fuel.log'
    _description = 'Fuel log for vehicle'

    vehicle_id = fields.Many2one('car.vehicle', 'Vehicle Details', required=True)
    odometer = fields.Float(related='vehicle_id.odometer')
    # Refueling Detail
    liter = fields.Float()
    price_per_liter = fields.Float()
    amount = fields.Float()
    # Additional Information
    date = fields.Date(default=fields.Date.context_today)
    purchaser_id = fields.Many2one('res.users', string='Purchaser')

    @api.onchange('liter', 'price_per_liter', 'amount')
    def _onchange_fule_price(self):
        # Set float becouse the value maybe integer from web client
        liter = float(self.liter)
        price = float(self.price_per_liter)
        self.amount = round(liter * price, 2)
    
    @api.model
    def create(self, values):
        res = super(CarVehicleFuelLog, self).create(values)
        res.create_cost_history('Refueling')
        return res

    def create_cost_history(self, cost_type_id):
        refueling = self.env['car.service.type'].search([('name', '=', cost_type_id)])
        for record in self:
            self.env['car.vehicle.cost'].create({
                'vehicle_id': record.vehicle_id.id,
                'cost_type_id': refueling.id,
                'date': fields.Date.today(),
                'amount': record.amount
            })

class CarVehicleServiceLog(models.Model):
    _name = 'car.vehicle.service.log'
    _description = 'Sevice log for vehicle'

    vehicle_id = fields.Many2one('car.vehicle', 'Vehicle', required=True)
    cost_type_id = fields.Many2one('car.service.type', string='Type')
    amount = fields.Float(string='Total Price')
    odometer = fields.Float(related='vehicle_id.odometer')
    # Additional Information
    date = fields.Date()
    purchaser_id = fields.Many2one('res.users', string='Purchaser')

    @api.model
    def create(self, values):
        res = super(CarVehicleServiceLog, self).create(values)
        res.create_cost_history(values['vehicle_id'], values['cost_type_id'], values['amount'])
        return res

    def create_cost_history(self, vehicle_id, cost_type_id, amount):
        for record in self:
            self.env['car.vehicle.cost'].create({
                'vehicle_id': vehicle_id,
                'cost_type_id': cost_type_id,
                'date': fields.Date.today(),
                'amount': amount
            })

class CarVehicleReportCost(models.TransientModel):
    _name = 'car.vehicle.report.wizard'
    _description = 'For create cost report'

    vehicle_id = fields.Many2one('car.vehicle', string='Vehicle')
    start_period = fields.Date()
    end_period = fields.Date()

    def action_print_report(self):
        vals = []
        cost_report = self.env['car.vehicle.cost'].search([('vehicle_id', '=', self.vehicle_id.id),
                                                            ('date', '>=', self.start_period), 
                                                            ('date', '<=', self.end_period)])
        for cost in cost_report:
            vals.append({
                'cost_type_id': cost.cost_type_id.name,
                'date': cost.date.strftime("%d/%m/%Y"),
                'amount': cost.amount,
                'currency': cost.currency_id.symbol,
            })
        
        data = {
            'ids': self.ids,
            'model': self._name,
            'vals': vals,
            'start_period': self.start_period.strftime("%d/%m/%Y"),
            'end_period': self.end_period.strftime("%d/%m/%Y"),
            'vehicle_id': self.vehicle_id.model_id.name,
        }

        return self.env.ref('car_app.car_vehicle_report_cost_print_action').report_action(self, data=data)
    