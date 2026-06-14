---
paths:
  - "frontend/**/*"
---

# Reglas para frontend

## Consumo de API

- Las páginas y componentes no deben realizar llamadas HTTP directamente.
- Las llamadas al backend deben centralizarse en archivos dentro de `services/`.
- Cada entidad puede tener su propio servicio. Ejemplos:
  - `pacienteService.js`
  - `medicoService.js`
  - `ingresoService.js`
- Si una página o componente necesita consumir datos, primero debe revisar si ya existe una función en `services/`.
- Si existe un endpoint en el backend pero no existe una función de servicio para consumirlo, agregar la función correspondiente en el servicio adecuado.
- Si no existe un endpoint necesario en el backend, consultar antes de crearlo.
- Los servicios deben exponer funciones reutilizables para consumir la API.
- Los servicios no deben contener lógica de presentación.

## Manejo de estado

- Utilizar Pinia únicamente para estado compartido entre páginas o componentes.
- Evitar almacenar en Pinia información que pueda mantenerse localmente.

## Creación de componentes

- Utilizar componentes de Vuetify siempre que sea posible.
- Antes de crear un componente en `components/`, verificar si existe una alternativa adecuada en Vuetify o un componente reutilizable ya implementado.

## Manejo de errores

- Mostrar mensajes de error y éxito mediante snackbars cuando corresponda.
