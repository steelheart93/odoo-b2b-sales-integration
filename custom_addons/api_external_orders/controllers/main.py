import json
from odoo import http
from odoo.http import request

class ExternalOrderController(http.Controller):

    @http.route('/api/orders', type='json', auth='public', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        # En Odoo 16, el objeto "params" del JSON-RPC llega directo a kwargs
        payload = kwargs
        external_id = payload.get('external_id')

        if not external_id:
            return {'status': 'error', 'message': 'Falta el external_id en el payload'}

        LogModel = request.env['integration.order.log'].sudo()

        # 1. Validar duplicados exitosos previos
        existing_log = LogModel.search([('external_order_id', '=', external_id)], limit=1)
        if existing_log and existing_log.status == 'success':
            return {'status': 'error', 'message': 'La orden externa ya fue procesada exitosamente.'}

        try:
            # 2. Validar / Crear Cliente
            customer_data = payload.get('customer', {})
            vat = customer_data.get('vat')
            if not vat:
                raise ValueError('El documento del cliente (vat) es obligatorio.')

            Partner = request.env['res.partner'].sudo()
            partner = Partner.search([('vat', '=', vat)], limit=1)
            
            if not partner:
                partner = Partner.create({
                    'name': customer_data.get('name', 'Cliente Desconocido'),
                    'vat': vat,
                    'email': customer_data.get('email', ''),
                })

            # 3. Validar Productos y armar las líneas de la orden
            order_lines = []
            Product = request.env['product.product'].sudo()
            lines_data = payload.get('lines', [])
            
            if not lines_data:
                raise ValueError('La orden debe tener al menos una línea de producto.')

            for line in lines_data:
                sku = line.get('sku')
                qty = line.get('qty', 0)
                price = line.get('price', 0.0)

                if qty <= 0:
                    raise ValueError(f'Cantidad inválida para el producto {sku}')

                product = Product.search([('default_code', '=', sku)], limit=1)
                if not product:
                    raise ValueError(f'Producto con SKU {sku} no encontrado en Odoo.')

                order_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_uom_qty': qty,
                    'price_unit': price,
                }))

            # 4. Crear la Orden de Venta nativa
            SaleOrder = request.env['sale.order'].sudo()
            new_order = SaleOrder.create({
                'partner_id': partner.id,
                'order_line': order_lines,
            })

            # 5. Registrar Trazabilidad (Éxito)
            LogModel.create({
                'external_order_id': external_id,
                'status': 'success',
                'sale_order_id': new_order.id,
                'payload': json.dumps(payload)
            })

            return {
                'status': 'success',
                'message': 'Orden creada exitosamente',
                'sale_order_id': new_order.id,
                'sale_order_name': new_order.name
            }

        except Exception as e:
            # 6. Registrar Trazabilidad (Error)
            LogModel.create({
                'external_order_id': external_id,
                'status': 'error',
                'error_message': str(e),
                'payload': json.dumps(payload)
            })
            return {'status': 'error', 'message': str(e)}