# -*- coding: utf-8 -*-
{
    'name': "Car App",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Simple Car App
    """,

    'author': "Shiddiq",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'views/car_vehicle_views.xml',
        'views/car_vehicle_service_views.xml',
        'views/car_vehicle_cost_views.xml',
        'views/car_vehicle_model_views.xml',
        'views/car_vehicle_report_views.xml',
        'reports/cost_report_template.xml',
        'views/car_menu_item.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
}
