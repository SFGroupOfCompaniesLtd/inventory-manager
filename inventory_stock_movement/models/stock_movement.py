from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class StockMovement(models.Model):
    _name = 'stock.movement'
    _description = 'Stock Movement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    date = fields.Datetime(
        string='Movement Date',
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    user_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True, copy=False)
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        required=True,
        domain=[('usage', 'in', ('internal', 'supplier', 'customer', 'inventory', 'production'))],
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    destination_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=True,
        domain=[('usage', 'in', ('internal', 'supplier', 'customer', 'inventory', 'production'))],
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    movement_line_ids = fields.One2many(
        'stock.movement.line',
        'movement_id',
        string='Movement Lines',
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    movement_type = fields.Selection([
        ('internal', 'Internal Transfer'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('adjustment', 'Inventory Adjustment')
    ], string='Movement Type', required=True, default='internal',
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]})
    reason_id = fields.Many2one(
        'stock.movement.reason',
        string='Reason',
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]}
    )
    notes = fields.Text('Notes', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]})
    scheduled_date = fields.Datetime(
        'Scheduled Date',
        states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]},
        default=fields.Datetime.now,
        index=True,
        tracking=True
    )
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
    ], default='0', string='Priority', states={'done': [('readonly', True)], 'cancelled': [('readonly', True)]})
    product_count = fields.Integer(compute='_compute_product_count', string='Product Count')
    total_quantity = fields.Float(compute='_compute_total_quantity', string='Total Quantity')
    picking_id = fields.Many2one('stock.picking', string='Related Picking', copy=False, readonly=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('stock.movement') or _('New')
        return super(StockMovement, self).create(vals_list)
    
    def _compute_product_count(self):
        for movement in self:
            movement.product_count = len(movement.movement_line_ids.mapped('product_id'))
    
    def _compute_total_quantity(self):
        for movement in self:
            movement.total_quantity = sum(movement.movement_line_ids.mapped('quantity'))
    
    def action_confirm(self):
        for movement in self:
            if not movement.movement_line_ids:
                raise UserError(_('You cannot confirm a stock movement without movement lines.'))
            movement.write({'state': 'confirmed'})
        return True
    
    def action_done(self):
        for movement in self:
            if not movement.movement_line_ids:
                raise UserError(_('You cannot validate a stock movement without movement lines.'))
            
            # Create stock moves and process them
            picking_type = self.env['stock.picking.type'].search([
                ('code', '=', 'internal'),
                ('warehouse_id.company_id', '=', movement.company_id.id)
            ], limit=1)
            
            if not picking_type:
                raise UserError(_('No internal operation type found for this company.'))
            
            picking_vals = {
                'location_id': movement.source_location_id.id,
                'location_dest_id': movement.destination_location_id.id,
                'picking_type_id': picking_type.id,
                'origin': movement.name,
                'user_id': movement.user_id.id,
                'company_id': movement.company_id.id,
                'scheduled_date': movement.scheduled_date,
                'move_type': 'direct',
            }
            
            picking = self.env['stock.picking'].create(picking_vals)
            
            for line in movement.movement_line_ids:
                move_vals = {
                    'name': line.product_id.name,
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity,
                    'product_uom': line.product_uom_id.id,
                    'picking_id': picking.id,
                    'location_id': movement.source_location_id.id,
                    'location_dest_id': movement.destination_location_id.id,
                    'company_id': movement.company_id.id,
                }
                self.env['stock.move'].create(move_vals)
            
            # Process the picking
            picking.action_confirm()
            picking.action_assign()
            
            # Create inventory adjustments if needed
            if all(move.state == 'assigned' for move in picking.move_ids):
                for move_line in picking.move_line_ids:
                    move_line.qty_done = move_line.reserved_uom_qty
                picking.button_validate()
                movement.write({
                    'state': 'done',
                    'picking_id': picking.id
                })
            else:
                raise UserError(_('Not all products are available for this movement.'))
        
        return True
    
    def action_cancel(self):
        for movement in self:
            if movement.state == 'done':
                if movement.picking_id and movement.picking_id.state == 'done':
                    raise UserError(_('Cannot cancel a movement related to a validated picking.'))
                elif movement.picking_id:
                    movement.picking_id.action_cancel()
            movement.write({'state': 'cancelled'})
        return True
    
    def action_draft(self):
        for movement in self:
            if movement.state == 'cancelled':
                movement.write({'state': 'draft'})
        return True
    
    @api.constrains('source_location_id', 'destination_location_id')
    def _check_locations(self):
        for movement in self:
            if movement.source_location_id == movement.destination_location_id:
                raise ValidationError(_('Source and destination locations cannot be the same.'))
    
    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            return
        
        action = {
            'name': _('Transfer'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'res_id': self.picking_id.id,
        }
        return action