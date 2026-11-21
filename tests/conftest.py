"""Fixtures y utilidades compartidas por todas las pruebas automáticas.

Las pruebas de servicios usan una base SQLite en memoria; las pruebas web crean la
aplicación con una base en un archivo temporal, de modo que ninguna prueba toca
datos reales ni depende de variables de entorno.
"""

import re
from itertools import count
from types import SimpleNamespace

import pytest

from app import create_app
from app.persistencia.db import conectar, crear_esquema
from app.servicios.cliente_servicio import ClienteServicio
from app.servicios.menu_servicio import MenuServicio
from app.servicios.pedido_servicio import PedidoServicio

DOMINIO = "epn.edu.ec"
CLAVE_PERSONAL = "clave-de-pruebas"


def con_verificador(nueve_digitos: str) -> str:
    """Completa una cédula ecuatoriana con su dígito verificador (módulo 10)."""
    suma = 0
    for posicion, caracter in enumerate(nueve_digitos):
        valor = int(caracter) * (2 if posicion % 2 == 0 else 1)
        suma += valor - 9 if valor > 9 else valor
    return nueve_digitos + str((10 - suma % 10) % 10)


@pytest.fixture
def cedula_valida():
    """Función que devuelve una cédula válida a partir de sus primeros nueve dígitos."""
    return con_verificador


@pytest.fixture(autouse=True)
def instancia_temporal(tmp_path, monkeypatch):
    """Redirige la carpeta `instance` de Flask a una temporal: las pruebas no escriben en el proyecto."""
    carpeta = tmp_path / "instance"
    monkeypatch.setattr("flask.app.Flask.auto_find_instance_path", lambda self: str(carpeta))
    return carpeta


# --------------------------------------------------------------------- servicios
@pytest.fixture
def conexion():
    """Base de datos SQLite en memoria con el esquema creado."""
    con = conectar(":memory:")
    crear_esquema(con)
    yield con
    con.close()


@pytest.fixture
def reloj():
    """Reloj determinista: cada llamada devuelve un segundo más tarde."""
    segundos = count()
    return lambda: f"2026-01-01 10:00:{next(segundos):02d}"


@pytest.fixture
def menu(conexion):
    """Servicio de menú sobre la base en memoria."""
    return MenuServicio(conexion)


@pytest.fixture
def clientes(conexion):
    """Servicio de clientes con el dominio institucional de pruebas."""
    return ClienteServicio(conexion, DOMINIO)


@pytest.fixture
def pedidos(conexion, reloj):
    """Servicio de pedidos con cantidad máxima 50 y reloj determinista."""
    return PedidoServicio(conexion, cantidad_maxima=50, reloj=reloj)


@pytest.fixture
def catalogo(menu):
    """Cuatro productos: dos bebidas y un alimento disponibles, y un alimento no disponible."""
    menu.registrar_producto("CAF1", "Café pasado", "BEBIDA", "1.50", True)
    menu.registrar_producto("SAN1", "Sánduche de pollo", "ALIMENTO", "2.50", True)
    menu.registrar_producto("AGU1", "Agua sin gas", "BEBIDA", "0.75", True)
    menu.registrar_producto("ALM1", "Almuerzo del día", "ALIMENTO", "3.50", False)
    return menu


@pytest.fixture
def cliente(clientes, cedula_valida):
    """Cliente registrado."""
    return clientes.registrar("Ana", "Torres", cedula_valida("171003406"), "0991234567", "ana@epn.edu.ec")


@pytest.fixture
def otro_cliente(clientes, cedula_valida):
    """Segundo cliente registrado, distinto del anterior."""
    return clientes.registrar("Luis", "Mora", cedula_valida("171003407"), "0987654321", "luis@epn.edu.ec")


@pytest.fixture
def pedido(catalogo, pedidos, cliente):
    """Pedido Pendiente de 2 cafés y 1 sánduche (total $5.50)."""
    return pedidos.confirmar_pedido(cliente.id, {"CAF1": 2, "SAN1": 1}, 550)


# --------------------------------------------------------------------------- web
@pytest.fixture
def app(tmp_path):
    """Aplicación Flask con base temporal, menú de demostración y usuario `admin`."""
    return create_app({
        "DATABASE": str(tmp_path / "pruebas.db"),
        "SECRET_KEY": "clave-solo-para-pruebas",
        "TESTING": True,
        "CARGAR_DATOS_DEMO": True,
        "PERSONAL_INICIAL_USUARIO": "admin",
        "PERSONAL_INICIAL_CLAVE": CLAVE_PERSONAL,
        "DOMINIO_CORREO": DOMINIO,
        "CANTIDAD_MAXIMA": 50,
    })


@pytest.fixture
def clave_personal():
    """Clave del usuario inicial `admin` que crean las pruebas web."""
    return CLAVE_PERSONAL


@pytest.fixture
def web(app):
    """Navegador simulado (conserva cookies de sesión entre peticiones)."""
    return app.test_client()


@pytest.fixture
def otro_web(app):
    """Segundo navegador simulado, con su propia sesión."""
    return app.test_client()


@pytest.fixture
def csrf():
    """Función que obtiene el token CSRF de la sesión de un navegador simulado."""
    def obtener(navegador):
        html = navegador.get("/ingresar").get_data(as_text=True)
        return re.search(r'name="csrf" value="([^"]+)"', html).group(1)
    return obtener


@pytest.fixture
def enviar(csrf):
    """Función que envía un formulario POST agregando el token CSRF válido."""
    def _enviar(navegador, ruta, datos=None, **opciones):
        cuerpo = {"csrf": csrf(navegador)}
        cuerpo.update(datos or {})
        return navegador.post(ruta, data=cuerpo, **opciones)
    return _enviar


@pytest.fixture
def registrar_cliente(enviar, cedula_valida):
    """Función que registra un cliente desde la web y deja su sesión iniciada."""
    def _registrar(navegador, nombre="Ana", prefijo="171003406", correo="ana@epn.edu.ec"):
        cedula = cedula_valida(prefijo)
        respuesta = enviar(navegador, "/registro", {
            "nombre": nombre, "apellido": "Torres", "cedula": cedula,
            "celular": "0991234567", "correo": correo,
        })
        assert respuesta.status_code == 302, respuesta.get_data(as_text=True)
        return SimpleNamespace(cedula=cedula, correo=correo)
    return _registrar


@pytest.fixture
def ingresar_personal(enviar):
    """Función que inicia la sesión del personal."""
    def _ingresar(navegador, usuario="admin", clave=CLAVE_PERSONAL):
        return enviar(navegador, "/personal/ingresar", {"usuario": usuario, "clave": clave})
    return _ingresar


@pytest.fixture
def hacer_pedido(enviar):
    """Función que revisa y confirma un pedido desde la web (el cliente ya debe haber ingresado)."""
    def _hacer(navegador, cantidades):
        datos = {f"cant_{codigo}": str(cantidad) for codigo, cantidad in cantidades.items()}
        revision = enviar(navegador, "/pedido/revisar", datos)
        assert revision.status_code == 200, revision.get_data(as_text=True)
        total = re.search(r'name="total_mostrado" value="(\d+)"', revision.get_data(as_text=True)).group(1)
        confirmacion = enviar(navegador, "/pedido/confirmar", {"total_mostrado": total})
        assert confirmacion.status_code == 302
        pedido_id = int(re.search(r"/mis-pedidos/(\d+)", confirmacion.headers["Location"]).group(1))
        detalle = navegador.get(f"/mis-pedidos/{pedido_id}").get_data(as_text=True)
        codigo = re.search(r'id="codigo-retiro">([A-Z0-9]+)<', detalle).group(1)
        return SimpleNamespace(id=pedido_id, codigo=codigo, total=int(total))
    return _hacer
