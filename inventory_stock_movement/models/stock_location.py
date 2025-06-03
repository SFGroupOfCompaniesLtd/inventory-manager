from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = 'stock.location'
    
    movement_count = fields.Integer(
        string='Movement Count',
        compute='_compute_movement_count'
    )
    
    def _compute_movement_count(self):
        for location in self:
            location.movement_count = self.env['stock.movement'].search_count([
                '|', 
                ('source_location_id', '=', location.id),
                ('destination_location_id', '=', location.id)
            ])
    
    def action_view_stock_movements(self):
        self.ensure_one()
        action = {
            'name': 'Stock Movements',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.movement',
            'view_mode': 'tree,form',
            'domain': ['|', ('source_location_id', '=', self.id), ('destination_location_id', '=', self.id)],
            'context': {'default_source_location_id': self.id},
        }
        return action