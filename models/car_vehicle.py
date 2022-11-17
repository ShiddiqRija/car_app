from odoo import models, fields, api, _

class CarVehicle(models.Model):
    _name = 'car.vehicle'
    _description = 'Vehicle'
    # _rec_name = 'model_id' + '/' + 'license_plate'

    # General Information
    name = fields.Char(string='Vehicle Name', compute='_compute_fields_name')
    model_id = fields.Many2one('car.vehicle.model', 'Model', required=True)
    image_128 = fields.Image(related='model_id.image_128')
    license_plate = fields.Char()
    # Vehicle Information
    odometer = fields.Float(string='Last Odometer', compute='_get_last_odometer', inverse='_create_odometer_history')
    odometer_unit = fields.Selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], default='kilometers')
    chassis_num = fields.Char(string='Chassis Number')
    net_car_value = fields.Float(string='Purchase Value')
    # Additional Information Model
    seats = fields.Integer(string='Seats Number')
    doors = fields.Integer(string='Doors Number')
    color = fields.Char()
    model_year = fields.Char()
    # Engine Information
    transmission = fields.Selection([('automatic', 'Automatic'), ('manual', 'Manual')])
    fuel_type = fields.Selection([('gasonline', 'Gasoline'), ('diesel', 'Diesel'), ('electric', 'Electric')])
    # User / Driver Information
    driver_id = fields.Many2one('res.users')
    future_driver_id = fields.Many2one('res.users')
    # Stats Information
    driver_history_count = fields.Integer(string='Driver History Count', compute='_count_driver')
    cost_log_count = fields.Integer(string='Cost Log Count', compute='_count_cost')
    odometer_history_count = fields.Integer(string='Odometer History Count', compute='_count_odometer')
    fuel_log_count = fields.Integer(string='Fuel Log Count', compute='_count_fuel')
    service_log_count = fields.Integer(string='Service Log Count', compute='_count_service')

    @api.depends('model_id', 'license_plate')
    def _compute_fields_name(self):
        for record in self:
            record.name = record.model_id.name + ' (' + record.license_plate + ')'

    def _count_driver(self):
        for record in self:
            record.driver_history_count = self.env['car.vehicle.assignation.log'].search_count([('vehicle_id', '=', record.id)])
    
    def _count_cost(self):
        for record in self:
            record.cost_log_count = self.env['car.vehicle.cost'].search_count([('vehicle_id', '=', record.id)])

    def _count_service(self):
        for record in self:
            record.service_log_count = self.env['car.vehicle.service.log'].search_count([('vehicle_id', '=', record.id)])

    def _count_fuel(self):
        for record in self:
            record.fuel_log_count = self.env['car.vehicle.fuel.log'].search_count([('vehicle_id', '=', record.id)])

    def _count_odometer(self):
        for record in self:
            record.odometer_history_count = self.env['car.vehicle.odometer'].search_count([('vehicle_id', '=', record.id)])
    
    def _get_last_odometer(self):
        for record in self:
            last_odometer = self.env['car.vehicle.odometer'].search([('vehicle_id', '=', record.id)], limit=1, order='value desc')
            if last_odometer:
                record.odometer = last_odometer.value
            else:
                record.odometer = 0

    def _create_odometer_history(self):
        for record in self:
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date, 'vehicle_id': record.id}
                self.env['car.vehicle.odometer'].create(data)

    @api.model
    def create(self, values):
        res = super(CarVehicle, self).create(values)
        if 'driver_id' in values:
            res.create_driver_history(values['driver_id'])
        return res
    
    def create_driver_history(self, driver_id):
        for vehicle in self:
            self.env['car.vehicle.assignation.log'].create({
                'vehicle_id': vehicle.id,
                'driver_id': driver_id,
                'start': fields.Date.today(),
            })
    
    def close_date_last_driver(self):
        self.env['car.vehicle.assignation.log'].search([
            ('vehicle_id', '=', self.id),
            ('end', '=', False)
        ]).write({'end': fields.Date.today()})
    
    def action_change_driver(self):
        self.write({'driver_id': False})
        self.close_date_last_driver()

        for vehicle in self:
            vehicle.driver_id = vehicle.future_driver_id
            vehicle.future_driver_id = False
        
        self.create_driver_history(self.driver_id.id)
    
    def open_assignation_log(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignation Logs',
            'view_mode': 'tree',
            'res_model': 'car.vehicle.assignation.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }
    
    def open_odometer_log(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Odometer History',
            'view_mode': 'tree',
            'res_model': 'car.vehicle.odometer',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_driver_id': self.driver_id.id, 'default_vehicle_id': self.id}
        }
    
    def open_service_log(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Service History',
            'view_mode': 'tree,form',
            'res_model': 'car.vehicle.service.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_purchaser_id': self.driver_id.id, 'default_vehicle_id': self.id}
        }
    
    def open_fuel_log(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Fuel History',
            'view_mode': 'tree,form',
            'res_model': 'car.vehicle.fuel.log',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_purchaser_id': self.driver_id.id, 'default_vehicle_id': self.id}
        }
    
    def open_cost_log(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cost History',
            'view_mode': 'tree',
            'res_model': 'car.vehicle.cost',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {'default_vehicle_id': self.id}
        }

class CarVehicleOdometer(models.Model):
    _name = 'car.vehicle.odometer'
    _desription = 'Odometer log for a vehicle'

    vehicle_id = fields.Many2one('car.vehicle', 'Vehicle')
    driver_id = fields.Many2one(related='vehicle_id.driver_id')
    date = fields.Date(default=fields.Date.context_today)
    value = fields.Float(string='Odometer Value')
    unit = fields.Selection(related='vehicle_id.odometer_unit', string='Unit')

class CarServiceType(models.Model):
    _name = 'car.service.type'
    _description = 'Car Service Type'

    name = fields.Char(required=True)

class CarVehicleAssignationLog(models.Model):
    _name = 'car.vehicle.assignation.log'
    _description = 'Drivers history on a vehicle'

    vehicle_id = fields.Many2one('car.vehicle', string='Vehicle', required=True)
    driver_id = fields.Many2one('res.users', string='Driver', required=True)
    start = fields.Date(string='Start Date')
    end = fields.Date(string='End Date')