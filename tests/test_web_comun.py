"""Pruebas de lo común a toda la web: protección CSRF, páginas de error, acceso restringido y redirecciones."""

import pytest

from app.web.comun import ruta_local


# ------------------------------------------------------------------------------ CSRF
@pytest.mark.parametrize("ruta", ["/registro", "/ingresar", "/salir", "/pedido/revisar", "/personal/ingresar"])
def test_un_formulario_sin_token_csrf_se_rechaza(web, ruta):
    respuesta = web.post(ruta, data={"nombre": "Ana"})
    assert respuesta.status_code == 400
    assert "expiró" in respuesta.get_data(as_text=True)


def test_un_token_csrf_incorrecto_se_rechaza(web, csrf):
    csrf(web)
    assert web.post("/ingresar", data={"csrf": "otro-token"}).status_code == 400


def test_el_token_de_una_sesion_no_sirve_en_otra(web, otro_web, csrf):
    token = csrf(web)
    csrf(otro_web)
    assert otro_web.post("/ingresar", data={"csrf": token}).status_code == 400


def test_sin_sesion_previa_un_envio_con_token_vacio_se_rechaza(web):
    assert web.post("/ingresar", data={"csrf": ""}).status_code == 400


def test_con_csrf_valido_el_formulario_se_procesa(web, enviar):
    assert enviar(web, "/ingresar", {"cedula": "x", "correo": "y"}).status_code == 401


def test_las_consultas_get_no_exigen_token(web):
    assert web.get("/menu").status_code == 200


# --------------------------------------------------------------------------- páginas
def test_la_pagina_de_inicio_es_publica(web):
    assert web.get("/").status_code == 200


def test_una_pagina_inexistente_muestra_el_error_404(web):
    respuesta = web.get("/no-existe")
    assert respuesta.status_code == 404
    assert "no existe" in respuesta.get_data(as_text=True)


def test_un_metodo_no_permitido_muestra_el_error_405(web):
    respuesta = web.get("/salir")
    assert respuesta.status_code == 405
    assert "no está permitida" in respuesta.get_data(as_text=True)


def test_un_pedido_de_otro_cliente_o_inexistente_muestra_un_error_controlado(web, registrar_cliente):
    registrar_cliente(web)
    respuesta = web.get("/mis-pedidos/999")
    assert respuesta.status_code == 400
    assert "No se encontró" in respuesta.get_data(as_text=True)


# ------------------------------------------------------------------ acceso restringido
@pytest.mark.parametrize("ruta", ["/mis-pedidos", "/mis-pedidos/1"])
def test_las_paginas_del_cliente_piden_identificarse(web, ruta):
    respuesta = web.get(ruta)
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].startswith("/ingresar?siguiente=")


@pytest.mark.parametrize("ruta", [
    "/personal/pedidos", "/personal/entrega", "/personal/productos", "/personal/productos/nuevo",
    "/personal/productos/B01/editar",
])
def test_las_paginas_del_personal_piden_iniciar_sesion(web, ruta):
    respuesta = web.get(ruta)
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/personal/ingresar")


@pytest.mark.parametrize("ruta", [
    "/personal/pedidos/1/avanzar", "/personal/entrega/confirmar", "/personal/productos/B01/disponibilidad",
])
def test_las_acciones_del_personal_por_post_piden_iniciar_sesion(web, enviar, ruta):
    respuesta = enviar(web, ruta, {})
    assert respuesta.status_code == 302
    assert respuesta.headers["Location"].endswith("/personal/ingresar")


def test_un_cliente_identificado_no_accede_a_las_paginas_del_personal(web, registrar_cliente):
    registrar_cliente(web)
    assert web.get("/personal/pedidos").status_code == 302


def test_la_sesion_del_personal_no_da_acceso_a_las_paginas_del_cliente(web, ingresar_personal):
    ingresar_personal(web)
    assert web.get("/mis-pedidos").status_code == 302


# -------------------------------------------------------------------- ruta_local
@pytest.mark.parametrize("destino", ["/menu", "/mis-pedidos/3", "/menu?a=1"])
def test_ruta_local_acepta_rutas_internas(destino):
    assert ruta_local(destino, "/por-defecto") == destino


@pytest.mark.parametrize("destino", [None, "", "menu", "//evil.com", "https://evil.com", "http://evil.com/x"])
def test_ruta_local_rechaza_destinos_externos_o_relativos(destino):
    assert ruta_local(destino, "/por-defecto") == "/por-defecto"


def test_el_parametro_siguiente_externo_no_redirige_fuera_del_sitio(web, enviar, registrar_cliente):
    cliente = registrar_cliente(web)
    web.post("/salir", data={"csrf": "x"})
    otro = web.application.test_client()
    respuesta = enviar(otro, "/ingresar", {"cedula": cliente.cedula, "correo": cliente.correo,
                                           "siguiente": "//evil.com"})
    assert respuesta.status_code == 302
    assert "evil.com" not in respuesta.headers["Location"]
