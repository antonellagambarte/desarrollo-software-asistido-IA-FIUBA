# Frontend

## Tecnologías

- Nuxt 3 (Vue 3)
- Vue 3
- Vuetify
- Pinia

## Estructura

Sigue estructura provista por Nuxt 3:

pages/
components/
services/
stores/
layouts/

## Objetivo

Proporcionar una interfaz simple para gestionar el flujo básico de pacientes en una guardia hospitalaria.

## Navegación y rutas

- Utilizar el sistema de rutas de Nuxt.
- Las páginas deben ubicarse en `pages/`.
- Los componentes reutilizables deben ubicarse en `components/`.
- Mantener una estructura de rutas simple y consistente.

El sistema cuenta con dos páginas principales:

- /recepcion
- /medico

No implementar autenticación basada en roles.

La separación entre recepción y médico se realiza mediante páginas independientes.

## Páginas principales

Las funcionalidades disponibles podrían extenderse. Las que se presentan a continuación son las mínimas.

### /recepcion

Funcionalidades disponibles:

- Registrar pacientes.
- Buscar pacientes por DNI.
- Registrar ingresos a guardia.
- Asignar prioridad manual.
- Consultar pacientes activos.
- Consultar el estado de los pacientes.

### /medico

Funcionalidades disponibles:

- Ver pacientes en espera.
- Ver pacientes en atención.
- Tomar pacientes para atención.
- Registrar observaciones.
- Dar altas a pacientes.
