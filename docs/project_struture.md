backend/
│
├── api/                # FastAPI
│
├── config/
│
├── database/
│
├── models/             # SQLAlchemy
│
├── repositories/       # Acceso a datos
│
├── services/           # Reglas de negocio
│
├── handlers/           # Acciones de los intents
│
├── recognizers/        # Lógica fuzzy
│
├── llm/
│
├── scripts/
│
└── utils/



GRAN REGLA

Handler
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL