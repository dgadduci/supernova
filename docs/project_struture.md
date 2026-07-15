backend/
│
├── main.py                     # Punto de entrada de la aplicación
│
├── config/
│   ├── config.py
│   └── settings.py
│
│── recognizers/
│   ├── logica_fuzzy_pedido_productos.py
│   ├── logica_fuzzy_pedido_metodo_de_entrega.py
│   ├── logica_fuzzy_pedido_medios_de_pago.py
│
├── llm/
│   ├── intent_classifier.py    # Texto libre -> JSON de intents
|   |__ query_llm               # clase base para enviar consultas a llm
│   ├── beauty_response.py      # JSON respuesta -> mensaje natural
│   └── prompts/
│       ├── intent_classifier.md
│       └── beauty_response.md
│
├── interpreter/
│   └── intent_interpreter.py   # Ejecuta las intents en orden
│
├── intents/
│   ├── intent_agregar_producto.py
│   ├── intent_quitar_producto.py
│   ├── intent_modificar_producto.py
│   ├── intent_consultar_producto.py
│   ├── intent_consultar_estado_pedido.py
│   ├── intent_confirmar_pedido.py
│   ├── intent_cancelar_pedido.py
│   ├── intent_set_metodo_pago.py
│   ├── intent_set_metodo_entrega.py
│   ├── intent_set_direccion_entrega.py
│   ├── intent_set_fecha_hora_entrega.py
│   ├── intent_set_observacion_producto.py
│   ├── intent_set_observacion_pedido.py
│   ├── intent_consultar_resumen_pedido.py
│   ├── intent_saludo.py
│   ├── intent_agradecimiento.py
│   ├── intent_despedida.py
│   ├── intent_respuesta_afirmativa.py
│   ├── intent_respuesta_negativa.py
│   ├── intent_ver_menu.py
│   ├── intent_ver_metodos_pago.py
│   ├── intent_ver_metodos_entrega.py
│   ├── intent_consultar_domicilio.py
│   ├── intent_consultar_horarios.py
│   ├── intent_iniciar_pedido.py
│   └── intent_desconocida.py
│
├── services/
│   ├── pedido_service.py
│   ├── producto_service.py
│   ├── cliente_service.py
│   └── comercio_service.py
│
├── validators/
│   ├── pedido_validator.py
│   ├── producto_validator.py
│   └── pago_validator.py
│
├── repositories/
│   ├── pedido_repository.py
│   ├── producto_repository.py
│   ├── cliente_repository.py
│   ├── comercio_repository.py
│   ├── medio_pago_repository.py
│   └── metodo_entrega_repository.py
│
├── models/
│   ├── pedido.py
│   ├── producto.py
│   ├── cliente.py
│   ├── comercio.py
│   ├── medio_pago.py
│   ├── metodo_entrega.py
│   └── conversation_context.py
│
├── database/
│   ├── connection.py
│   ├── migrations/
│   └── schema.sql
│
├── responses/
│   ├── response_builder.py      # Construye el JSON de respuesta
│   ├── response_models.py
│   └── templates.py             # Fallback sin LLM
│
├── integrations/
│   ├── whatsapp_terminal.py
│   └── twilio.py
│
├── utils/
│   ├── logger.py
│   ├── constants.py
│   └── helpers.py
│
└── tests/
    ├── intents/
    ├── services/
    ├── repositories/
    └── llm/