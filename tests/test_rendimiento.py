"""Pruebas de rendimiento (RNF-07): las páginas responden en menos de 1 s con 1 000 pedidos."""

import time

import pytest

from app.persistencia.db import conectar
from app.servicios.cliente_servicio import ClienteServicio
from app.servicios.pedido_servicio import PedidoServicio

PEDIDOS = 1000
CLIENTES = 50
LIMITE_SEGUNDOS = 1.0


@pytest.fixture
def con_mil_pedidos(app, web, otro_web, registrar_cliente, ingresar_personal, cedula_valida):
    """Carga 1 000 pedidos de 50 clientes (con estados variados) y deja ambas sesiones iniciadas."""
    ana = registrar_cliente(web)
    ingresar_personal(otro_web)
    conexion = conectar(app.config["DATABASE"])
    try:
        clientes = ClienteServicio(conexion, app.config["DOMINIO_CORREO"])
        pedidos = PedidoServicio(conexion)
        ids = [clientes.identificar(ana.cedula, ana.correo).id]
        ids += [clientes.registrar("Cliente", "Prueba", cedula_valida(f"17{numero:07d}"), "0991234567",
                                   f"cliente{numero}@epn.edu.ec").id for numero in range(1, CLIENTES)]
        for numero in range(PEDIDOS):
            items = {"A01": 1 + numero % 3, "B02": 1}
            pedido = pedidos.confirmar_pedido(ids[numero % CLIENTES], items,
                                              pedidos.calcular_resumen(items).total_centavos)
            if numero % 4 == 1:
                pedidos.avanzar_estado(pedido.id, pedido.estado.siguiente(), "admin")
    finally:
        conexion.close()
    return web, otro_web


def _medir(navegador, ruta):
    inicio = time.perf_counter()
    respuesta = navegador.get(ruta)
    return respuesta, time.perf_counter() - inicio


@pytest.mark.parametrize("quien, ruta", [
    ("cliente", "/menu"),
    ("cliente", "/mis-pedidos"),
    ("cliente", "/mis-pedidos/1"),
    ("personal", "/personal/pedidos"),
    ("personal", "/personal/pedidos?estado=EN_PREPARACION"),
    ("personal", "/personal/productos"),
])
def test_cada_pagina_responde_en_menos_de_un_segundo_con_mil_pedidos(con_mil_pedidos, quien, ruta):
    cliente, personal = con_mil_pedidos
    respuesta, segundos = _medir(cliente if quien == "cliente" else personal, ruta)
    assert respuesta.status_code == 200
    assert segundos < LIMITE_SEGUNDOS, f"{ruta} tardó {segundos:.3f} s"


def test_la_lista_del_personal_muestra_todos_los_pendientes_con_mil_pedidos(con_mil_pedidos):
    _, personal = con_mil_pedidos
    html = personal.get("/personal/pedidos").get_data(as_text=True)
    assert html.count("Pedido #") == PEDIDOS * 3 // 4
