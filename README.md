# Gestión de pedidos · Cafetería universitaria

Aplicación web para consultar el menú, registrar pedidos anticipados y retirarlos con un código. Proyecto de Construcción y Evolución de Software.

**Integrantes:** Doménica Astudillo, Fernando Carrera, Guillermo Cevallos, Matthew Redín.

## Ramas

- `main`: versión estable.
- `develop`: integración.
- `documentacion`: entregables en la carpeta `docs/`.

## Inicio rápido

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Abra <http://127.0.0.1:5000>. Personal: usuario `admin`, clave `cafeteria2026` (cámbiela con `CAFETERIA_ADMIN_CLAVE` antes de la primera ejecución).

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

