{
    'name': 'Inventory Stock Movement',
    'version': '1.0',
    'category': 'Inventory/Inventory',
    'summary': 'Track and manage inventory stock movements',
    'description': """
Inventory Stock Movement
========================
This module enhances Odoo's inventory management capabilities by providing detailed tracking and analysis of stock movements:

* Track product movements between locations
* Analyze stock movement history with detailed filters
* Generate movement reports with exportable data
* Manage batch movements for efficient processing
* Integrate with existing inventory workflows
* Control access with multi-level permissions
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['stock', 'product', 'base'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'views/stock_movement_views.xml',
        'views/stock_movement_line_views.xml',
        'views/stock_movement_reason_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'wizard/stock_movement_wizard_views.xml',
        'report/stock_movement_report_views.xml',
        'report/stock_movement_report_templates.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'inventory_stock_movement/static/src/js/**/*',
            'inventory_stock_movement/static/src/scss/**/*',
            'inventory_stock_movement/static/src/xml/**/*',
        ],
    },
}