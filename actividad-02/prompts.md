# Prompts - API para gestión de turnos médicos

## 1. Especificación completa del openapi.yaml

```txt
necesito un openapi.yaml para una API que gestioná turnos médicos de pacientes. Te paso las especificaciones:

Los recursos son paciente y turno.

El paciente tiene: {idpaciente,nombre,apellido, dni, obra_social, fecha_nacimiento, telefono, email }
El turno tiene: {idturno, fecha, hora, especialidad(representa la especialidad para la cual pide turno)}

Los endpoints van a ser:

POST /pacientes :para crear un paciente. Devuelve 201 para caso de éxito, 400 para fracaso
GET /pacientes: para obtener los pacientes creados. Opcionalmente se puede mandar "limit" para limitar la cantidad de pacientes a devolver. Devuelve 200 para éxito, 404 para fracaso
GET /pacientes/{dni}: para obtener un paciente por dni. Devuelve 200 para caso de éxito, 404 para fracaso.
POST /pacientes/{dni}/turnos : para crearle un nuevo turno a un paciente. Devuelve 201 para caso de éxito, 404 para fracaso.
GET /pacientes/{dni}/turnos: para obtener los turnos que tiene el paciente. Devuelve 200 para caso de éxito, 404 para fracaso.
DELETE /pacientes/{dni}/turnos/{idturno}: para borrar un turno de un paciente. Devuelve 200 para caso de éxito, 404 para fracaso. Sólo se puede borrar si la fecha actual es menor a la fecha del turno. Es decir un turno futuro
```

## 2. Luego de una revisión se corrige el endpoint GET /pacientes , donde no tiene sentido devolver un error si no encuentra pacientes en el sistema aún. En su lugar, se devolvería un array vacío.

```txt
Para el endpoint GET /pacientes no devuelvas error. Devolvé un array vacío si aún no hay pacientes en el sistema
```

## 3. Se corrige para GET /pacientes/{dni}/turnos el error a devolver. Sólo se devuelve error si no se encontró el paciente por dni. En caso de que no haya turnos asociados, se devuelve array vacio

```txt
para GET /pacientes/{dni}/turnos se devulve error si no existe el paciente en el sistema (no se encuentra mediante el dni). si no se encuentran turnos asociados se devulve array vacio
```
