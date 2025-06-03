from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    group_stock_movement_lot = fields.Boolean(
        string="Track Lots or Serial Numbers",
        implied_group='inventory_stock_movement.group_stock_movement_lot'
    )
    group_stock_movement_multi_locations = fields.Boolean(
        string="Multi-Locations",
        implied_group='inventory_stock_movement.group_stock_movement_multi_locations'
    )
    module_stock_movement_batch = fields.Boolean(
        string="Batch Stock Movements"
    )
    auto_validate_zero_quantity = fields.Boolean(
        string="Auto Validate Zero Quantities",
        config_parameter='inventory_stock_movement.auto_validate_zero_quantity'
    )
    default_movement_type = fields.Selection([
        ('internal', 'Internal Transfer'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('adjustment', 'Inventory Adjustment')
    ], string='Default Movement Type', 
    config_parameter='inventory_stock_movement.default_movement_type',
    default='internal')