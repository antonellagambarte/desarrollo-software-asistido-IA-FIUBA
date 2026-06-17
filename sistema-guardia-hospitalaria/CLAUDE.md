# Sistema de gestión de guardia hospitalaria

## Descripción

Aplicación web para gestionar el flujo básico de pacientes en una guardia hospitalaria.

El sistema permite registrar pacientes, registrar ingresos a guardia, asignar prioridad manual, asignar médicos y consultar el estado actual de los pacientes en guardia.

## Stack

- Frontend: Nuxt 3 (Vue 3) + Vuetify + Pinia
- Backend: FastAPI
- ORM: SQLAlchemy
- Base de datos: SQLite

## Comunicación frontend - backend

El frontend se comunica con el backend mediante una API REST utilizando JSON.

## Alcance funcional

Este es el alcance mínimo del proyecto. Podría extenderse si se lo pide explícitamente.

El sistema incluye:

- Registro y búsqueda de pacientes.
- Registro de ingresos a guardia.
- Clasificación manual por prioridad: baja, media y alta.
- Gestión de estados del paciente: en espera, en atención y alta.
- Asignación manual de médicos.
- Visualización de pacientes activos en guardia.
- Dos vistas principales: recepción y médico.

## Fuera de alcance

No implementar:

- Notificaciones en tiempo real.
- Clasificación automática de prioridad.

## Estructura del proyecto

```txt
backend/
frontend/
.claude/
CLAUDE.md
```

## Ejecución del proyecto

Proyecto pensado para ejecución local solamente.

## Comandos útiles

### Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm run dev
```
