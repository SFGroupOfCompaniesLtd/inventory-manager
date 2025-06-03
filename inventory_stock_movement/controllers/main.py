from odoo import http
from odoo.http import request


class StockMovementController(http.Controller):
    @http.route('/inventory/stock_movement/data', type='json', auth='user')
    def get_movement_data(self):
        """Get data for stock movement dashboard"""
        movements = request.env['stock.movement'].search_read(
            [('state', 'in', ['draft', 'confirmed'])],
            ['name', 'date', 'movement_type', 'state', 'total_quantity', 'product_count'],
            limit=10
        )
        
        # Get movement counts by state
        movement_states = request.env['stock.movement'].read_group(
            domain=[],
            fields=['state'],
            groupby=['state']
        )
        
        # Get movement counts by type
        movement_types = request.env['stock.movement'].read_group(
            domain=[],
            fields=['movement_type'],
            groupby=['movement_type']
        )
        
        return {
            'recent_movements': movements,
            'movement_states': movement_states,
            'movement_types': movement_types,
        }