# 7. Manual de Instalación

**Proyecto:** Gestión de pedidos de una cafetería universitaria\
**Versión:** 1.0.0\
**Destinatario:** responsable técnico que instala y mantiene el sistema en la cafetería.

Este manual explica cómo instalar, configurar, ejecutar y mantener el sistema de pedidos en un computador con Windows, macOS o Linux. El uso diario por parte de clientes y personal se describe en el *Manual de Usuario* (documento 8).

## 7.1 Resumen rápido

Para quien ya tiene Python 3.11 o superior y Git:

```bash
git clone https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1.git
cd Proyecto_1B_EvolucionSW_Equipo-1
python -m venv .venv
source .venv/Scripts/activate      # Git Bash en Windows · PowerShell: .venv\Scripts\Activate.ps1 · macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Abra <http://127.0.0.1:5000>. Personal: usuario `admin`, clave `cafeteria2026`. Las secciones siguientes explican cada paso.

## 7.2 Requisitos

| Elemento | Requisito |
|---|---|
| Sistema operativo | Windows 10/11, macOS 12 o superior, o Linux con Python disponible. |
| Python | **3.11 o superior** (la integración continua lo prueba en 3.11, 3.12 y 3.13). Incluye SQLite, por lo que no hace falta instalar un servidor de base de datos. |
| Git | Cualquier versión reciente. Es opcional: también se puede descargar el ZIP desde GitHub. |
| Espacio en disco | Unos 50 MB con las dependencias de ejecución. |
| Navegador | Chrome, Edge, Firefox o Safari actualizados, en computador o celular. |
| Red | Solo para descargar el código y las dependencias. La aplicación funciona sin Internet. |

Para verificar la versión de Python, abra una terminal y ejecute:

```bash
python --version        # en macOS/Linux puede ser: python3 --version · en Windows también: py --version
```

Si no está instalado, descárguelo de <https://www.python.org/downloads/>. En Windows marque la casilla **«Add python.exe to PATH»** durante la instalación.

## 7.3 Obtener el código

```bash
git clone https://github.com/g-cevallos/Proyecto_1B_EvolucionSW_Equipo-1.git
cd Proyecto_1B_EvolucionSW_Equipo-1
```

La rama `main` contiene la versión estable, que es la que se debe instalar en la cafetería. Sin Git: en GitHub pulse **Code → Download ZIP**, descomprima el archivo y abra una terminal dentro de la carpeta descomprimida.

## 7.4 Crear el entorno virtual e instalar las dependencias

El entorno virtual mantiene las dependencias del sistema separadas de las demás instalaciones de Python del equipo. Ejecute los tres comandos de su terminal:

| Terminal | Comandos |
|---|---|
| Windows · PowerShell | `python -m venv .venv` · `.venv\Scripts\Activate.ps1` · `pip install -r requirements.txt` |
| Windows · Git Bash | `python -m venv .venv` · `source .venv/Scripts/activate` · `pip install -r requirements.txt` |
| macOS / Linux | `python3 -m venv .venv` · `source .venv/bin/activate` · `pip install -r requirements.txt` |

Cuando el entorno está activo, la línea de la terminal empieza con `(.venv)`. Hay que activarlo cada vez que se abre una terminal nueva para ejecutar el sistema; la creación y la instalación se hacen una sola vez.

> Si PowerShell indica que la ejecución de scripts está deshabilitada, ejecute una vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y repita la activación.

## 7.5 Configuración (opcional)

El sistema funciona sin configurar nada. Para adaptarlo se usan variables de entorno, que se leen cada vez que arranca la aplicación:

| Variable | Valor por defecto | Para qué sirve |
|---|---|---|
| `CAFETERIA_DOMINIO_CORREO` | `epn.edu.ec` | Dominio aceptado para el correo institucional de los clientes. |
| `CAFETERIA_ADMIN_USUARIO` | `admin` | Usuario del personal que se crea en la **primera** ejecución. |
| `CAFETERIA_ADMIN_CLAVE` | `cafeteria2026` | Clave de ese usuario (mínimo 8 caracteres). **Cámbiela en una instalación real.** |
| `CAFETERIA_DATOS_DEMO` | `1` | `1` carga 9 productos de ejemplo si el menú está vacío; `0` inicia con el menú vacío. |
| `CAFETERIA_CANTIDAD_MAXIMA` | `50` | Unidades máximas de un producto en un pedido. |
| `CAFETERIA_DB` | `instance/cafeteria.db` | Ruta del archivo de base de datos. |
| `CAFETERIA_HOST` / `CAFETERIA_PUERTO` | `127.0.0.1` / `5000` | Dirección y puerto en que escucha el servidor. |
| `CAFETERIA_SECRET_KEY` | se genera sola | Clave que firma las sesiones. Si no se define, se crea y se guarda en `instance/secret_key`. |

**Importante:** el usuario inicial del personal y el menú de ejemplo solo se crean cuando todavía no existen. Por eso `CAFETERIA_ADMIN_USUARIO`, `CAFETERIA_ADMIN_CLAVE` y `CAFETERIA_DATOS_DEMO` deben definirse **antes de la primera ejecución**; cambiarlos después no modifica los datos ya creados. Las demás variables pueden cambiarse en cualquier momento reiniciando la aplicación.

Ejemplos (las variables valen solo para la terminal en que se definen):

```powershell
# Windows · PowerShell
$env:CAFETERIA_ADMIN_CLAVE = "UnaClaveSegura2026"
$env:CAFETERIA_DATOS_DEMO = "0"
```

```bash
# Git Bash, macOS o Linux
export CAFETERIA_ADMIN_CLAVE=UnaClaveSegura2026
export CAFETERIA_DATOS_DEMO=0
```

## 7.6 Ejecutar y verificar la instalación

Con el entorno virtual activo:

```bash
python run.py
```

En la primera ejecución se crean automáticamente la carpeta `instance/`, la base de datos `instance/cafeteria.db`, la clave de sesiones `instance/secret_key`, el usuario del personal y, si corresponde, el menú de ejemplo. Para detener el servidor pulse `Ctrl + C` en la terminal; los datos se conservan para la próxima ejecución.

Compruebe que la instalación funciona:

1. Abra <http://127.0.0.1:5000>: debe aparecer la página de inicio con los accesos «Soy estudiante o docente» y «Trabajo en la cafetería».
2. Pulse **Ver el menú**: con los datos de ejemplo se ven 8 productos disponibles, agrupados en «Para comer» y «Para tomar».
3. Pulse **Entrar como personal** e ingrese con `admin` y la clave configurada (por defecto `cafeteria2026`): debe abrirse la sección **Pedidos**.

## 7.7 Uso en la red local de la cafetería

Por defecto el sistema solo acepta conexiones del propio computador (`127.0.0.1`). Para que los clientes pidan desde sus celulares conectados a la misma red Wi-Fi, inícielo escuchando en todas las interfaces:

```powershell
# Windows · PowerShell
$env:CAFETERIA_HOST = "0.0.0.0"; python run.py
```

```bash
# Git Bash, macOS o Linux
CAFETERIA_HOST=0.0.0.0 python run.py
```

Averigüe la IP del equipo (`ipconfig` en Windows; `ip addr` o `ifconfig` en macOS/Linux) y comparta la dirección `http://<IP>:5000`, por ejemplo `http://192.168.1.20:5000`. Si Windows lo pregunta, permita el acceso de Python en el firewall para **redes privadas**.

El servidor que trae Flask está pensado para desarrollo. Para un uso continuo durante la jornada se recomienda Waitress, un servidor de producción para Python que funciona también en Windows. No está en `requirements.txt`, por lo que se instala aparte:

```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 run:app
```

**Seguridad:** el sistema se comunica por HTTP sin cifrar, lo que es adecuado para la red interna de la cafetería pero no para publicarlo en Internet. Cambie la clave del usuario inicial antes de abrir el sistema a los clientes.

## 7.8 Administración

| Tarea | Cómo hacerlo |
|---|---|
| Crear otro usuario del personal | Con el entorno activo: `flask --app run crear-personal maria "María López"`. Pide la clave dos veces; debe tener al menos 8 caracteres, o el comando la rechaza. |
| Respaldar los datos | Con la aplicación detenida, copie la carpeta `instance/` completa (base de datos y clave de sesiones) a otro lugar. |
| Restaurar un respaldo | Detenga la aplicación y reemplace la carpeta `instance/` por la copia. |
| Empezar con datos limpios | Detenga la aplicación y elimine `instance/cafeteria.db`; se recreará vacía, con el usuario inicial y, si corresponde, el menú de ejemplo, en la siguiente ejecución. **Se pierden todos los pedidos y clientes.** |
| Actualizar a una nueva versión | Detenga la aplicación, ejecute `git pull` y luego `pip install -r requirements.txt`. La carpeta `instance/` y sus datos se conservan. |
| Desinstalar | Detenga la aplicación y elimine la carpeta del proyecto. Respalde antes `instance/` si quiere conservar los datos. |

Los productos del menú no se eliminan: se desactivan desde la sección **Menú** del personal (ver *Manual de Usuario*, sección 8.3.4).

## 7.9 Instalación para desarrollo y verificación

Para ejecutar las pruebas automáticas se instalan además las dependencias de desarrollo:

```bash
pip install -r requirements-dev.txt
pytest --cov=app --cov-branch --cov-fail-under=85
```

Todas las pruebas deben pasar y la cobertura debe ser de al menos 85 %, el mismo criterio que aplica la integración continua. Al 22 de noviembre de 2026 la suite tiene 452 pruebas, con una cobertura de 99,9 %.

Los comandos de análisis estático (flake8, pylint y bandit) están en la *Documentación del Ambiente de Desarrollo*, sección 3.6.

## 7.10 Solución de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `python` no se reconoce como comando | Python no está en el PATH. | Reinstale marcando «Add python.exe to PATH», o use `py` en Windows. |
| `pip` no se reconoce como comando | El entorno virtual no está activo. | Active `.venv` (sección 7.4) o use `python -m pip install -r requirements.txt`. |
| `ModuleNotFoundError: No module named 'flask'` | El entorno virtual no está activo o no se instalaron las dependencias. | Active `.venv` (sección 7.4), ejecute `pip install -r requirements.txt` y vuelva a intentar. |
| `Address already in use` o puerto ocupado | Otro programa usa el puerto 5000. | Defina `CAFETERIA_PUERTO=5001` (u otro). En macOS el puerto 5000 puede estar ocupado por *AirPlay Receiver*. |
| `sqlite3.OperationalError: no such table: json_each` | Python con una versión antigua de SQLite. | Instale Python 3.11 o superior desde python.org. |
| «El formulario expiró» al enviar un formulario | La sesión ya no es válida (se borraron las cookies o se cambió la clave de sesiones). | Recargue la página y envíe el formulario de nuevo. |
| «Usuario o clave incorrectos» con `admin` | La clave se definió con `CAFETERIA_ADMIN_CLAVE` en la primera ejecución. | Use esa clave o cree otro usuario con `crear-personal` (sección 7.8). |
| El menú aparece vacío | Se inició con `CAFETERIA_DATOS_DEMO=0`, o se desactivaron todos los productos. | Agregue o active productos desde la sección **Menú** del personal. |
| Los celulares no abren la página | El servidor escucha solo en `127.0.0.1`, o el firewall bloquea Python. | Inicie con `CAFETERIA_HOST=0.0.0.0` (sección 7.7) y permita Python en el firewall para redes privadas. |
