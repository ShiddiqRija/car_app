from odoo import models, fields, api, _

class CarVehicleModel(models.Model):
    _name = 'car.vehicle.model'
    _description = 'Model of a vehicle'

    name = fields.Char('Model Name', required=True)
    brand_id = fields.Many2one('car.vehicle.model.brand', 'Brand', required=True, help='Brand of the vehicle')
    handler_id = fields.Many2one('res.users', 'Car Handler', default=lambda self: self.env.uid)
    image_128 = fields.Image(related='brand_id.image_128')

class CarVehicleModelBrand(models.Model):
    _name = 'car.vehicle.model.brand'
    _description = 'Brand of the vehicle'

    name = fields.Char('Brand', required=True)
    image_128 = fields.Image('Logo', max_width=128, max_height=128)