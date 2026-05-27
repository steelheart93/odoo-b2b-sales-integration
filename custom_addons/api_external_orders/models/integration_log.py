from odoo import models, fields

class IntegrationOrderLog(models.Model):
    _name = 'integration.order.log'
    _description = 'Trazabilidad de Órdenes Externas'
    _order = 'create_date desc'

    external_order_id = fields.Char(string='ID Orden Externa', required=True, index=True)
    status = fields.Selection([
        ('success', 'Éxito'), 
        ('error', 'Error')
    ], string='Estado del Procesamiento', required=True)
    
    error_message = fields.Text(string='Mensaje de Error')
    
    # Relación con la orden de venta nativa de Odoo
    sale_order_id = fields.Many2one('sale.order', string='Orden de Venta Odoo', readonly=True)
    
    payload = fields.Text(string='Payload Recibido')

    # Restricción a nivel de base de datos para evitar duplicados estrictos
    _sql_constraints = [
        ('unique_external_order', 'unique(external_order_id)', 'Esta orden externa ya fue procesada o está en la base de datos.')
    ]