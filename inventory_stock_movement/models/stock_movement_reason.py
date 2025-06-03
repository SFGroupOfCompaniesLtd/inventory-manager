from odoo import api, fields, models, _

class StockMovementReason(models.Model):
    _name = 'stock.movement.reason'
    _description = 'Stock Movement Reason'
    _order = 'name'

    name = fields.Char('Reason', required=True)
    code = fields.Char('Code')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    movement_type = fields.Selection([
        ('internal', 'Internal Transfer'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('adjustment', 'Inventory Adjustment')
    ], string='Applicable Movement Type')
    
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'The reason name must be unique per company!')
    ]