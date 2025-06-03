from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    movement_count = fields.Integer(
        string='Movement Count',
        compute='_compute_movement_count'
    )
    
    def _compute_movement_count(self):
        for product in self:
            product.movement_count = self.env['stock.movement.line'].search_count([
                ('product_id', '=', product.id)
            ])
    
    def action_view_stock_movements(self):
        self.ensure_one()
        action = {
            'name': 'Stock Movements',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.movement',
            'view_mode': 'tree,form',
            'domain': [('movement_line_ids.product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
        }
        return action


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    movement_count = fields.Integer(
        string='Movement Count',
        compute='_compute_movement_count'
    )
    
    def _compute_movement_count(self):
        for template in self:
            template.movement_count = self.env['stock.movement.line'].search_count([
                ('product_id.product_tmpl_id', '=', template.id)
            ])
    
    def action_view_stock_movements(self):
        self.ensure_one()
        action = {
            'name': 'Stock Movements',
            'type': 'ir.actions.act_window',
            'res_model': 'stock.movement',
            'view_mode': 'tree,form',
            'domain': [('movement_line_ids.product_id.product_tmpl_id', '=', self.id)],
        }
        return action