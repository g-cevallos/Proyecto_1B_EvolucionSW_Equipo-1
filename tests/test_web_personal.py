"""Pruebas de la web del personal: ingreso, atención de pedidos, entrega con código y mantenimiento del menú."""

import re

import pytest

from app.persistencia.db import conectar


def _texto(respuesta):
    return respuesta.get_data(as_text=True)


@pytest.fixture
def personal_web(otro_web, ingresar_personal):
    """Navegador con la sesión del personal iniciada."""
    ingresar_personal(otro_web)
    return otro_web


@pytest.fixture
def pedido_web(web, registrar_cliente, hacer_pedido):
    """Pedido de un cliente: 2 cafés y 1 sánduche ($4.50)."""
    registrar_cliente(web)
    return hacer_pedido(web, {"B01": 2, "A01": 1})


# ------------------------------------------------------------------------------ ingreso
def test_el_formulario_de_ingreso_del_personal_se_muestra(web):
    respuesta = web.get("/personal/ingresar")
    assert respuesta.status_code == 200 and 'name="clave"' in _texto(respuesta)


def test_el_personal_ingresa_con_usuario_y_clave(web, ingresar_personal):
    respuesta = ingresar_personal(web)
    assert respuesta.status_code == 302 and respuesta.headers["Location"].endswith("/personal/pedidos")
    assert web.get("/personal/pedidos").status_code == 200


def test_el_usuario_se_acepta_sin_distinguir_mayusculas(web, ingresar_personal):
    assert ingresar_personal(web, " ADMIN ").status_code == 302


@pytest.mark.parametrize("usuario, clave", [("admin", "incorrecta"), ("nadie", "clave-de-pruebas"), ("", "")])
def test_credenciales_incorrectas_no_inician_sesion(web, ingresar_personal, usuario, clave):
    respuesta = ingresar_personal(web, usuario, clave)
    assert respuesta.status_code == 401
    assert "Usuario o clave incorrectos" in _texto(respuesta)
    assert web.get("/personal/pedidos").status_code == 302


def test_salir_cierra_la_sesion_del_personal(personal_web, enviar):
    assert enviar(personal_web, "/personal/salir").status_code == 302
    assert personal_web.get("/personal/pedidos").status_code == 302


def test_la_clave_inicial_no_queda_en_texto_claro_en_la_base(app):
    con = conectar(app.config["DATABASE"])
    try:
        fila = con.execute("SELECT hash_clave FROM personal").fetchone()
    finally:
        con.close()
    assert "clave-de-pruebas" not in fila[0]


# ------------------------------------------------------------------------ lista de pedidos
def test_la_lista_muestra_por_defecto_los_pedidos_pendientes_con_su_accion(personal_web, pedido_web):
    texto = _texto(personal_web.get("/personal/pedidos"))
    assert f"#{pedido_web.id}" in texto and "Iniciar preparación" in texto


def test_la_lista_se_filtra_por_estado(personal_web, pedido_web):
    assert f"#{pedido_web.id}" not in _texto(personal_web.get("/personal/pedidos?estado=ENTREGADO"))
    assert f"#{pedido_web.id}" in _texto(personal_web.get("/personal/pedidos?estado=PENDIENTE"))


def test_un_estado_desconocido_en_el_filtro_muestra_los_pendientes(personal_web, pedido_web):
    respuesta = personal_web.get("/personal/pedidos?estado=INVENTADO")
    assert respuesta.status_code == 200 and f"#{pedido_web.id}" in _texto(respuesta)


# ------------------------------------------------------------------------ avance de estado
def test_el_personal_avanza_un_pedido_paso_a_paso(personal_web, web, enviar, pedido_web):
    ruta = f"/personal/pedidos/{pedido_web.id}/avanzar"
    primero = enviar(personal_web, ruta, {"estado_nuevo": "EN_PREPARACION", "estado_origen": "PENDIENTE"},
                     follow_redirects=True)
    assert "ahora está «En preparación»" in _texto(primero)
    segundo = enviar(personal_web, ruta, {"estado_nuevo": "LISTO_PARA_RETIRAR", "estado_origen": "EN_PREPARACION"},
                     follow_redirects=True)
    assert "ahora está «Listo para retirar»" in _texto(segundo)
    assert "Listo para retirar" in _texto(web.get(f"/mis-pedidos/{pedido_web.id}"))


@pytest.mark.parametrize("nuevo", ["LISTO_PARA_RETIRAR", "ENTREGADO", "PENDIENTE"])
def test_no_se_puede_saltar_ni_entregar_desde_la_lista(personal_web, enviar, pedido_web, nuevo):
    respuesta = enviar(personal_web, f"/personal/pedidos/{pedido_web.id}/avanzar", {"estado_nuevo": nuevo},
                       follow_redirects=True)
    assert "no puede pasar" in _texto(respuesta) or "código de retiro" in _texto(respuesta)
    assert f"#{pedido_web.id}" in _texto(personal_web.get("/personal/pedidos?estado=PENDIENTE"))


def test_un_estado_no_reconocido_se_informa(personal_web, enviar, pedido_web):
    respuesta = enviar(personal_web, f"/personal/pedidos/{pedido_web.id}/avanzar", {"estado_nuevo": "XYZ"},
                       follow_redirects=True)
    assert "Estado no reconocido" in _texto(respuesta)


def test_avanzar_un_pedido_inexistente_se_informa(personal_web, enviar):
    respuesta = enviar(personal_web, "/personal/pedidos/999/avanzar", {"estado_nuevo": "EN_PREPARACION"},
                       follow_redirects=True)
    assert "#999" in _texto(respuesta)


# ----------------------------------------------------------------------------------- entrega
def _dejar_listo(personal_web, enviar, pedido):
    ruta = f"/personal/pedidos/{pedido.id}/avanzar"
    enviar(personal_web, ruta, {"estado_nuevo": "EN_PREPARACION"})
    enviar(personal_web, ruta, {"estado_nuevo": "LISTO_PARA_RETIRAR"})


def test_la_pantalla_de_entrega_se_muestra_vacia(personal_web):
    assert personal_web.get("/personal/entrega").status_code == 200


def test_buscar_por_codigo_muestra_el_pedido_y_su_cliente(personal_web, enviar, pedido_web):
    respuesta = enviar(personal_web, "/personal/entrega", {"codigo": pedido_web.codigo.lower()})
    texto = _texto(respuesta)
    assert f"#{pedido_web.id}" in texto and "Ana Torres" in texto


def test_buscar_un_codigo_inexistente_se_informa(personal_web, enviar, pedido_web):
    respuesta = enviar(personal_web, "/personal/entrega", {"codigo": "ZZZZZZ"})
    assert "código de retiro" in _texto(respuesta)


def test_entregar_un_pedido_listo_con_su_codigo_lo_marca_como_entregado(personal_web, web, enviar, pedido_web):
    _dejar_listo(personal_web, enviar, pedido_web)
    respuesta = enviar(personal_web, "/personal/entrega/confirmar",
                       {"pedido_id": str(pedido_web.id), "codigo": pedido_web.codigo}, follow_redirects=True)
    assert "registrado como Entregado" in _texto(respuesta)
    assert "Entregado" in _texto(web.get(f"/mis-pedidos/{pedido_web.id}"))


def test_un_codigo_incorrecto_no_entrega_el_pedido(personal_web, web, enviar, pedido_web):
    _dejar_listo(personal_web, enviar, pedido_web)
    respuesta = enviar(personal_web, "/personal/entrega/confirmar",
                       {"pedido_id": str(pedido_web.id), "codigo": "ZZZZZZ"}, follow_redirects=True)
    assert "no corresponde" in _texto(respuesta)
    assert "Listo para retirar" in _texto(web.get(f"/mis-pedidos/{pedido_web.id}"))


def test_un_pedido_que_aun_no_esta_listo_no_se_entrega(personal_web, enviar, pedido_web):
    respuesta = enviar(personal_web, "/personal/entrega/confirmar",
                       {"pedido_id": str(pedido_web.id), "codigo": pedido_web.codigo}, follow_redirects=True)
    assert "solo se entregan pedidos Listos" in _texto(respuesta)


def test_un_pedido_no_se_entrega_dos_veces(personal_web, enviar, pedido_web):
    _dejar_listo(personal_web, enviar, pedido_web)
    datos = {"pedido_id": str(pedido_web.id), "codigo": pedido_web.codigo}
    enviar(personal_web, "/personal/entrega/confirmar", datos)
    respuesta = enviar(personal_web, "/personal/entrega/confirmar", datos, follow_redirects=True)
    assert "Entregado" in _texto(respuesta) and "registrado como Entregado" not in _texto(respuesta)


@pytest.mark.parametrize("pedido_id", ["", "abc", "1.5"])
def test_un_identificador_de_pedido_no_valido_se_informa(personal_web, enviar, pedido_id):
    respuesta = enviar(personal_web, "/personal/entrega/confirmar", {"pedido_id": pedido_id, "codigo": "ABCDEF"},
                       follow_redirects=True)
    assert "Identificador de pedido no válido" in _texto(respuesta)


# ------------------------------------------------------------------------------- productos
def test_el_personal_ve_todos_los_productos_incluso_los_no_disponibles(personal_web):
    texto = _texto(personal_web.get("/personal/productos"))
    assert "Almuerzo del día" in texto and "Café pasado" in texto


def test_el_formulario_de_producto_nuevo_se_muestra_con_disponible_marcado(personal_web):
    respuesta = personal_web.get("/personal/productos/nuevo")
    assert respuesta.status_code == 200 and "checked" in _texto(respuesta)


def test_registrar_un_producto_lo_agrega_al_menu_del_cliente(personal_web, web, enviar):
    respuesta = enviar(personal_web, "/personal/productos/nuevo", {
        "codigo": "z01", "nombre": "Brownie", "categoria": "ALIMENTO", "precio": "1,25", "disponible": "1"},
        follow_redirects=True)
    assert "Producto «Brownie» registrado" in _texto(respuesta)
    assert "Brownie" in _texto(web.get("/menu"))


def test_registrar_un_producto_sin_marcar_disponible_no_lo_muestra_al_cliente(personal_web, web, enviar):
    enviar(personal_web, "/personal/productos/nuevo", {
        "codigo": "Z02", "nombre": "Brownie", "categoria": "ALIMENTO", "precio": "1.25"})
    assert "Brownie" not in _texto(web.get("/menu"))
    assert "Brownie" in _texto(personal_web.get("/personal/productos"))


@pytest.mark.parametrize("cambios, mensaje", [
    ({"codigo": "B01"}, "B01"),
    ({"nombre": "A"}, ""),
    ({"precio": "0"}, ""),
    ({"precio": "abc"}, ""),
    ({"categoria": "POSTRE"}, ""),
])
def test_un_producto_invalido_o_repetido_se_rechaza_y_conserva_lo_escrito(personal_web, enviar, cambios, mensaje):
    datos = {"codigo": "Z03", "nombre": "Brownie", "categoria": "ALIMENTO", "precio": "1.25", "disponible": "1"}
    datos.update(cambios)
    respuesta = enviar(personal_web, "/personal/productos/nuevo", datos)
    assert respuesta.status_code == 422
    assert mensaje in _texto(respuesta)
    assert "Z03" not in _texto(personal_web.get("/personal/productos")) or cambios.get("codigo")


def test_el_formulario_de_edicion_muestra_los_datos_actuales(personal_web):
    texto = _texto(personal_web.get("/personal/productos/B01/editar"))
    assert 'value="Café pasado"' in texto and 'value="1.00"' in texto


def test_editar_un_producto_inexistente_muestra_un_error(personal_web):
    assert personal_web.get("/personal/productos/NOEXISTE/editar").status_code == 400


def test_editar_un_producto_actualiza_precio_y_nombre(personal_web, web, enviar):
    respuesta = enviar(personal_web, "/personal/productos/B01/editar", {
        "nombre": "Café americano", "categoria": "BEBIDA", "precio": "1.20", "disponible": "1"},
        follow_redirects=True)
    assert "actualizado" in _texto(respuesta)
    menu = _texto(web.get("/menu"))
    assert "Café americano" in menu and "$1.20" in menu


def test_una_edicion_invalida_no_cambia_el_producto(personal_web, web, enviar):
    respuesta = enviar(personal_web, "/personal/productos/B01/editar", {
        "nombre": "Café americano", "categoria": "BEBIDA", "precio": "-3", "disponible": "1"})
    assert respuesta.status_code == 422
    assert "Café pasado" in _texto(web.get("/menu"))


def test_el_codigo_de_un_producto_no_se_cambia_al_editar(personal_web, enviar):
    enviar(personal_web, "/personal/productos/B01/editar", {
        "codigo": "OTRO", "nombre": "Café americano", "categoria": "BEBIDA", "precio": "1.20", "disponible": "1"})
    texto = _texto(personal_web.get("/personal/productos"))
    assert "B01" in texto and "OTRO" not in texto


def test_desactivar_y_activar_un_producto_con_un_clic(personal_web, web, enviar):
    desactivado = enviar(personal_web, "/personal/productos/B01/disponibilidad", {"disponible": "0"},
                         follow_redirects=True)
    assert "ahora está no disponible" in _texto(desactivado)
    assert "Café pasado" not in _texto(web.get("/menu"))
    activado = enviar(personal_web, "/personal/productos/B01/disponibilidad", {"disponible": "1"},
                      follow_redirects=True)
    assert "ahora está disponible" in _texto(activado)
    assert "Café pasado" in _texto(web.get("/menu"))


def test_cambiar_la_disponibilidad_de_un_producto_inexistente_muestra_un_error(personal_web, enviar):
    assert enviar(personal_web, "/personal/productos/NOEXISTE/disponibilidad", {"disponible": "1"}).status_code == 400


def test_un_pedido_ya_hecho_conserva_el_precio_aunque_el_personal_lo_cambie(personal_web, web, enviar, pedido_web):
    enviar(personal_web, "/personal/productos/B01/editar", {
        "nombre": "Café pasado", "categoria": "BEBIDA", "precio": "9.00", "disponible": "1"})
    detalle = _texto(web.get(f"/mis-pedidos/{pedido_web.id}"))
    assert "$4.50" in detalle and re.search(r"\$9\.00", detalle) is None
