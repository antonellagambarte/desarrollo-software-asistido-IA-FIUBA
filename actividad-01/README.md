# CAPTCHA para inicio de sesión — Bad UI

## ¿Qué es?

Consiste en una página de login con un sistema de CAPTCHA diseñado para ser incómodo de ingresar.

El usuario debe revelar caracteres ocultos raspando una superficie hecha con canvas sobre una grilla 6x6. Si se revela una celda incorrecta, todo el progreso se reinicia.

---

## Autora

Proyecto realizado por Antonella Gambarte para la materia Desarrollo de Software asistido por IA.

## ¿Cómo funciona?

1. El usuario ingresa usuario y contraseña (ingresar cualquier cosa ya que no tiene especificado un usuario y contraseña).
2. Al presionar "Ingresar" aparece una modal.
3. Se genera una grilla 6x6 con caracteres aleatorios y un código captcha de 5 caracteres.
4. El usuario raspa la celdas para develar el caracter oculto.
5. Si el usuario raspa una celda incorrecta:
   - el canvas se reinicia,
   - la grilla vuelve a ocultarse,
   - y el usuario debe comenzar nuevamente.

---

## Qué funcionó

Con la indicación 1 se logró crear un formulario con buena estética y funcionalidad inicial, además de respetar que sea una single page.

Con la indicación 2 creó muy bien lo que se pretendía en cuanto al captcha(sin entrar en muchos detalles de la funcionalidad). Se logró crear la grilla, con los caracteres aleatorios y el canvas encima, además de la animación de raspado sobre las celdas.

## Qué no funcionó

La indicación 3 no fue muy clara. Además, se mezclaron distintas indicaciones que sólo logró que la animación que se había construído hasta el momento, se borrara. Con las inidicaiones 4 y 5, no se logró reestablecer eso. La indicación 6 fue concisa pero muy clara para lograr reestablecer el canvas y la animación.

La indicación 8 "vamos a corregir solo la funcionalidad...", provocó que el LLM devolviera sólo la función a modificar y dejara de devolver el código del html completo. En realidad, lo que se pretendía era inidicar que la parte visual, por el momento, quedaba como estaba y que se concentrara sólo en lo funcional.

---
