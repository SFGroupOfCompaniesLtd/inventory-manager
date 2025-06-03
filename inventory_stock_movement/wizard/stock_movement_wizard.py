from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockMovementWizard(models.TransientModel):
    _name = 'stock.movement.wizard'
    _description = 'Create Stock Movement Wizard'

    movement_type = fields.Selection([
        ('internal', 'Internal Transfer'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('adjustment', 'Inventory Adjustment')
    ], string='Movement Type', required=True, default='internal')
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
        domain=[('usage', 'in', ('internal', 'supplier', 'customer', 'inventory', 'production'))]
    )
    destination_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        domain=[('usage', 'in', ('internal', 'supplier', 'customer', 'inventory', 'production'))]
    )
    scheduled_date = fields.Datetime(
        'Scheduled Date',
        default=fields.Datetime.now,
    )
    reason_id = fields.Many2one(
        'stock.movement.reason',
        string='Reason'
    )
    line_ids = fields.One2many(
        'stock.movement.wizard.line',
        'wizard_id',
        string='Products'
    )
    notes = fields.Text('Notes')
    
    @api.onchange('movement_type')
    def _onchange_movement_type(self):
        if self.movement_type == 'incoming':
            supplier_location = self.env.ref('stock.stock_location_suppliers', raise_if_not_found=False)
            if supplier_location:
                self.source_location_id = supplier_location.id
            stock_location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
            if stock_location:
                self.destination_location_id = stock_location.id
        elif self.movement_type == 'outgoing':
            stock_location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
            if stock_location:
                self.source_location_id = stock_location.id
            customer_location = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
            if customer_location:
                self.destination_location_id = customer_location.id
    
    def action_create_movement(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_('You need to add at least one product to create a movement.'))
        
        if self.source_location_id == self.destination_location_id:
            raise UserError(_('Source and destination locations cannot be the same.'))
        
        vals = {
            'movement_type': self.movement_type,
            'source_location_id': self.source_location_id.id,
            'destination_location_id': self.destination_location_id.id,
            'scheduled_date': self.scheduled_date,
            'reason_id': self.reason_id.id if self.reason_id else False,
            'notes': self.notes,
            'movement_line_ids': [],
        }
        
        for line in self.line_ids:
            vals['movement_line_ids'].append((0, 0, {
                'product_id': line.product_id.id,
                'quantity': line.quantity,
                'product_uom_id': line.product_uom_id.id,
                'lot_id': line.lot_id.id if line.lot_id else False,
                'description': line.description,
            }))
        
        movement = self.env['stock.movement'].create(vals)
        
        action = {
            'name': _('Stock Movement'),
            'view_mode': 'form',
            'res_model': 'stock.movement',
            'res_id': movement.id,
            'type': 'ir.actions.act_window',
        }
        return action


class StockMovementWizardLine(models.TransientModel):
    _name = 'stock.movement.wizard.line'
    _description = 'Stock Movement Wizard Line'

    wizard_id = fields.Many2one(
        'stock.movement.wizard',
        string='Wizard',
        required=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain=[('type', 'in', ['product', 'consu'])]
    )
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True
    )
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial Number',
        domain="[('product_id', '=', product_id)]"
    )
    description = fields.Char('Description')
    product_tracking = fields.Selection(related='product_id.tracking')
    available_qty = fields.Float(
        string='Available Quantity',
        compute='_compute_available_qty'
    )
    
    @api.depends('product_id', 'wizard_id.source_location_id')
    def _compute_available_qty(self):
        for line in self:
            if line.product_id and line.wizard_id.source_location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', line.product_id.id),
                    ('location_id', '=', line.wizard_id.source_location_id.id)
                ])
                line.available_qty = sum(quants.mapped('quantity'))
            else:
                line.available_qty = 0.0
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id