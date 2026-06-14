# Backend

## Tecnologías

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Estructura del backend

backend/
├── models/
├── schemas/
├── routers/
├── services/

## Entidades principales

- Paciente
- Médico
- IngresoGuardia

## Estados del ingreso

- EN_ESPERA
- EN_ATENCION
- ALTA

## Prioridades

- BAJA
- MEDIA
- ALTA

## Arquitectura

- El backend expone una API REST.
- La comunicación se realiza mediante JSON.
- Utilizar códigos HTTP apropiados para indicar éxito o error.
- Mantener organizada la estructura del backend respetando las carpetas definidas para modelos, schemas, routers y servicios.

## Reglas de negocio

- Al crear un ingreso, el estado inicial debe ser `EN_ESPERA`.
- Un ingreso solo puede pasar de `EN_ESPERA` a `EN_ATENCION`.
- Un ingreso solo puede pasar de `EN_ATENCION` a `ALTA`.
- Un ingreso con estado `ALTA` no debe modificarse.
- La prioridad siempre se carga manualmente.
