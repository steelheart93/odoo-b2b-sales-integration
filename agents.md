# Odoo API Integration - AI Agent Documentation

Este archivo proporciona el contexto estructurado para que agentes de Inteligencia Artificial (LLMs) puedan analizar, mantener y extendir este repositorio de forma autónoma.

## System Architecture Context
- **Core Platform:** Odoo 16.0 Community Edition
- **Database:** PostgreSQL 15
- **Language:** Python 3.10+
- **Custom App Path:** `/custom_addons/api_external_orders/`

## Key Design Patterns Applied
1. **Idempotency & Traceability:** Implementado a través del modelo `integration.order.log`. Los agentes que realicen modificaciones deben asegurar que el controlador en `controllers/main.py` siga registrando intentos fallidos (`except` blocks) para mantener la observabilidad.
2. **KISS & Native Features:** Se evitó el uso de middlewares externos (FastAPI/Flask). La API REST está expuesta directamente usando `odoo.http.Controller`.
3. **JSON-RPC Wrapper:** Los agentes deben notar que los payloads externos están envueltos en la clave `"params"` nativa de la arquitectura web de Odoo 16+.