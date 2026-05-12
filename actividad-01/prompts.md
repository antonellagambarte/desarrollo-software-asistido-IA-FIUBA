# Prompts - Captcha para inicio de sesión

## 1. Creación de formulario base

Crea una página HTML simple con login usando un único archivo HTML, CSS y JS inline, sin dependencias externas.

```txt
Necesito que me hagas una página con un formulario con dos campos: uno para ingresar un usuario y otro para ingresar contraseña y abajo un boton que diga "ingresar". Tiene que ser en un solo archivo html, con css y js inline, vanilla js, sin dependencias externas.
```

## 2. Se agrega captcha

```txt
Ahora, hay que agregarle un captcha para permitir el acceso. Al hacer click sobre el botón ingresar se debe abrir una modal con una grilla tipo captcha de 6x6. Cada celda debe estar separada 8px. Cada celda debe contener un carácter aleatorio (A-Z, 0-9). La grilla tiene que estar debajo de una capa que luego voy a raspar con canvas. También necesito la funcionalidad para saber qué caracteres están en qué posiciones.
```

## 3. Se agrega validación del captcha

```txt
Bien. Ahora, en la misma modal se debe indicar cual es el valor correcto a ingresar. Si el usuario raspa una celda que no corresponde, debe volver a empezar. Que el valor sea de longitud 5.
```

## 4. Se borró la animación de raspado. Se pide mantenerlo y se explica el funcionamiento pretendido.

```txt
No saques la animación de raspado. Eso debe quedar igual. Tanto el valor correcto a ingresar como la grilla deben ser fijos. Si el usuario raspa una celda que no corresponde, se tienen que cubrir nuevamente todas las celdas para que el usuario vuelva a iniciar el raspado.
```

## 5. Con la orden anterior, se borró el canvas. Se explica nuevamente el funcionamiento y se da precisiones de cuando se considera que una celda está raspada.

```txt
Ahora aparecen todas las celdas descubiertas. El usuario revela celdas al raspar con el mouse sobre un canvas. Se debe detectar qué celda se está revelando. Si el usuario revela una celda incorrecta, se debe reiniciar completamente el estado: volver a ocultar toda la grilla y resetear el canvas. Una celda se considera revelada cuando el usuario la raspa al menos en un 70%.
```

## 6. Con la orden anterior no se logró que el canvas vuelva a aparecer sobre la grilla.

```txt
La grilla debe estar completamente oculta al inicio bajo un canvas. El usuario no debe ver ninguna letra hasta que la raspe.
```

## 7. Ahora se indica que se agregue las guías al canvas para que el usuario pueda distinguir cada celda.

```txt
agregale al canvas una cuadrícula como guía.
```

## 8. Se da indicaciones para corregir el funcionamiento del captcha en caso de que el usuario raspe una celda equivocada.

```txt
Perfecto, ahora vamos a corregir solo la funcionalidad. Cuando el usuario raspe una celda equivocada (es decir una que no contenga alguno de los caracteres que son parte del captcha correcto), se debe reiniciar en canvas para que el usuario comience de nuevo a raspar
```

## 9. Se delvolvió solo la función específica a cambiar, por que se pide que devuelva el código completo.

```txt
devolve el codigo completo
```

## 10. Se corrige el área con el que se considera una celda raspada.

```txt
vamos a disminuir el porcentaje con el que se considera una celda descubierta. Que sea el 30% y no el 75%
```

## 11. Se disminuye el tamañó del pincel de raspado.

```txt
Ahora quiero reducir el tamaño del pincel de raspado en el canvas. El área de borrado debe ser pequeña (por ejemplo un radio de 5 o 10px)
```

## 12. Se disminuye aún más el aréa con el que se considera una celda raspada.

```txt
Ahora, hay que disminuir mas el area que se considera para decir que una celda esta revelada.que sea del 10%
```

## 13. Nuevamente se devolvió sólo una porción de código. Se pide código completo.

```txt
devolveme el codigo completo
```

## 14. Ahora se pide que para cada intento de ingreso se genere un nuevo código y una nueva grilla.

```txt
bien, ahora cada vez que se presione el boton "ingresar", se debe generar un codigo captcha y una nueva grilla
```

## 14. Corrección de tamaño de letras en grilla.

```txt
aumentá el tamaño de las letras de la grilla. Probemos con 32px
```
