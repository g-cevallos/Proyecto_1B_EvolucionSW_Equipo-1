# Gestión de pedidos · Cafetería universitaria

![CI](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/actions/workflows/ci.yml/badge.svg)

Aplicación web para consultar el menú, registrar pedidos anticipados y retirarlos con un código. Proyecto de Construcción y Evolución de Software · **Release 1.0.0**.

**Integrantes:** Doménica Astudillo, Fernando Carrera, Guillermo Cevallos, Matthew Redín.

## Propósito

La cafetería universitaria necesita reducir el tiempo que se pierde registrando pedidos en horas de alta demanda, dar seguimiento a cada pedido y evitar confusiones al entregarlo. Esta aplicación permite que el cliente haga su pedido desde su celular o computador antes de llegar, y que el personal lo prepare y lo entregue verificando un código de retiro.

## Funcionalidades principales

**Cliente (estudiante o docente)**
- Registro con cédula ecuatoriana validada, celular y correo institucional; ingreso con cédula y correo.
- Consulta del menú con productos disponibles y precios.
- Selección de productos y cantidades, con el importe total antes de confirmar.
- Confirmación del pedido y **código de retiro** de 6 caracteres.
- Seguimiento del estado del pedido (Pendiente → En preparación → Listo para retirar → Entregado), con fecha y responsable de cada cambio.

**Personal de cafetería**
- Ingreso con usuario y clave.
- Pedidos agrupados por estado y en orden de llegada, con avance paso a paso.
- Entrega del pedido **solo con el código** que presenta el cliente.
- Mantenimiento del menú: alta, edición de precios y activación o desactivación de productos.

**Calidad**
- Importes en centavos enteros, restricciones de integridad en la base de datos, protección CSRF y control de concurrencia entre empleados.
- Pruebas automáticas con cobertura mínima del 85 % y análisis estático en cada cambio.

## Requisitos previos

| Elemento | Requisito |
|---|---|
| Python | 3.11 o superior (probado en 3.11, 3.12 y 3.13). Incluye SQLite: no hace falta instalar un servidor de base de datos. |
| Git | Para clonar el repositorio (opcional: también sirve descargar el ZIP). |
| Navegador | Chrome, Edge, Firefox o Safari actualizados. |
| Internet | Solo para descargar el código y las dependencias. |

## Instalación y ejecución

```bash
git clone https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1.git
cd Proyecto_1B_EvolucionSW_Equipo-1
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1   ·   Git Bash: source .venv/Scripts/activate
# Linux/macOS:          source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Abra <http://127.0.0.1:5000>.

- **Cliente:** use «Registrarme» y luego haga su pedido.
- **Personal:** usuario `admin`, clave `cafeteria2026`. Cámbiela con `CAFETERIA_ADMIN_CLAVE` **antes de la primera ejecución**; después de crearse el usuario, la variable ya no tiene efecto.

En la primera ejecución se crea la carpeta `instance/` con la base de datos y se carga un menú de ejemplo. Para detener la aplicación, presione `Ctrl + C`.

## Estructura del repositorio

```text
.
├── app/
│   ├── __init__.py          # create_app: construye la aplicación Flask
│   ├── config.py            # configuración desde variables de entorno
│   ├── datos_demo.py        # menú de ejemplo de la primera ejecución
│   ├── dominio/             # entidades, validaciones y excepciones de negocio
│   ├── persistencia/        # conexión SQLite, esquema y repositorios
│   ├── servicios/           # casos de uso y reglas de negocio
│   └── web/                 # rutas del cliente y del personal, plantillas y estilos
├── tests/                   # pruebas automáticas (pytest)
├── scripts/capturas.py      # prueba de sistema con navegador que genera las capturas del manual
├── .github/workflows/ci.yml # integración continua
├── pyproject.toml           # configuración de pytest, cobertura, pylint y bandit
├── .flake8                  # configuración de flake8
├── requirements.txt         # dependencias de ejecución
├── requirements-dev.txt     # dependencias de desarrollo y pruebas
└── run.py                   # punto de entrada: python run.py
```

La aplicación se organiza en cuatro capas (web → servicios → persistencia → dominio). Cada capa solo depende de las inferiores.

**Ramas**

| Rama | Contenido |
|---|---|
| `main` | Código estable. La versión publicada lleva la etiqueta `v1.0.0`. |
| `develop` | Integración del trabajo en curso. |
| `documentacion` | Documentos del proyecto en la carpeta `docs/`. No se fusiona en `main`. |

## Configuración local

Todo se configura con variables de entorno, y todas son opcionales.

| Variable | Por defecto | Descripción |
|---|---|---|
| `CAFETERIA_DB` | `instance/cafeteria.db` | Ruta del archivo de la base de datos. |
| `CAFETERIA_SECRET_KEY` | se genera en `instance/secret_key` | Clave que firma las cookies de sesión. |
| `CAFETERIA_DOMINIO_CORREO` | `epn.edu.ec` | Dominio del correo institucional válido para el registro. |
| `CAFETERIA_CANTIDAD_MAXIMA` | `50` | Máximo de unidades por producto en un pedido. |
| `CAFETERIA_DATOS_DEMO` | `1` | `0` para no cargar el menú de ejemplo. |
| `CAFETERIA_ADMIN_USUARIO` | `admin` | Usuario inicial del personal. |
| `CAFETERIA_ADMIN_CLAVE` | `cafeteria2026` | Clave inicial del personal. |
| `CAFETERIA_HOST` / `CAFETERIA_PUERTO` | `127.0.0.1` / `5000` | Dirección y puerto del servidor. |

Ejemplo (Linux/macOS): `CAFETERIA_PUERTO=8000 CAFETERIA_DOMINIO_CORREO=uce.edu.ec python run.py`.
En PowerShell: `$env:CAFETERIA_PUERTO="8000"; python run.py`.

**Empezar con una base de datos nueva:** detenga la aplicación y borre `instance/cafeteria.db`.

**Agregar otro usuario del personal:**

```bash
flask --app run crear-personal maria "María Pérez" --clave "clave-segura-1"
```

## Pruebas

Instale las dependencias de desarrollo y ejecute la suite desde la raíz del repositorio:

```bash
pip install -r requirements-dev.txt
pytest                                                   # todas las pruebas
pytest --cov=app --cov-branch --cov-report=term-missing  # con cobertura
pytest tests/test_web_cliente.py                         # un solo archivo
```

Las pruebas no usan la base de datos real: cada una crea la suya en memoria o en una carpeta temporal.

| Archivo | Qué verifica |
|---|---|
| `test_validaciones.py`, `test_dominio.py` | Validación de datos y entidades del dominio. |
| `test_persistencia.py` | Esquema SQLite, restricciones y repositorios. |
| `test_menu_servicio.py`, `test_cliente_personal.py`, `test_pedido_registro.py`, `test_pedido_atencion.py` | Reglas de negocio de los servicios. |
| `test_aplicacion.py`, `test_web_comun.py`, `test_web_cliente.py`, `test_web_personal.py` | Rutas, sesión, CSRF y flujos completos de cliente y personal. |
| `test_rendimiento.py` | Tiempo de respuesta con 1 000 pedidos. |

**Análisis estático** (lo mismo que ejecuta la integración continua):

```bash
flake8 .
pylint $(git ls-files 'app/*.py' 'run.py') --fail-under=9.0
bandit -r app -ll
```

**Prueba de sistema con navegador** (genera las capturas del manual de usuario):

```bash
python -m playwright install chromium
python scripts/capturas.py docs/img
```

Cada cambio enviado a GitHub ejecuta estas comprobaciones en Python 3.11, 3.12 y 3.13 (pestaña *Actions*). La cobertura mínima exigida es 85 %.

## Documentación

Los documentos están en la rama [`documentacion`](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/tree/documentacion/docs), carpeta `docs/`:

| N.º | Documento |
|---|---|
| 1 | [Requisitos](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/01_requisitos.md) |
| 2 | [Diseño](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/02_diseno.md) |
| 3 | [Ambiente de desarrollo](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/03_ambiente_desarrollo.md) |
| 4 | [Análisis estático](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/04_analisis_estatico.md) |
| 5 | [Documentación técnica](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/tree/documentacion/docs/05_documentacion_tecnica) (generada con pdoc; para verla, clone la rama y abra `index.html`) |
| 6 | [Casos de prueba](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/06_casos_prueba_sistema.pdf) |
| 7 | [Manual de instalación](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/07_manual_instalacion.md) |
| 8 | [Manual de usuario](https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1/blob/documentacion/docs/08_manual_usuario.md) |

## Guía de estilos

Los estilos residen en un único archivo (`app/web/static/estilos.css`), sin frameworks externos, manteniendo la metáfora visual de **pizarra de cafetería** (`.pizarra`) y **ticket de retiro troquelado** (`.ticket`), con soporte automático para modo claro y modo oscuro (`prefers-color-scheme: dark`).

### Paleta principal

| Token CSS | Modo claro | Modo oscuro | Uso principal |
| :--- | :--- | :--- | :--- |
| `--pizarra` / `--pizarra-2` | `#163a35` / `#1f4a44` | `#163a35` / `#1f4a44` | Cabecera, pizarra del menú, hero y pestaña activa |
| `--madera` / `--madera-oscura` | `#6e4e34` / `#49321f` | `#6e4e34` / `#49321f` | Marco biselado de la pizarra |
| `--tiza` / `--tiza-2` | `#f5efe4` / `#ebe2d2` | `#111816` / `#17211e` | Fondo general cálido (papel craft) y superficies secundarias |
| `--papel` / `--papel-2` | `#fffdf8` / `#f9f4ea` | `#1b2523` / `#212e2b` | Tarjetas, formularios, tablas y ticket de retiro |
| `--tinta` / `--tinta-suave` | `#1b2422` / `#52605d` | `#e8eeec` / `#a7b8b4` | Texto principal y secundario |
| `--mostaza` / `--mostaza-oscura` | `#d99a1e` / `#a8730c` | `#d99a1e` / `#a8730c` | Botón principal, foco visible y acentos |
| `--verde` / `--rojo` | `#267045` / `#b3261e` | `#81c995` / `#f28b82` | Avisos de éxito/error e indicadores de disponibilidad |

### Tipografías

- **Títulos y encabezados de pizarra (`--fuente-titulos`)**: `Georgia, "Palatino Linotype", "Book Antiqua", "Times New Roman", serif`.
- **Interfaz, formularios y tablas (`--fuente-base`)**: `"Segoe UI", system-ui, -apple-system, Roboto, "Helvetica Neue", Arial, sans-serif` (precios e importes con `font-variant-numeric: tabular-nums`).
- **Códigos de retiro y producto (`--fuente-mono`)**: `ui-monospace, "Cascadia Mono", Consolas, "Liberation Mono", monospace`.

### Variables de diseño adicionales

- **Espaciado y medidas**: `--espacio-2xs` (`0.15rem`) a `--espacio-4xl` (`3.5rem`), `--ancho-maximo` (`64rem`), `--alto-tactil` (`2.75rem`, mínimo 44 px para áreas táctiles).
- **Bordes, radios y sombras**: `--radio-xs` (`4px`), `--radio` (`8px`), `--radio-md` (`12px`), `--radio-pildora` (`999px`), `--sombra-suave`, `--sombra-tarjeta`, `--sombra-pizarra` y `--sombra-ticket`.
- **Estados de pedido (`.estado-*`)**: variables `--estado-{pendiente,preparacion,listo,entregado}-{texto,borde,fondo}` ajustadas para cumplir contraste WCAG AA en modo claro y oscuro.

