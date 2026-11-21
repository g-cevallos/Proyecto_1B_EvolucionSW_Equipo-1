"""Pruebas de la web del cliente: registro, ingreso, menú, pedido y seguimiento."""

import re

import pytest


def _texto(respuesta):
    return respuesta.get_data(as_text=True)


# ---------------------------------------------------------------------------- registro
def test_el_formulario_de_registro_se_muestra(web):
    respuesta = web.get("/registro")
    assert respuesta.status_code == 200
    for campo in ("nombre", "apellido", "cedula", "celular", "correo"):
        assert f'name="{campo}"' in _texto(respuesta)


def test_un_registro_correcto_inicia_la_sesion_y_lleva_al_menu(web, enviar, cedula_valida):
    respuesta = enviar(web, "/registro", {
        "nombre": "Ana", "apellido": "Torres", "cedula": cedula_valida("171003406"),
        "celular": "0991234567", "correo": "ana@epn.edu.ec"}, follow_redirects=True)
    assert respuesta.request.path == "/menu"
    assert "CLI-00001" in _texto(respuesta)
    assert web.get("/mis-pedidos").status_code == 200


def test_un_registro_invalido_se_rechaza_y_conserva_lo_escrito(web, enviar):
    respuesta = enviar(web, "/registro", {
        "nombre": "Ana", "apellido": "Torres", "cedula": "123", "celular": "0991234567",
        "correo": "ana@epn.edu.ec"})
    assert respuesta.status_code == 422
    assert 'value="Ana"' in _texto(respuesta)
    assert web.get("/mis-pedidos").status_code == 302


def test_no_se_puede_registrar_dos_veces_la_misma_persona(web, otro_web, enviar, registrar_cliente, cedula_valida):
    registrar_cliente(web)
    respuesta = enviar(otro_web, "/registro", {
        "nombre": "Ana", "apellido": "Torres", "cedula": cedula_valida("171003406"),
        "celular": "0991234567", "correo": "otro@epn.edu.ec"})
    assert respuesta.status_code == 422
    assert "cédula" in _texto(respuesta)


# ------------------------------------------------------------------------------ ingreso
def test_un_cliente_registrado_ingresa_con_cedula_y_correo(web, otro_web, enviar, registrar_cliente):
    cliente = registrar_cliente(web)
    respuesta = enviar(otro_web, "/ingresar", {"cedula": cliente.cedula, "correo": cliente.correo})
    assert respuesta.status_code == 302 and respuesta.headers["Location"] == "/menu"
    assert otro_web.get("/mis-pedidos").status_code == 200


@pytest.mark.parametrize("cedula, correo", [
    ("1710034065", "otro@epn.edu.ec"), ("", ""), ("0100000009", "ana@epn.edu.ec")])
def test_datos_que_no_corresponden_no_inician_sesion(web, otro_web, enviar, registrar_cliente, cedula, correo):
    registrar_cliente(web)
    respuesta = enviar(otro_web, "/ingresar", {"cedula": cedula, "correo": correo})
    assert respuesta.status_code == 401
    assert "no corresponden" in _texto(respuesta)
    assert otro_web.get("/mis-pedidos").status_code == 302


def test_despues_de_identificarse_vuelve_a_la_pagina_que_se_pidio(web, otro_web, enviar, registrar_cliente):
    cliente = registrar_cliente(web)
    destino = otro_web.get("/mis-pedidos").headers["Location"]
    respuesta = enviar(otro_web, destino, {"cedula": cliente.cedula, "correo": cliente.correo})
    assert respuesta.headers["Location"] == "/mis-pedidos"


def test_salir_cierra_la_sesion_del_cliente(web, enviar, registrar_cliente):
    registrar_cliente(web)
    assert enviar(web, "/salir").status_code == 302
    assert web.get("/mis-pedidos").status_code == 302


# --------------------------------------------------------------------------------- menú
def test_el_menu_es_publico_y_muestra_solo_productos_disponibles_con_precio(web):
    texto = _texto(web.get("/menu"))
    assert "Café pasado" in texto and "$1.00" in texto
    assert "Almuerzo del día" not in texto


def test_un_producto_que_el_personal_desactiva_desaparece_del_menu(web, otro_web, enviar, ingresar_personal):
    ingresar_personal(otro_web)
    enviar(otro_web, "/personal/productos/B01/disponibilidad", {"disponible": "0"})
    assert "Café pasado" not in _texto(web.get("/menu"))


# -------------------------------------------------------------------------------- pedido
def test_revisar_sin_haberse_identificado_pide_ingresar(web, enviar):
    respuesta = enviar(web, "/pedido/revisar", {"cant_B01": "1"})
    assert respuesta.status_code == 302 and "/ingresar" in respuesta.headers["Location"]


def test_la_revision_muestra_el_detalle_y_el_total(web, enviar, registrar_cliente):
    registrar_cliente(web)
    respuesta = enviar(web, "/pedido/revisar", {"cant_B01": "2", "cant_A01": "1", "cant_B02": ""})
    texto = _texto(respuesta)
    assert respuesta.status_code == 200
    assert "$4.50" in texto
    assert 'name="total_mostrado" value="450"' in texto


def test_una_revision_sin_productos_vuelve_al_menu_con_un_aviso(web, enviar, registrar_cliente):
    registrar_cliente(web)
    respuesta = enviar(web, "/pedido/revisar", {"cant_B01": "0"})
    assert respuesta.status_code == 422
    assert "al menos un producto" in _texto(respuesta)


@pytest.mark.parametrize("cantidad, mensaje", [("-1", "entero positivo"), ("x", "entero positivo"), ("51", "máxima")])
def test_una_cantidad_invalida_se_informa_y_se_conserva_lo_escrito(web, enviar, registrar_cliente, cantidad, mensaje):
    registrar_cliente(web)
    respuesta = enviar(web, "/pedido/revisar", {"cant_B01": cantidad})
    assert respuesta.status_code == 422
    assert mensaje in _texto(respuesta)


def test_un_producto_no_disponible_no_se_puede_pedir(web, enviar, registrar_cliente):
    registrar_cliente(web)
    respuesta = enviar(web, "/pedido/revisar", {"cant_A05": "1"})
    assert respuesta.status_code == 422
    assert "Almuerzo del día" in _texto(respuesta)


def test_confirmar_un_pedido_muestra_el_codigo_de_retiro_y_el_estado_pendiente(web, enviar, registrar_cliente):
    registrar_cliente(web)
    enviar(web, "/pedido/revisar", {"cant_B01": "2", "cant_A01": "1"})
    respuesta = enviar(web, "/pedido/confirmar", {"total_mostrado": "450"}, follow_redirects=True)
    texto = _texto(respuesta)
    assert re.search(r'id="codigo-retiro">[A-Z0-9]{6}<', texto)
    assert "Pendiente" in texto and "$4.50" in texto


def test_el_carrito_se_vacia_despues_de_confirmar(web, enviar, registrar_cliente):
    registrar_cliente(web)
    enviar(web, "/pedido/revisar", {"cant_B01": "1"})
    enviar(web, "/pedido/confirmar", {"total_mostrado": "100"})
    respuesta = enviar(web, "/pedido/confirmar", {"total_mostrado": "100"})
    assert respuesta.status_code == 302 and respuesta.headers["Location"].endswith("/menu")
    assert len(re.findall(r"/mis-pedidos/\d+", _texto(web.get("/mis-pedidos")))) == 1


def test_un_total_distinto_al_mostrado_no_registra_el_pedido(web, enviar, registrar_cliente):
    registrar_cliente(web)
    enviar(web, "/pedido/revisar", {"cant_B01": "1"})
    respuesta = enviar(web, "/pedido/confirmar", {"total_mostrado": "999"})
    assert respuesta.status_code == 409
    assert "$1.00" in _texto(respuesta)
    assert "/mis-pedidos/" not in _texto(web.get("/mis-pedidos"))


def test_un_total_ausente_o_no_numerico_no_registra_el_pedido(web, enviar, registrar_cliente):
    registrar_cliente(web)
    enviar(web, "/pedido/revisar", {"cant_B01": "1"})
    assert enviar(web, "/pedido/confirmar", {"total_mostrado": "abc"}).status_code == 409
    assert enviar(web, "/pedido/confirmar", {}).status_code == 409


def test_si_el_precio_cambia_durante_la_revision_se_pide_confirmar_de_nuevo(
        web, otro_web, enviar, registrar_cliente, ingresar_personal):
    registrar_cliente(web)
    enviar(web, "/pedido/revisar", {"cant_B01": "2"})
    ingresar_personal(otro_web)
    enviar(otro_web, "/personal/productos/B01/editar", {
        "nombre": "Café pasado", "categoria": "BEBIDA", "precio": "1.50", "disponible": "1"})
    respuesta = enviar(web, "/pedido/confirmar", {"total_mostrado": "200"})
    assert respuesta.status_code == 409
    assert "$3.00" in _texto(respuesta)


def test_si_el_producto_deja_de_estar_disponible_al_confirmar_el_pedido_no_se_registra(
        web, otro_web, enviar, registrar_cliente, ingresar_personal):
    registrar_cliente(web)
    enviar(web, "/pedido/revisar", {"cant_B01": "1"})
    ingresar_personal(otro_web)
    enviar(otro_web, "/personal/productos/B01/disponibilidad", {"disponible": "0"})
    respuesta = enviar(web, "/pedido/confirmar", {"total_mostrado": "100"}, follow_redirects=True)
    assert "El pedido no se confirmó" in _texto(respuesta)
    assert respuesta.request.path == "/menu"


# ------------------------------------------------------------------------ seguimiento
def test_el_cliente_ve_sus_pedidos_y_su_estado(web, registrar_cliente, hacer_pedido):
    registrar_cliente(web)
    pedido = hacer_pedido(web, {"B01": 1})
    texto = _texto(web.get("/mis-pedidos"))
    assert f"/mis-pedidos/{pedido.id}" in texto and "Pendiente" in texto


def test_un_cliente_sin_pedidos_ve_la_lista_vacia(web, registrar_cliente):
    registrar_cliente(web)
    respuesta = web.get("/mis-pedidos")
    assert respuesta.status_code == 200
    assert "/mis-pedidos/" not in _texto(respuesta)


def test_un_cliente_no_ve_los_pedidos_de_otro(web, otro_web, registrar_cliente, hacer_pedido):
    registrar_cliente(web)
    pedido = hacer_pedido(web, {"B01": 1})
    registrar_cliente(otro_web, "Luis", "171003407", "luis@epn.edu.ec")
    assert f"/mis-pedidos/{pedido.id}" not in _texto(otro_web.get("/mis-pedidos"))
    respuesta = otro_web.get(f"/mis-pedidos/{pedido.id}")
    assert respuesta.status_code == 400
    assert pedido.codigo not in _texto(respuesta)


def test_el_cliente_ve_el_avance_de_su_pedido_cuando_el_personal_lo_atiende(
        web, otro_web, enviar, registrar_cliente, hacer_pedido, ingresar_personal):
    registrar_cliente(web)
    pedido = hacer_pedido(web, {"B01": 1})
    ingresar_personal(otro_web)
    enviar(otro_web, f"/personal/pedidos/{pedido.id}/avanzar", {"estado_nuevo": "EN_PREPARACION"})
    assert "En preparación" in _texto(web.get(f"/mis-pedidos/{pedido.id}"))


def test_cada_pedido_queda_a_nombre_del_cliente_que_lo_hizo(web, otro_web, registrar_cliente, hacer_pedido):
    registrar_cliente(web)
    registrar_cliente(otro_web, "Luis", "171003407", "luis@epn.edu.ec")
    pedido_luis = hacer_pedido(otro_web, {"B01": 1})
    assert f"/mis-pedidos/{pedido_luis.id}" in _texto(otro_web.get("/mis-pedidos"))
    assert "/mis-pedidos/" not in _texto(web.get("/mis-pedidos"))
