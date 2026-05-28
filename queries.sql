-- 1. Consultar el estado de procesamiento de una orden externa específica
SELECT external_order_id, status, error_message, create_date 
FROM integration_order_log 
WHERE external_order_id = 'ORD-002';

-- 2. Trazabilidad: Tasa de éxito vs errores en la integración
SELECT status, COUNT(*) as total_procesamientos
FROM integration_order_log
GROUP BY status;

-- 3. Detalle integral: Cruzar el log de integración con las tablas nativas de Odoo (Ventas y Clientes)
SELECT 
    log.external_order_id, 
    log.status,
    so.name as odoo_sale_order, 
    rp.name as client_name, 
    so.amount_total
FROM integration_order_log log
JOIN sale_order so ON log.sale_order_id = so.id
JOIN res_partner rp ON so.partner_id = rp.id
WHERE log.status = 'success';