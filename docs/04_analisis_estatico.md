# 5. Reporte de Análisis Estático del Código

**Proyecto:** Gestión de pedidos de una cafetería universitaria
**Versión analizada:** 1.0.0 · rama `documentacion`, commit `9a83c23` (el código de `app/` y `run.py` es idéntico al de `main`)
**Fecha de ejecución:** 20 de noviembre de 2026
**Entorno:** Python 3.14.8
**Evidencias:** carpeta [`docs/reportes/analisis_estatico/`](reportes/analisis_estatico/)

## 5.1 Propósito y alcance

El análisis estático examina el código fuente sin ejecutarlo, para detectar errores de estilo, defectos probables, vulnerabilidades conocidas y exceso de complejidad antes de las pruebas.

Se analizaron los 21 archivos Python del proyecto: los 20 módulos del paquete `app/` (1 774 líneas físicas y 1 118 líneas de código efectivo, según radon) y `run.py`. No se analizan las plantillas HTML ni la hoja de estilos, porque las herramientas usadas solo leen código Python.

## 5.2 Herramientas y configuración

| Herramienta | Versión | Qué revisa | Configuración |
|---|---|---|---|
| flake8 | 7.5.0 | Estilo PEP 8, errores de sintaxis y nombres sin uso. | `.flake8`: longitud máxima de línea 120; excluye `.git`, `__pycache__`, entornos virtuales, `instance` y `docs`. |
| pylint | 4.1.3 | Errores probables, convenciones, docstrings, diseño y código duplicado. Califica de 0 a 10. | `pyproject.toml`: longitud máxima 120; ignora `instance` y `docs`. |
| bandit | 1.9.4 | Vulnerabilidades de seguridad conocidas. | `pyproject.toml`: excluye `tests`, `docs` e `instance`. |
| radon | 6.0.1 | Complejidad ciclomática, índice de mantenibilidad y métricas de tamaño. | Por defecto. |

## 5.3 Cómo reproducir el análisis

```bash
python -m venv .venv
source .venv/Scripts/activate        # Git Bash en Windows; en Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pip install flake8==7.5.0 pylint==4.1.3 bandit==1.9.4 radon==6.0.1

D=docs/reportes/analisis_estatico
mkdir -p $D
flake8 app run.py --count --statistics > $D/flake8.txt
pylint app run.py --reports=y > $D/pylint_app.txt
bandit -r app run.py > $D/bandit.txt
radon cc app -s -a > $D/radon_complejidad.txt
radon mi app -s > $D/radon_mantenibilidad.txt
radon raw app -s > $D/radon_metricas.txt
```

Las salidas completas, junto con la versión de Python y el commit analizado (`entorno.txt`), están en `docs/reportes/analisis_estatico/`.

## 5.4 Resultados

| Herramienta | Resultado | Umbral del CI | Cumple |
|---|---|---|---|
| flake8 | 0 avisos | 0 avisos | Sí |
| pylint | 10.00 / 10, 0 mensajes | ≥ 9.0 | Sí |
| bandit | 0 hallazgos (0 bajos, 0 medios, 0 altos) | Sin hallazgos medios ni altos | Sí |
| radon (complejidad) | Promedio A (2.12) | No aplica | No aplica |

### flake8

0 avisos en los 21 archivos.

### pylint

- Nota **10.00 / 10** sobre 816 sentencias analizadas, con 0 mensajes en las categorías convención, refactorización, advertencia y error.
- Código duplicado: 0 líneas (0.000 %).
- Documentación: el 100 % de los módulos (21), clases (30), métodos (68) y funciones (59) tiene docstring.
- Nombres que incumplen la convención: 0 %.
- Dependencias externas: el código importa únicamente `flask`, `click` y `werkzeug` (solo `werkzeug.security`). `click` y `werkzeug` se instalan junto con Flask, que es la única dependencia declarada en `requirements.txt`.
- Dependencias internas: según el grafo de pylint, las capas se importan en un solo sentido, de `web` a `servicios`, de `servicios` a `persistencia` y de todas ellas a `dominio`. Ningún módulo de `dominio` importa de las capas superiores.

### bandit

Se escanearon 1 409 líneas de código: no se identificó ningún problema, en ninguna severidad ni confianza. No hay líneas omitidas con `# nosec`.

### radon: complejidad ciclomática

Se analizaron 148 bloques (clases, funciones y métodos). El promedio es **A (2.12)**. De ellos, 144 son de rango A (1 a 5), 4 de rango B (6 a 10) y ninguno de rango C o superior.

| Bloque | Archivo | Complejidad |
|---|---|---|
| `validar_cedula` | `app/dominio/validaciones.py` | B (8) |
| `PersonalServicio.registrar` | `app/servicios/personal_servicio.py` | B (8) |
| `convertir_precio_a_centavos` | `app/dominio/validaciones.py` | B (7) |
| `validar_correo_institucional` | `app/dominio/validaciones.py` | B (6) |

Las cuatro son secuencias de validaciones con rechazo anticipado: cada rama corresponde a una regla distinta (por ejemplo, formato, provincia y dígito verificador de la cédula), no a lógica entrelazada. Están dentro del rango aceptable y no requieren refactorización.

### radon: índice de mantenibilidad

Los 20 módulos analizados obtienen rango A. Los más bajos son:

| Módulo | Índice |
|---|---|
| `app/web/personal.py` | 38.32 |
| `app/web/cliente.py` | 42.56 |
| `app/persistencia/repositorios.py` | 47.70 |
| `app/web/comun.py` | 47.99 |

El índice baja con la cantidad de código y de operaciones de un módulo. Los más bajos son los que concentran las rutas web y el acceso a datos; aun así se mantienen en rango A.

### radon: tamaño

| Métrica | Valor |
|---|---|
| Líneas totales (LOC) | 1 774 |
| Líneas lógicas (LLOC) | 1 057 |
| Líneas de código fuente (SLOC) | 1 118 |
| Líneas en blanco | 361 |
| Comentarios (`#`) | 16 |
| Líneas de cadenas multilínea (incluye docstrings) | 168 |
| (Comentarios + cadenas multilínea) / LOC | 10 % |

Los módulos más grandes, por líneas de código fuente, son `persistencia/repositorios.py` (197), `servicios/pedido_servicio.py` (149) y `web/personal.py` (133).

## 5.5 Supresiones de reglas en el código

Hay tres supresiones, todas de pylint. No hay `# noqa`, `# nosec` ni `# type: ignore`.

| Ubicación | Regla suprimida | Justificación |
|---|---|---|
| `app/dominio/modelos.py` · clase `Pedido` | `too-many-instance-attributes` | La entidad tiene 8 atributos (el límite por defecto es 7) y todos son datos propios del pedido. Dividirla empeoraría la legibilidad. |
| `app/config.py` · clase `Config` | `too-few-public-methods` | Es una clase de configuración que solo agrupa valores; no necesita métodos. |
| `app/__init__.py` · función `create_app` | `import-outside-toplevel` | Patrón de fábrica de Flask: los módulos de rutas se cargan al crear la aplicación, justo antes de registrarlos. |

## 5.6 Hallazgos detectados durante el desarrollo

El código actual no tiene avisos, pero flake8 (en el CI y en local) sí detectó avisos en varios momentos de la construcción. Se corrigieron antes de integrar. Para documentarlos se ejecutó flake8 sobre el estado de cada commit, antes y después de la corrección.

| # | Fecha | Regla | Dónde | Análisis | Corrección | Re-ejecución |
|---|---|---|---|---|---|---|
| 1 | 12/11/2026 | W292 (4 avisos) | `app/dominio/__init__.py`, `excepciones.py`, `modelos.py`, `validaciones.py` | Los archivos terminaban sin salto de línea final; el editor no lo agrega al guardar. | Commit `16c64c4` | 1 aviso nuevo: W391 (línea en blanco sobrante) en `app/__init__.py` |
| 2 | 12/11/2026 | W391 (1 aviso) | `app/__init__.py` | La corrección anterior agregó una línea en blanco de más. | Commit `622e1a1` | 0 avisos |
| 3 | 17/11/2026 | W291 (2 avisos), E501 (1 aviso) | `app/servicios/pedido_servicio.py` (líneas 116 y 120) y `app/web/personal.py` (línea 98, de 123 caracteres) | Espacios al final de línea y una línea por encima del máximo de 120. | Commit `a541dfd` | 2 avisos: E128 y E501 en `personal.py` |
| 4 | 17/11/2026 | E128 (1 aviso), E501 (1 aviso) | `app/web/personal.py` (líneas 96 y 99, función de confirmación de entrega) | La corrección anterior dejó una continuación mal indentada y una línea todavía de 123 caracteres. | Commit `117717b` | 0 avisos |

## 5.7 Observaciones de la revisión manual

Estas observaciones no las reportan las herramientas:

1. **Clave inicial del personal por defecto.** En `app/config.py`, `PERSONAL_INICIAL_CLAVE` toma el valor `"cafeteria2026"` si no se define la variable de entorno `CAFETERIA_ADMIN_CLAVE`. Bandit no lo reporta porque su regla de contraseñas fijas (B105) busca nombres de variable como `password`, `pass`, `pwd`, `secret` o `token`, y esta se llama `CLAVE`. En una demostración local el riesgo es bajo y el README indica cambiarla antes de la primera ejecución. En una instalación real debe definirse la variable de entorno.
2. **Valores por defecto del servidor.** `run.py` arranca con `debug=False` y escucha en `127.0.0.1`, es decir, solo accesible desde el propio equipo, salvo que se defina `CAFETERIA_HOST`. La configuración activa la protección CSRF y marca las cookies de sesión como `HttpOnly` y `SameSite=Lax`.

## 5.8 Conclusión

- El código cumple los umbrales de calidad: flake8 sin avisos, pylint 10.00/10 y bandit sin hallazgos en ninguna severidad.
- La complejidad promedio es A (2.12) y todos los módulos tienen índice de mantenibilidad de rango A.
- Todas las clases, métodos y funciones tienen docstring, y no hay código duplicado.
- Los puntos a vigilar son las cuatro funciones de rango B (complejidad máxima 8) y los módulos con índice de mantenibilidad más bajo, que siguen en rango A.