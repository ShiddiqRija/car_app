# -*- coding: utf-8 -*-
# from odoo import http


# class CarApp(http.Controller):
#     @http.route('/car_app/car_app/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/car_app/car_app/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('car_app.listing', {
#             'root': '/car_app/car_app',
#             'objects': http.request.env['car_app.car_app'].search([]),
#         })

#     @http.route('/car_app/car_app/objects/<model("car_app.car_app"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('car_app.object', {
#             'object': obj
#         })
