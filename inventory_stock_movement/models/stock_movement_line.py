from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockMovementLine(models.Model):
    _name = 'stock.movement.line'
    _description = 'Stock Movement Line'
    _order = 'id'

    movement_id = fields.Many2one(
        'stock.movement',
        string='Stock Movement',
        required=True,
        ondelete='cascade',
        index=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('type', 'in', ['product', 'consu'])],
        index=True
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial Number',
        domain="[('product_id', '=', product_id)]"
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        related='movement_id.source_location_id',
        store=True
    )
    destination_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        related='movement_id.destination_location_id',
        store=True
    )
    state = fields.Selection(
        related='movement_id.state',
        string='Status',
        store=True
    )
    company_id = fields.Many2one(
        related='movement_id.company_id',
        string='Company',
        store=True
    )
    date = fields.Datetime(
        related='movement_id.date',
        string='Movement Date',
        store=True
    )
    move_id = fields.Many2one(
        'stock.move',
        string='Stock Move',
        readonly=True,
        copy=False
    )
    product_tracking = fields.Selection(
        related='product_id.tracking',
        string='Product Tracking'
    )
    available_qty = fields.Float(
        string='Available Quantity',
        compute='_compute_available_qty'
    )
    description = fields.Char('Description')
    
    @api.depends('product_id', 'source_location_id')
    def _compute_available_qty(self):
        for line in self:
            if line.product_id and line.source_location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.source_location_id.id)
                ])
                line.available_qty = sum(quants.mapped('quantity'))
            else:
                line.available_qty = 0.0
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
    
    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity must be positive.'))
    
    @api.constrains('product_id', 'lot_id')
    def _check_lot(self):
        for line in self:
            if line.product_tracking in ['lot', 'serial'] and not line.lot_id:
                raise ValidationError(_('Lot/Serial number is required for tracked products.'))
            if line.product_tracking == 'serial' and line.quantity > 1:
                raise ValidationError(_('Quantity for serialized products must be 1.'))