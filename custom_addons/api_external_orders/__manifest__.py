{
    'name': 'API External Orders Integration',
    'version': '1.0',
    'summary': 'Integración API para recepción de órdenes de venta externas',
    'description': 'Módulo para recibir, validar y procesar órdenes externas dejando trazabilidad.',
    'author': 'Fábrica de Software',
    'category': 'Sales',
    'depends': ['base', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}