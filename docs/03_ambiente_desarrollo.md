# 3. Documentación del Ambiente de Desarrollo

## 3.1 Herramientas seleccionadas

| Propósito | Herramienta | Versión | Motivo de la elección |
|---|---|---|---|
| Lenguaje | Python | 3.11 o superior (probado en 3.13.14) | Sintaxis clara, biblioteca estándar con SQLite incluido. |
| Framework web | Flask | 3.1.3 | Microframework con blueprints, plantillas Jinja2 y cliente de pruebas integrado. |
| Base de datos | SQLite (módulo `sqlite3`) | 3.50.4 (incluida en Python) | Persistencia en archivo sin instalar un servidor. |
| Editor / IDE | Visual Studio Code + extensiones *Python*, *Pylint*, *Flake8*, *Markdown Preview Mermaid Support* | — | Gratuito, multiplataforma, integra análisis y depuración. |
| Control de versiones | Git + GitHub | Git ≥ 2.40 | Requerido por la cátedra; revisiones mediante *pull requests*. |
| Integración continua | GitHub Actions (`.github/workflows/ci.yml`) | — | Ejecuta pruebas y análisis en cada *push* y *pull request*. |
| Pruebas | pytest | 9.2.0 | Fixtures, parametrización y reportes JUnit. |
| Cobertura | pytest-cov (coverage.py) | 7.1.0 | Cobertura de líneas y ramas, reporte HTML. |
| Análisis estático | pylint · flake8 · bandit · radon | 4.1.3 · 7.5.0 · 1.9.4 · 6.0.1 | Estilo y errores; PEP 8; seguridad; complejidad y mantenibilidad. |
| Documentación técnica | pdoc | 16.0.0 | Genera HTML a partir de los *docstrings* (equivalente a JavaDoc). |
| Pruebas de sistema y capturas | Playwright (Chromium) | 1.56.0 | Recorre la aplicación en un navegador real y genera las capturas del manual. |
| Diagramas | Mermaid (en Markdown) | — | GitHub los dibuja directamente; quedan versionados como texto. |

Las dependencias están fijadas en `requirements.txt` (ejecución) y `requirements-dev.txt` (desarrollo).

## 3.2 Estructura del repositorio

```text
Proyecto_1B_EvolucionSW_Equipo-1/
├── app/
│   ├── __init__.py            # create_app(): arranque y configuración
│   ├── config.py              # variables de entorno
│   ├── datos_demo.py          # menú de ejemplo
│   ├── dominio/               # modelos, validaciones, excepciones
│   ├── persistencia/          # esquema SQLite y repositorios
│   ├── servicios/             # casos de uso y reglas de negocio
│   └── web/                   # blueprints, plantillas y estilos
├── tests/                     # pruebas pytest (CP-01 a CP-47)
├── scripts/capturas.py        # prueba de sistema con navegador y capturas
├── docs/                      # solo en la rama documentacion
├── .github/workflows/ci.yml   # integración continua
├── run.py                     # punto de entrada
├── requirements.txt / requirements-dev.txt
├── pyproject.toml / .flake8   # configuración de herramientas
└── README.md
```

## 3.3 Estrategia de ramificación

El equipo trabaja con **tres ramas permanentes**. No se crean ramas temporales: cada integrante trabaja directamente sobre la rama que corresponde al tipo de cambio.

| Rama | Se crea desde | Se integra en | Contenido |
|---|---|---|---|
| `main` | — | — | Solo versiones estables y etiquetadas (`v1.0.0`). Nadie hace *push* directo; recibe cambios únicamente desde `develop`. |
| `develop` | `main` | `main` (al liberar) | Rama de trabajo del código: aquí se programan las historias de usuario, las pruebas y las correcciones. |
| `documentacion` | `main` | — | Código estable + carpeta `docs/` con los entregables. Es la única rama donde existe `docs/`. |

```mermaid
gitGraph
    commit id: "estructura inicial"
    branch documentacion
    checkout documentacion
    commit id: "docs: requisitos"
    commit id: "docs: diseño"
    commit id: "docs: ambiente"
    checkout main
    branch develop
    checkout develop
    commit id: "dominio y validaciones"
    commit id: "esquema y repositorios"
    commit id: "servicios"
    commit id: "interfaz web"
    commit id: "pruebas CP-01..CP-47"
    commit id: "integración continua"
    checkout main
    merge develop tag: "v1.0.0"
    checkout documentacion
    merge main
    commit id: "docs 4-8"
```

### Reglas del flujo

1. **Cada cambio va a su rama**: código, pruebas y configuración en `develop`; documentos de la carpeta `docs/` en `documentacion`. Nunca se sube documentación a `develop` ni código nuevo a `documentacion`.
2. **Mensajes de commit** con la convención *Conventional Commits* en español: `feat(pedidos): genera código de retiro único`, `fix(web): …`, `test: …`, `docs: …`, `refactor: …`, `chore: …`. Un commit = un cambio coherente, hecho por quien realizó el aporte, para que quede constancia del trabajo de cada integrante.
3. **Actualizar antes de trabajar** (`git pull`) para evitar conflictos entre integrantes que trabajan en la misma rama.
4. **`main` solo recibe desde `develop`** mediante *pull request* con al menos **una revisión aprobada** de otro integrante y la integración continua en verde, integrado con `--no-ff`.
5. **Versionado semántico**: `vMAYOR.MENOR.PARCHE`; el Release 1.0 es `v1.0.0`.
6. **Protección de `main`** en GitHub (*Settings → Branches → Branch protection rules*): exigir PR, revisión y CI aprobada.

## 3.4 Flujo de trabajo diario

Trabajo en código:

```bash
git switch develop && git pull                     # 1. partir de develop actualizado
# … programar + pruebas …
pytest && flake8 app tests && pylint app           # 2. verificar localmente
git add -A && git commit -m "feat(pedidos): consulta de estado por el cliente"
git push                                           # 3. publicar en develop
```

Trabajo en documentación:

```bash
git switch documentacion && git pull               # 1. partir de documentacion actualizada
# … editar archivos en docs/ …
git add docs && git commit -m "docs: documento de ambiente de desarrollo"
git push                                           # 2. publicar en documentacion
```

Para liberar: PR de `develop` a `main`, revisar, integrar, etiquetar (`git tag -a v1.0.0 -m "Release 1.0"`, `git push --tags`) y actualizar `documentacion` desde `main` (`git switch documentacion && git merge main`).

## 3.5 Definición de terminado

Una historia está terminada cuando: cumple todos sus criterios de aceptación; tiene pruebas automatizadas que los cubren y pasan; pylint ≥ 9.0, flake8 sin avisos y bandit sin hallazgos de severidad media o alta; las funciones públicas tienen *docstring*; está publicada en `develop` con la integración continua en verde; y el manual de usuario refleja cualquier cambio visible.

## 3.6 Preparación del entorno

```bash
git clone https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1.git
cd Proyecto_1B_EvolucionSW_Equipo-1
python -m venv .venv
# Windows: .venv\Scripts\activate      Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
python -m playwright install chromium     # solo para scripts/capturas.py
```

### Comandos de calidad

| Tarea | Comando |
|---|---|
| Ejecutar la aplicación | `python run.py` |
| Pruebas | `pytest` |
| Pruebas con cobertura | `pytest --cov=app --cov-branch --cov-report=html` |
| Estilo PEP 8 | `flake8 app tests scripts run.py` |
| Análisis completo | `pylint app run.py scripts` y `pylint tests` |
| Seguridad | `bandit -r app run.py` |
| Complejidad | `radon cc app -s -a` · `radon mi app -s` |
| Documentación técnica | `pdoc app -o docs/api --docformat google` |
| Prueba de sistema y capturas | `python scripts/capturas.py docs/img` |

## 3.7 Integración continua

`.github/workflows/ci.yml` se ejecuta en cada *push* a `main`, `develop` y `documentacion` y en cada *pull request*. Instala Python 3.11 y 3.12, y ejecuta flake8, pylint (falla bajo 9.0), bandit y pytest con cobertura (falla bajo 85 %). El reporte de cobertura queda como artefacto descargable del flujo.
