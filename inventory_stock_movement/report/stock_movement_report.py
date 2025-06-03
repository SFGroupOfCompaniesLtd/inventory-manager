from odoo import api, fields, models, tools


class StockMovementReport(models.Model):
    _name = 'stock.movement.report'
    _description = 'Stock Movement Analysis Report'
    _auto = False
    _order = 'date desc'

    id = fields.Integer('ID', readonly=True)
    movement_id = fields.Many2one('stock.movement', 'Stock Movement', readonly=True)
    date = fields.Datetime('Movement Date', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled')
    ], string='Status', readonly=True)
    movement_type = fields.Selection([
        ('internal', 'Internal Transfer'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
        ('adjustment', 'Inventory Adjustment')
    ], string='Movement Type', readonly=True)
    source_location_id = fields.Many2one('stock.location', 'Source Location', readonly=True)
    destination_location_id = fields.Many2one('stock.location', 'Destination Location', readonly=True)
    reason_id = fields.Many2one('stock.movement.reason', 'Reason', readonly=True)
    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    product_categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    quantity = fields.Float('Quantity', readonly=True)
    lot_id = fields.Many2one('stock.lot', 'Lot/Serial Number', readonly=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', readonly=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
    ], string='Priority', readonly=True)
    month = fields.Char('Month', readonly=True)
    
    def _select(self):
        return """
            SELECT
                MIN(l.id) AS id,
                m.id AS movement_id,
                m.date,
                m.company_id,
                m.user_id,
                m.state,
                m.movement_type,
                m.source_location_id,
                m.destination_location_id,
                m.reason_id,
                l.product_id,
                p.product_tmpl_id,
                t.categ_id AS product_categ_id,
                l.quantity,
                l.lot_id,
                l.product_uom_id,
                m.priority,
                to_char(m.date, 'YYYY-MM') AS month
        """
    
    def _from(self):
        return """
            FROM stock_movement_line l
            LEFT JOIN stock_movement m ON (l.movement_id = m.id)
            LEFT JOIN product_product p ON (l.product_id = p.id)
            LEFT JOIN product_template t ON (p.product_tmpl_id = t.id)
        """
    
    def _group_by(self):
        return """
            GROUP BY
                m.id,
                m.date,
                m.company_id,
                m.user_id,
                m.state,
                m.movement_type,
                m.source_location_id,
                m.destination_location_id,
                m.reason_id,
                l.product_id,
                p.product_tmpl_id,
                t.categ_id,
                l.quantity,
                l.lot_id,
                l.product_uom_id,
                m.priority,
                to_char(m.date, 'YYYY-MM')
        """
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
            CREATE OR REPLACE VIEW %s AS (
                %s
                %s
                %s
            )
        """ % (self._table, self._select(), self._from(), self._group_by())
        self.env.cr.execute(query)