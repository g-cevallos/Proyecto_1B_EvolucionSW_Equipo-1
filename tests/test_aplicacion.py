"""Pruebas de la creación de la aplicación: configuración, datos iniciales y comando de administración."""

import pytest

from app import create_app
from app.persistencia.db import conectar
from app.servicios.menu_servicio import MenuServicio
from app.servicios.personal_servicio import PersonalServicio


def _configuracion(tmp_path, **extra):
    base = {"DATABASE": str(tmp_path / "base.db"), "SECRET_KEY": "clave-solo-para-pruebas", "TESTING": True,
            "PERSONAL_INICIAL_USUARIO": "admin", "PERSONAL_INICIAL_CLAVE": "clave-de-pruebas"}
    base.update(extra)
    return base


def _con_base(aplicacion):
    return conectar(aplicacion.config["DATABASE"])


def test_la_aplicacion_crea_el_menu_de_demostracion_si_se_pide(tmp_path):
    aplicacion = create_app(_configuracion(tmp_path, CARGAR_DATOS_DEMO=True))
    con = _con_base(aplicacion)
    try:
        assert len(MenuServicio(con).listar_todos()) == 9
    finally:
        con.close()


def test_la_aplicacion_no_carga_datos_de_demostracion_si_no_se_pide(tmp_path):
    aplicacion = create_app(_configuracion(tmp_path, CARGAR_DATOS_DEMO=False))
    con = _con_base(aplicacion)
    try:
        assert MenuServicio(con).listar_todos() == []
    finally:
        con.close()


def test_los_datos_de_demostracion_no_se_duplican_al_reiniciar(tmp_path):
    configuracion = _configuracion(tmp_path, CARGAR_DATOS_DEMO=True)
    create_app(configuracion)
    aplicacion = create_app(configuracion)
    con = _con_base(aplicacion)
    try:
        assert len(MenuServicio(con).listar_todos()) == 9
    finally:
        con.close()


def test_el_usuario_inicial_del_personal_se_crea_una_sola_vez(tmp_path):
    configuracion = _configuracion(tmp_path, CARGAR_DATOS_DEMO=False)
    create_app(configuracion)
    configuracion["PERSONAL_INICIAL_CLAVE"] = "otra-clave-larga"
    aplicacion = create_app(configuracion)
    con = _con_base(aplicacion)
    try:
        servicio = PersonalServicio(con)
        assert servicio.autenticar("admin", "clave-de-pruebas") == "Administrador"
    finally:
        con.close()


def test_sin_base_indicada_se_usa_la_carpeta_instance(tmp_path, instancia_temporal):
    configuracion = _configuracion(tmp_path, CARGAR_DATOS_DEMO=False, DATABASE=None)
    aplicacion = create_app(configuracion)
    assert aplicacion.config["DATABASE"] == str(instancia_temporal / "cafeteria.db")


def test_sin_clave_secreta_se_genera_una_y_se_reutiliza(tmp_path, instancia_temporal):
    aplicacion = create_app(_configuracion(tmp_path, CARGAR_DATOS_DEMO=False, SECRET_KEY=None))
    clave = aplicacion.config["SECRET_KEY"]
    assert len(clave) == 64 and (instancia_temporal / "secret_key").read_text() == clave
    otra = create_app(_configuracion(tmp_path, CARGAR_DATOS_DEMO=False, SECRET_KEY=None))
    assert otra.config["SECRET_KEY"] == clave


def test_el_comando_crear_personal_registra_un_usuario(app):
    resultado = app.test_cli_runner().invoke(
        args=["crear-personal", "maria", "María Pérez", "--clave", "clave-segura-1"])
    assert resultado.exit_code == 0 and "Usuario maria creado" in resultado.output
    con = _con_base(app)
    try:
        assert PersonalServicio(con).autenticar("maria", "clave-segura-1") == "María Pérez"
    finally:
        con.close()


@pytest.mark.parametrize("clave", ["corta"])
def test_el_comando_crear_personal_rechaza_claves_cortas(app, clave):
    resultado = app.test_cli_runner().invoke(args=["crear-personal", "maria", "María", "--clave", clave])
    assert resultado.exit_code != 0
