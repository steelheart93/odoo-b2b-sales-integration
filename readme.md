# Odoo B2B External Orders Integration

Solución de arquitectura para la recepción, validación y trazabilidad de órdenes de venta provenientes de un sistema externo B2B hacia Odoo 16, implementando el patrón KISS y minimizando la infraestructura intermedia.

## 1. Instalación y Ejecución

Este proyecto utiliza Docker Compose para levantar el entorno completo (PostgreSQL + Odoo 16) con el módulo _custom_ ya montado en volumen.

1. Clonar el repositorio.
2. Ejecutar el entorno: `docker-compose up -d`
3. Ingresar a `http://localhost:8069` (Usuario/Pass: admin/admin)
4. Activar el Modo Desarrollador en Odoo.
5. Ir a Aplicaciones, "Actualizar lista de aplicaciones" y buscar e instalar: **API External Orders Integration**.

## 2. Diagrama Lógico y de Relación de Datos

El siguiente diagrama detalla el flujo de información, la persistencia y la trazabilidad:

```mermaid
sequenceDiagram
    participant B2B as Sistema Externo
    participant API as Odoo Controller (API REST)
    participant DB as PostgreSQL
    participant Odoo as Odoo ORM (Modelos)

    B2B->>API: POST /api/orders (JSON Payload)
    API->>DB: Consultar integration_order_log
    alt Orden ya fue procesada exitosamente
        DB-->>API: Retorna Log Exitoso
        API-->>B2B: 400 Bad Request (Orden duplicada)
    else Nueva Orden o Intento Fallido Previo
        API->>Odoo: Validar Cliente (res.partner)
        API->>Odoo: Validar Producto (product.product)
        alt Falla Validación (Ej. SKU no existe)
            API->>DB: INSERT en integration_order_log (status: 'error')
            API-->>B2B: 400 Bad Request (Mensaje de error)
        else Validación Exitosa
            Odoo->>DB: INSERT en sale_order (Crear Orden)
            API->>DB: INSERT en integration_order_log (status: 'success', sale_order_id)
            API-->>B2B: 200 OK (sale_order_name)
        end
    end
```

## 3. Documentación y Pruebas de la API

**Endpoint:** `POST /api/orders`
**Content-Type:** `application/json`

Se incluye en la raíz del repositorio el archivo `postman_collection.json` listo para ser importado y ejecutar las pruebas de integración (casos de éxito y manejo de errores por validación de SKU/Cliente).

**Request Payload de Ejemplo:**

```json
{
  "jsonrpc": "2.0",
  "params": {
    "external_id": "ORD-12345",
    "customer": {
      "name": "Cliente de Prueba API",
      "vat": "1053123456",
      "email": "cliente@prueba.com"
    },
    "lines": [{ "sku": "SKU-001", "qty": 5, "price": 120.5 }]
  }
}
```
