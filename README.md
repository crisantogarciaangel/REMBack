# KYC Onboarding – Backend

## Descripción

Backend del mini-módulo de onboarding.  
Esta API permite registrar, consultar y evaluar solicitudes de verificación de identidad, aplicando reglas básicas de riesgo y manteniendo auditoría de eventos.

---

## Tecnologías utilizadas

- Python 3.8+ (Docker utiliza Python 3.11)
- FastAPI
- SQLAlchemy
- PostgreSQL (base de datos principal)
- MongoDB (auditoría y logs)
- Pydantic v2
- Pytest
- Docker y Docker Compose (opcional)

---

## Estructura del proyecto

```
.
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   ├── core/
│   └── main.py
├── scripts/
│   └── seed.py
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Configuración de entorno

Crear un archivo `.env` en la raíz del proyecto (no versionado), usando como referencia `.env.example`.

### Variables requeridas

```
POSTGRES_DSN=postgresql://kyc_user:kyc_password@localhost:5432/kyc_db
MONGO_URI=mongodb://localhost:27017
LOG_LEVEL=INFO
```

---

## Ejecución sin Docker (local)

### Instalar dependencias

```
python -m pip install -r requirements.txt
```

### Crear base de datos

En PostgreSQL, crear el usuario y la base de datos:

```
CREATE USER kyc_user WITH PASSWORD 'kyc_password';
CREATE DATABASE kyc_db OWNER kyc_user;
```

### Crear tablas

La creación automática de tablas al arranque fue removida intencionalmente para evitar bloqueos.  
Ejecutar una sola vez:

```
python -c "from app.infrastructure.postgres.init_db import init_db; init_db()"
```

### Levantar la API

```
uvicorn app.main:app --reload --port 8000
```

Endpoints útiles:
- Health: http://localhost:8000/health
- Swagger: http://localhost:8000/docs

---

## Ejecución con Docker (opcional)

Este repositorio incluye Docker únicamente para el backend y las bases de datos (PostgreSQL y MongoDB), ya que el frontend vive en otro repositorio.

### Levantar servicios

```
docker compose up --build
```

Servicios disponibles:
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- MongoDB: localhost:27017

### Crear tablas en Docker

```
docker compose exec backend python -c "from app.infrastructure.postgres.init_db import init_db; init_db()"
```

---

## Pruebas automatizadas

El proyecto incluye **2 pruebas unitarias de backend** que validan:
- El motor de reglas de riesgo.
- El servicio principal de creación de solicitudes.

Las pruebas no dependen de bases de datos reales.

### Ejecutar pruebas

```
python -m pytest -q
```

Resultado esperado:

```
..
2 passed in X.XXs
```

---

## Datos de ejemplo (Seeder)

Se incluye un script idempotente para cargar datos dummy:
- Inserta solicitudes de verificación en PostgreSQL.
- Inserta eventos de auditoría en MongoDB.
- MongoDB es *best-effort*: si no está disponible, el script no falla.

### Ejecutar seed en local

```
python -m scripts.seed
```

### Ejecutar seed en Docker

```
docker compose exec backend python scripts/seed.py
```

---

## Decisiones técnicas

- PostgreSQL se usa como fuente de verdad para las solicitudes.
- MongoDB se utiliza únicamente para auditoría y logs de eventos.
- Arquitectura en capas: API, Application, Domain e Infrastructure.
- Validaciones de entrada con Pydantic.
- Logs estructurados sin exponer información sensible.
- Pruebas desacopladas de infraestructura.

---

## Limitaciones conocidas

- MongoDB no es obligatorio para el flujo principal.
- No se implementa autenticación/autorización.
- No se implementa logica para recibir archivos de imagen

---

