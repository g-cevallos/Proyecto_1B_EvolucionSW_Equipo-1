# 1. Documentación de Requisitos

**Proyecto:** Gestión de pedidos de una cafetería universitaria
**Versión del producto:** Release 1.0 · **Fecha comprometida:** 27 de noviembre de 2026
**Fuente:** *Especificación inicial de necesidades del cliente*, versión 1.0 (27/10/2026)

## 1.1 Propósito y alcance

Este documento traduce la especificación del cliente en historias de usuario con criterios de aceptación, requisitos funcionales y no funcionales verificables, y una matriz de trazabilidad que conecta cada necesidad con el código y con los casos de prueba. También registra las ambigüedades encontradas y la decisión tomada para cada una.

El sistema permite a estudiantes y docentes consultar el menú, registrar pedidos anticipados y retirarlos con un código; y al personal de cafetería mantener el menú y registrar el avance de cada pedido hasta su entrega.

## 1.2 Objetivo del Release 1.0
Entregar, el 27 de noviembre de 2026, una primera versión estable de la aplicación web de la cafetería universitaria que permita a los clientes consultar el menú, registrar pedidos anticipados y retirarlos con un código, y al personal mantener el menú y registrar el avance de cada pedido hasta su entrega. Con ello se busca reducir el tiempo de registro en períodos de alta demanda, mejorar el seguimiento de los pedidos y evitar confusiones en la entrega.

## 1.3 Usuarios del sistema

| Actor | Descripción | Necesidades principales |
|---|---|---|
| Cliente | Estudiante o docente identificado por código, nombre, apellido, cédula, celular y correo institucional. | Ver el menú con precios, pedir, conocer el total, obtener un código de retiro y seguir el estado del pedido. |
| Personal de cafetería | Trabajador que mantiene el menú y procesa los pedidos. | Registrar y actualizar productos, consultar pedidos por estado, registrar avances y entregas. |

## 1.4 Requisitos de negocio

| ID | Requisito de negocio | Cómo lo atiende la solución |
|---|---|---|
| RN-01 | Reducir el tiempo empleado en registrar los pedidos durante períodos de alta demanda. | El cliente registra su pedido desde su dispositivo antes de llegar; el personal no digita pedidos. |
| RN-02 | Facilitar que los clientes conozcan los productos y precios antes de pedir. | Menú público con productos disponibles y precios. |
| RN-03 | Mejorar el seguimiento de los pedidos desde su recepción hasta la entrega. | Estados con orden obligatorio, vista por estado para el personal y línea de tiempo con fecha y responsable de cada cambio. |
| RN-04 | Reducir confusiones al entregar pedidos. | Entrega solo con código de retiro verificado y solo si el pedido está Listo para retirar. |

## 1.5 Requisitos de usuario

| ID | Requisito de usuario |
|---|---|
| RU-01 | El cliente necesita consultar el menú de la cafetería, con los productos disponibles y sus precios. |
| RU-02 | El cliente necesita seleccionar uno o más productos y las cantidades que desea pedir. |
| RU-03 | El cliente necesita conocer el importe total antes de confirmar su pedido. |
| RU-04 | El cliente necesita confirmar un pedido y obtener un código que permita identificarlo al momento del retiro. |
| RU-05 | El cliente necesita consultar el estado de su pedido. |
| RU-06 | El personal necesita registrar o actualizar los productos del menú, sus precios y su disponibilidad. |
| RU-07 | El personal necesita consultar los pedidos y registrar sus avances hasta la entrega. |

## 1.6 Historias de usuario

Prioridad según MoSCoW (M = imprescindible, S = importante, C = deseable). Estimación en puntos de historia (escala Fibonacci). Los criterios de aceptación usan el formato *Dado / Cuando / Entonces*.

### HU-01 · Registrarme como cliente
**Como** cliente **quiero** registrarme con mis datos **para** poder hacer pedidos y consultarlos.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** que ingreso nombre, apellido, cédula válida, celular y correo institucional, **cuando** envío el formulario, **entonces** quedo registrado, recibo un código `CLI-xxxxx` y paso al menú. | |
| 2 | **Dado** una cédula con dígito verificador incorrecto, un celular que no empieza con 09 o un correo de otro dominio, **cuando** envío, **entonces** veo el motivo y no se registra nada. | |
| 3 | **Dado** que la cédula o el correo ya están registrados, **cuando** envío, **entonces** se me informa y no se crea un duplicado. | |

### HU-02 · Identificarme como cliente
**Como** cliente registrado **quiero** ingresar con mi cédula y correo **para** pedir y ver mis pedidos.
Prioridad: M · Estimación: 2

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** que mi cédula y correo coinciden con un registro, **cuando** ingreso, **entonces** accedo al menú con mi nombre visible. | |
| 2 | **Dado** una combinación que no coincide, **cuando** ingreso, **entonces** veo «La cédula y el correo no corresponden a un cliente registrado». | |
| 3 | **Dado** que no he ingresado, **cuando** intento revisar un pedido o ver «Mis pedidos», **entonces** se me lleva a la pantalla de ingreso. | |

### HU-03 · Consultar el menú (RU-01)
**Como** cliente **quiero** ver los productos disponibles con sus precios **para** decidir qué pedir.
Prioridad: M · Estimación: 2

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** productos disponibles y no disponibles, **cuando** abro el menú, **entonces** veo solo los disponibles, agrupados en alimentos y bebidas, con su precio. | |
| 2 | **Dado** que no he ingresado, **cuando** abro el menú, **entonces** puedo verlo pero se me invita a ingresar para pedir. | |

### HU-04 · Seleccionar productos y cantidades (RU-02)
**Como** cliente **quiero** indicar la cantidad de cada producto **para** armar mi pedido.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** el menú, **cuando** escribo cantidades en uno o más productos, **entonces** solo esos productos forman la selección. | |
| 2 | **Dado** que no escribo ninguna cantidad, **cuando** pido revisar, **entonces** veo «Seleccione al menos un producto»| |
| 3 | **Dado** una cantidad negativa, decimal o no numérica, **cuando** pido revisar, **entonces** veo que debe ser un entero positivo. | |
| 4 | **Dado** una cantidad mayor que el máximo configurado, **cuando** pido revisar, **entonces** se rechaza. | |
| 5 | **Dado** un producto no disponible, **cuando** intento incluirlo, **entonces** se rechaza. | |

### HU-05 · Conocer el importe total antes de confirmar (RU-03)
**Como** cliente **quiero** ver el detalle y el total **para** confirmar sabiendo cuánto pagaré.
Prioridad: M · Estimación: 2

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** una selección válida, **cuando** pido revisar, **entonces** veo cada producto con cantidad, precio vigente y subtotal, y el total igual a la suma de precio × cantidad. | |
| 2 | **Dado** que un precio cambió mientras revisaba, **cuando** confirmo, **entonces** el pedido no se registra, veo el nuevo total y debo confirmar otra vez. | |

### HU-06 · Confirmar el pedido y obtener un código de retiro (RU-04)
**Como** cliente **quiero** confirmar y recibir un código **para** retirar mi pedido sin confusiones.
Prioridad: M · Estimación: 5

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** que reviso una selección válida, **cuando** confirmo, **entonces** el pedido se registra en estado Pendiente con fecha, total y un código de retiro de 6 caracteres que se muestra en pantalla. | |
| 2 | **Dado** que existen pedidos registrados, **cuando** se confirma un nuevo pedido, **entonces** el código generado es diferente a todos los códigos de retiro existentes. | |
| 3 | **Dado** un pedido confirmado, **cuando** el personal cambia después el precio del producto, **entonces** mi pedido conserva el precio con el que se confirmó. | |
| 4 | **Dado** que un producto deja de estar disponible antes de confirmar, **cuando** confirmo, **entonces** se informa el motivo y el pedido no se registra. | |

### HU-07 · Consultar el estado de mis pedidos (RU-05)
**Como** cliente **quiero** ver el estado de mis pedidos **para** saber cuándo retirarlos.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** que tengo pedidos, **cuando** abro «Mis pedidos», **entonces** veo cada uno con fecha, código, estado y total, del más reciente al más antiguo. | |
| 2 | **Dado** un pedido, **cuando** abro su detalle, **entonces** veo el seguimiento con la hora de cada estado alcanzado. | |
| 3 | **Dado** el pedido de otro cliente, **cuando** intento abrirlo, **entonces** no se muestra. | |

### HU-08 · Registrar productos en el menú (RU-06)
**Como** personal **quiero** agregar productos **para** mantener el menú actualizado.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** código, nombre, categoría, precio y disponibilidad válidos, **cuando** guardo, **entonces** el producto aparece en el listado y en el menú si está disponible. | |
| 2 | **Dado** un código ya existente, un precio ≤ 0 o con más de dos decimales, **cuando** guardo, **entonces** veo el motivo y no se registra. | |

### HU-09 · Actualizar productos, precios y disponibilidad (RU-06)
**Como** personal **quiero** modificar productos y marcarlos como disponibles o no **para** reflejar lo que realmente puedo vender.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** un producto, **cuando** cambio nombre, categoría o precio, **entonces** los nuevos pedidos usan los nuevos valores y los anteriores conservan los suyos. | |
| 2 | **Dado** un producto disponible, **cuando** lo desactivo, **entonces** deja de aparecer en el menú del cliente y no puede pedirse. | |

### HU-10 · Ingresar como personal
**Como** personal **quiero** ingresar con usuario y clave **para** que solo el personal procese pedidos y modifique el menú.
Prioridad: M · Estimación: 2

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** usuario y clave correctos, **cuando** ingreso, **entonces** veo la lista de pedidos. | |
| 2 | **Dado** una clave incorrecta, **cuando** ingreso, **entonces** veo «Usuario o clave incorrectos». | |
| 3 | **Dado** que no he ingresado, **cuando** abro una página del personal, **entonces** se me redirige al ingreso. | |

### HU-11 · Consultar pedidos por estado (RU-07)
**Como** personal **quiero** ver los pedidos agrupados por estado y en orden de llegada **para** atenderlos en orden.
Prioridad: M · Estimación: 2

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** pedidos en varios estados, **cuando** abro una pestaña de estado, **entonces** veo solo esos pedidos, del más antiguo al más reciente, con cliente, productos y total, y el número de pedidos en cada pestaña. | |

### HU-12 · Registrar el avance de preparación (RU-07)
**Como** personal **quiero** marcar un pedido como En preparación y luego como Listo para retirar **para** que el cliente sepa cuándo acercarse.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** un pedido Pendiente, **cuando** pulso «Iniciar preparación», **entonces** pasa a En preparación; y desde ahí, con «Marcar listo para retirar», pasa a Listo para retirar. | |
| 2 | **Dado** cualquier pedido, **cuando** intento saltar, retroceder o repetir un estado, **entonces** se rechaza. | |
| 3 | **Dado** que dos empleados avanzan el mismo pedido a la vez, **cuando** ambos guardan, **entonces** solo el primero tiene efecto y el segundo recibe un aviso. | |

### HU-13 · Entregar un pedido verificando el código (RU-07)
**Como** personal **quiero** registrar la entrega solo con el código del cliente **para** no entregar pedidos equivocados.
Prioridad: M · Estimación: 3

| # | Criterio de aceptación | CP |
|---|---|---|
| 1 | **Dado** un pedido Listo para retirar, **cuando** escribo el código que presenta el cliente (sin importar mayúsculas, espacios o guiones) y registro la entrega, **entonces** pasa a Entregado. | |
| 2 | **Dado** un código que no corresponde al pedido, **cuando** registro la entrega, **entonces** se rechaza. | |
| 3 | **Dado** un pedido Pendiente o En preparación, **cuando** intento entregarlo aunque el código sea correcto, **entonces** se rechaza. | |
| 4 | **Dado** un pedido ya Entregado, **cuando** intento entregarlo otra vez, **entonces** se rechaza. | |
| 5 | **Dado** que intento pasar a Entregado sin código, **cuando** uso el avance de estado, **entonces** se rechaza. | |

## 1.7 Requisitos funcionales

| ID | El sistema debe… | HU | Verificación |
|---|---|---|---|
| RF-01 | registrar clientes validando cédula ecuatoriana (módulo 10), celular `09xxxxxxxx` y correo del dominio institucional configurado, sin duplicar cédula ni correo. | HU-01 | |
| RF-02 | asignar a cada cliente un código único con formato `CLI-00001`. | HU-01 | |
| RF-03 | identificar al cliente por cédula y correo institucional. | HU-02 | |
| RF-04 | mostrar el menú con productos disponibles, categoría y precio. | HU-03 | |
| RF-05 | aceptar cantidades enteras positivas hasta un máximo configurable (50 por defecto). | HU-04 | |
| RF-06 | rechazar pedidos vacíos, con productos inexistentes o no disponibles, indicando el motivo. | HU-04 | |
| RF-07 | calcular subtotales y total con el precio vigente antes de la confirmación. | HU-05 | |
| RF-08 | volver a validar disponibilidad y total al confirmar, y rechazar si el total cambió. | HU-05, HU-06 | |
| RF-09 | registrar el pedido en estado Pendiente con fecha, total, detalle con precio unitario congelado y código de retiro único de 6 caracteres. | HU-06 | |
| RF-10 | listar los pedidos del cliente con su estado, y mostrar el detalle y el seguimiento solo a su dueño. | HU-07 | |
| RF-11 | registrar, editar y activar/desactivar productos. | HU-08, HU-09 | |
| RF-12 | autenticar al personal con usuario y clave almacenada como hash. | HU-10 | |
| RF-13 | listar pedidos por estado en orden de llegada, con conteo por estado. | HU-11 | |
| RF-14 | permitir solo las transiciones Pendiente → En preparación → Listo para retirar. | HU-12 | |
| RF-15 | registrar Entregado solo para pedidos Listos para retirar y con el código correcto. | HU-13 | |
| RF-16 | guardar el historial de cambios de estado con fecha y usuario. | HU-07, HU-12 | |

## 1.8 Requisitos no funcionales

| ID | Categoría | Requisito | Verificación |
|---|---|---|---|
| RNF-01 | Persistencia | Productos, clientes, pedidos e historial persisten entre ejecuciones (SQLite en archivo). | |
| RNF-02 | Integridad | Las reglas críticas se refuerzan también en la base de datos: `UNIQUE` en código de retiro, cédula, correo y código de producto; `CHECK` en estados, precios y cantidades; claves foráneas activas. | |
| RNF-03 | Seguridad | Claves del personal con hash (PBKDF2/scrypt de Werkzeug); protección CSRF en todo formulario; cookies de sesión `HttpOnly` y `SameSite=Lax`; consultas SQL parametrizadas; redirecciones solo a rutas internas. | |
| RNF-04 | Usabilidad | Interfaz en español, adaptable a celulares (desde 360 px), mensajes de error que indican qué corregir, foco de teclado visible. | |
| RNF-05 | Mantenibilidad | Calificación pylint ≥ 9.0, 0 avisos flake8, complejidad ciclomática promedio A, cobertura de pruebas ≥ 85 %. | |
| RNF-06 | Portabilidad | Funciona en Windows, macOS y Linux con Python 3.11 o superior, sin servicios externos. | |
| RNF-07 | Rendimiento | Las páginas responden en menos de 1 s con hasta 1 000 pedidos en una instalación local. | |
| RNF-08 | Concurrencia | Dos usuarios del personal no pueden aplicar el mismo cambio de estado dos veces. | |

## 1.9 Reglas de negocio
| Regla | Dónde se aplica | Prueba |
|---|---|---|
| RN-NEG-01 Al menos un producto; cantidades enteras positivas. | | |
| RN-NEG-02 Solo productos disponibles en nuevos pedidos. | | |
| RN-NEG-03 Total = Σ precio vigente × cantidad. | | |
| RN-NEG-04 El precio del pedido no cambia si cambia el menú. | | |
| RN-NEG-05 Código de retiro único. | | |
| RN-NEG-06 Pendiente → En preparación → Listo para retirar → Entregado, en ese orden. | | |
| RN-NEG-07 Entregado solo desde Listo para retirar y con el código del cliente. | | |

## 1.10 Ambigüedades detectadas y decisiones tomadas

La especificación deja abiertos varios puntos. El equipo tomó las decisiones siguientes, que deben **validarse con el cliente** antes del cierre del Release 1.0.

| # | Ambigüedad | Decisión | Justificación |
|---|---|---|---|
| A-01 | ¿Cómo se identifica el cliente para consultar sus pedidos? | Registro único con sus datos; luego ingresa con cédula y correo institucional. | La sección 7 pide identificarlo con datos personales; evita gestionar contraseñas en la primera versión. |
| A-02 | ¿Qué es un «correo institucional»? | Correo cuyo dominio es el configurado (`CAFETERIA_DOMINIO_CORREO`, por defecto `epn.edu.ec`) o un subdominio suyo. | Distintas instituciones usan dominios distintos; se deja configurable. |
| A-03 | ¿Cómo se valida la cédula? | Algoritmo oficial de módulo 10 (personas naturales). | Evita registros con cédulas mal digitadas. |
| A-04 | ¿Existe un límite de cantidad por producto? | Máximo 50 unidades por producto, configurable. | Previene errores de digitación (p. ej. 500 en lugar de 5)|
| A-05 | ¿Qué ocurre si cambia un precio entre la revisión y la confirmación? | Se rechaza la confirmación, se muestra el nuevo total y el cliente confirma otra vez. | RU-03 exige que el cliente conozca el total antes de confirmar; cobrarle un total distinto lo contradiría. |
| A-06 | ¿El menú del cliente muestra productos no disponibles? | No; solo los disponibles (el personal ve todos). | RU-01 habla de «productos disponibles». |
| A-07 | ¿Quién ve el código de retiro? | Solo el cliente. El personal busca el pedido escribiendo el código que el cliente presenta. | Si el personal viera el código, la verificación perdería sentido.|
| A-08 | Formato del código de retiro. | 6 caracteres de un alfabeto sin caracteres ambiguos (sin 0/O, 1/I/L). | Fácil de leer en voz alta; ~887 millones de combinaciones, difícil de adivinar. |
| A-09 | ¿Puede eliminarse un producto? | No; se desactiva. | Preserva la integridad de pedidos históricos que lo referencian. |
| A-10 | ¿Puede cancelarse un pedido? | No en el Release 1.0. | La especificación no lo menciona. Se propone para una versión posterior. |
| A-11 | Moneda y redondeo. | Dólares estadounidenses; importes almacenados en centavos enteros. | Evita errores de redondeo de punto flotante. |
| A-12 | ¿Cómo se autentica el personal? | Usuario y clave; se crea un usuario inicial (`admin`) y pueden añadirse otros por línea de comandos. | La especificación no detalla gestión de usuarios del personal. |

## 1.11 Fuera de alcance (Release 1.0)

Pago electrónico o cobro en línea, integración con servicios financieros, notificaciones por correo o mensajería, impresoras o lectores de códigos, promociones, reembolsos, pedidos programados, gestión de inventario de ingredientes, cancelación de pedidos y gestión de usuarios del personal desde la interfaz.

## 1.12. Matriz de trazabilidad

Las siguientes matrices permiten relacionar las necesidades y reglas establecidas por el cliente con los requisitos derivados por el equipo, las historias de usuario y los elementos definidos en el diseño.

La trazabilidad permite comprobar que las funcionalidades desarrolladas responden al alcance del proyecto y que los requisitos cuentan con elementos de diseño y verificación asociados.

### 1.12.1. Matriz de trazabilidad funcional

| Requisito de negocio | Requisito de usuario | Regla de negocio | Historia de usuario | Requisito funcional | Elementos de diseño relacionados | Casos de prueba |
|---|---|---|---|---|---|---|
| RN-01, RN-03 (relación de apoyo) | — | — | HU-01. Registrar cliente | RF-01, RF-02 | CU-01, ruta `/registro`, modelo Cliente y sección 2.7 | Pendiente |
| RN-01, RN-03 (relación de apoyo) | RU-04, RU-05 (relación de apoyo) | — | HU-02. Identificar cliente | RF-03 | CU-02, ruta `/ingresar`, sección 2.9 de seguridad y gestión de sesión | Pendiente |
| RN-02 | RU-01 | — | HU-03. Consultar menú | RF-04 | CU-03, ruta `/menu`, modelo Producto y sección 2.8 | Pendiente |
| RN-01 | RU-02 | RN-NEG-01, RN-NEG-02 | HU-04. Seleccionar productos y cantidades | RF-05, RF-06 | CU-04, PN-01, ruta `/pedido/revisar`, modelo Pedido y Detalle del pedido | Pendiente |
| RN-01, RN-02 | RU-03 | RN-NEG-03 | HU-05. Consultar importe total | RF-07, RF-08 | CU-04, PN-01, ruta `/pedido/revisar`, decisiones D-04 y D-05 | Pendiente |
| RN-01, RN-04 | RU-04 | RN-NEG-01, RN-NEG-02, RN-NEG-03, RN-NEG-04, RN-NEG-05, RN-NEG-06 | HU-06. Confirmar pedido y obtener código | RF-08, RF-09 | CU-04, PN-01, ruta `/pedido/confirmar`, decisiones D-04, D-05 y D-09 | Pendiente |
| RN-03 | RU-05 | RN-NEG-06 | HU-07. Consultar estado del pedido | RF-10, RF-16 | CU-05, ruta `/mis-pedidos`, ruta `/mis-pedidos/<id>`, diagrama de estados de la sección 2.5 | Pendiente |
| RN-02 | RU-06 | — | HU-08. Registrar productos | RF-11 | CU-07, rutas `/personal/productos` y `/personal/productos/nuevo`, modelo Producto | Pendiente |
| RN-02 | RU-06 | RN-NEG-04 | HU-09. Actualizar productos, precios y disponibilidad | RF-11 | CU-07, rutas `/personal/productos/<codigo>/editar` y `/personal/productos/<codigo>/disponibilidad`, modelo Producto | Pendiente |
| RN-02, RN-03 (relación de apoyo) | RU-06, RU-07 (relación de apoyo) | — | HU-10. Iniciar sesión del personal | RF-12 | CU-06, ruta `/personal/ingresar` y sección 2.9 de seguridad | Pendiente |
| RN-03 | RU-07 | RN-NEG-06 | HU-11. Consultar pedidos por estado | RF-13 | CU-08, PN-02, ruta `/personal/pedidos?estado=` y modelo Pedido | Pendiente |
| RN-03 | RU-07 | RN-NEG-06 | HU-12. Avanzar estado de preparación | RF-14, RF-16 | CU-09, PN-02, diagrama de estados de la sección 2.5, ruta `/personal/pedidos/<id>/avanzar` y decisión D-08 | Pendiente |
| RN-03, RN-04 | RU-07 | RN-NEG-06, RN-NEG-07 | HU-13. Entregar pedido verificando código | RF-15 | CU-10, PN-02, diagrama de estados de la sección 2.5, rutas `/personal/entrega` y `/personal/entrega/confirmar`, decisión D-07 | Pendiente |


### 1.12.2. Matriz de trazabilidad de requisitos no funcionales

Esta matriz relaciona los requisitos no funcionales definidos por el equipo con los elementos de diseño y las formas previstas para verificar su cumplimiento.

| Requisito de negocio relacionado | Requisito no funcional | Elementos de diseño o documentación relacionados | Método de verificación | Casos de prueba |
|---|---|---|---|---|
| RN-01, RN-03 | RNF-01. Persistencia de información | Arquitectura de persistencia, sección 2.1; modelo de datos, sección 2.7; decisión D-02 | Registrar productos y pedidos, reiniciar la aplicación y comprobar que la información se conserva | Pendiente |
| RN-01, RN-03, RN-04 | RNF-02. Integridad de la base de datos | Modelo de datos y diccionario, sección 2.7; restricciones UNIQUE, CHECK y claves foráneas | Comprobar que la base de datos rechaza registros duplicados o datos que incumplen las restricciones | Pendiente |
| RN-01, RN-02, RN-03, RN-04 | RNF-03. Seguridad | Rutas y navegación, sección 2.8; seguridad, sección 2.9; manejo de errores, sección 2.10 | Verificar autenticación, control de acceso, protección CSRF, sesiones y validación de datos | Pendiente |
| RN-02, RN-03 | RNF-04. Usabilidad | Diseño de interfaz y navegación, sección 2.8 | Comprobar la visualización desde distintos tamaños de pantalla, la navegación con teclado y la claridad de los mensajes | Pendiente |
| RN-01, RN-02, RN-03, RN-04 | RNF-05. Mantenibilidad | Documento de ambiente de desarrollo, `03_ambiente_desarrollo.md`; herramientas de calidad y configuración de pruebas | Ejecutar las herramientas de análisis estático y comprobar los niveles de cobertura y calidad establecidos | Pendiente |
| RN-01, RN-02, RN-03, RN-04 | RNF-06. Portabilidad | Documento de ambiente de desarrollo, `03_ambiente_desarrollo.md`; configuración de Python y dependencias | Instalar y ejecutar la aplicación en los sistemas operativos contemplados en el requisito | Pendiente |
| RN-01, RN-03 | RNF-07. Rendimiento | Arquitectura de persistencia, sección 2.1; modelo de datos e índices, sección 2.7 | Medir el tiempo de consulta con un conjunto de hasta 1000 pedidos y comprobar el límite establecido de un segundo | Pendiente |
| RN-03 | RNF-08. Concurrencia | Diagrama de estados, sección 2.5; diagramas de secuencia, sección 2.6; decisión D-08 | Simular que dos trabajadores intentan modificar simultáneamente el estado de un mismo pedido y comprobar que no se aplique dos veces el mismo cambio | Pendiente |
