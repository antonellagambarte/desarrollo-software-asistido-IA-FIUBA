# API PARA GESTIÓN DE TURNOS MÉDICOS

## ¿Qué es?

Consiste en la especificación y diseño del contrato de una API REST utilizando el estándar OpenAPI para la gestión de turnos médicos.

---

## Autora

Proyecto realizado por Antonella Gambarte para la materia Desarrollo de Software asistido por IA.

## ¿Cómo funciona?

Permite:

Gestión de pacientes:

- Permite dar de alta nuevos pacientes enviando DNI, obra social, datos de contacto mediante un método POST.

- Permite consultar el listado completo de pacientes registrados a través de un GET, con una opción para limitar la cantidad de pacientes a devolver.

- Permite obtener un paciente en particular buscando por dni.

Gestión de turnos médicos:

- Permite la creación y asignación de turnos médicos a un paciente. Para ello es necesario fecha, hora, la especialidad correspondiente del turno y DNI del paciente.

- Permite listar los turnos programados para un paciente en particular.

- Permite cancelar turnos siempre y cuando sea un turno futuro.

---

## Qué funcionó

Con la indicación en un sólo prompt, se pudo crear correctamente la cantidad de especificaciones de endpoints con la estructura mayormente correcta.

## Qué no funcionó

Al no especificar bien en que casos se tenía que devolver error (se indicó solamente "404 para fracaso"), asumió casos de errores que no tenían sentido en la práctica común. Por ejemplo, al obtener los turnos asociados a un paciente, indicó que se debía tirar error si no había turnos asociados. Lo lógico es devolver un array vacío (que permite gestionar fácilmente desde front los mensajes o advertencias a mostrar). El no tener turnos asociados no es un error. En todo caso, se devuelve error si el paciente para el cual se quiere obtener sus turnos asociados no existe en el sistema.

---
