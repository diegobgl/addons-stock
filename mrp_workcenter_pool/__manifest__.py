# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Production Workcenter Pool',
    'website': 'http://www.brainiacpy.com',
    'author': 'brainiacPY',
    'version': '11.0.1.0.2',
    'support': 'brainiacpy@gmail.com',
    'license': 'AGPL-3',
    'images': ['images/main_screenshot.png'],
    'category': 'Manufacturing',
    'sequence': 14,
    'summary': 'Pool of Workcenters',
    'depends': ['mrp'],
    'description': "'This module provide the feature to create workcenter pools(a group of workcenters that on the particular production), The pools will asigned to an operation in the routing, then when a manufacture order is created an workorders are planing the workcenter with the lower priority order value in the assignated pool, is asigned to the workorder. Them when the workorder start the work the system request a confirmation of the assigned workcenter showed in the pop-up or can be changed manually from another available workcenter from the pool, the workcenter in progress or in use cant be selected manually. The workcenter showed in the confirmaiton pop-up is the workcenter with the lower priority order value and is in active state; if you deactive a workcenter of a pool the workcenter can't be assigned in the confirmation pop-up and can't be selected manually until active again the workcenter.'",
    'data': [
        'views/mrp_workcenter_pool_views.xml',
        'wizard/mrp_change_confirm_views.xml',
    ],
    'test': [],
    'application': True,
}
