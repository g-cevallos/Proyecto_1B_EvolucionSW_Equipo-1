"""Pruebas de los servicios de clientes (registro e identificación) y del personal (autenticación)."""

import pytest

from app.dominio.excepciones import ClienteDuplicadoError, CredencialesInvalidasError, ValidacionError
from app.persistencia.repositorios import ClienteRepositorio, PersonalRepositorio
from app.servicios.cliente_servicio import ClienteServicio
from app.servicios.personal_servicio import LONGITUD_MINIMA_CLAVE, PersonalServicio


def _total_clientes(conexion):
    return conexion.execute("SELECT COUNT(*) FROM cliente").fetchone()[0]


# --------------------------------------------------------------- registro de clientes
def test_registrar_cliente_normaliza_los_datos_y_asigna_codigo(clientes, cedula_valida):
    cliente = clientes.registrar("  Ana   María ", " Torres ", cedula_valida("171003406"),
                                 "099 123 4567", " ANA@EPN.edu.ec ")
    assert (cliente.nombre, cliente.apellido) == ("Ana María", "Torres")
    assert (cliente.celular, cliente.correo) == ("0991234567", "ana@epn.edu.ec")
    assert cliente.codigo == "CLI-00001"
    assert clientes.obtener(cliente.id).cedula == "1710034065"


def test_los_codigos_de_cliente_son_consecutivos(cliente, otro_cliente):
    assert (cliente.codigo, otro_cliente.codigo) == ("CLI-00001", "CLI-00002")


def test_no_se_registra_dos_veces_la_misma_cedula(clientes, cliente, conexion):
    with pytest.raises(ClienteDuplicadoError, match="cédula"):
        clientes.registrar("Otra", "Persona", cliente.cedula, "0987654321", "otra@epn.edu.ec")
    assert _total_clientes(conexion) == 1


def test_no_se_registra_dos_veces_el_mismo_correo(clientes, cliente, cedula_valida, conexion):
    with pytest.raises(ClienteDuplicadoError, match="correo"):
        clientes.registrar("Otra", "Persona", cedula_valida("171003407"), "0987654321", cliente.correo)
    assert _total_clientes(conexion) == 1


@pytest.mark.parametrize("cambios", [
    {"nombre": "1"},
    {"apellido": ""},
    {"cedula": "1710034066"},
    {"cedula": "123"},
    {"celular": "0891234567"},
    {"correo": "ana@gmail.com"},
    {"correo": "ana"},
])
def test_un_dato_invalido_impide_el_registro(clientes, cedula_valida, conexion, cambios):
    datos = {"nombre": "Ana", "apellido": "Torres", "cedula": cedula_valida("171003406"),
             "celular": "0991234567", "correo": "ana@epn.edu.ec"}
    datos.update(cambios)
    with pytest.raises(ValidacionError):
        clientes.registrar(**datos)
    assert _total_clientes(conexion) == 0


def test_el_correo_se_valida_contra_el_dominio_configurado(conexion, cedula_valida):
    servicio = ClienteServicio(conexion, "uce.edu.ec")
    with pytest.raises(ValidacionError):
        servicio.registrar("Ana", "Torres", cedula_valida("171003406"), "0991234567", "ana@epn.edu.ec")
    assert servicio.registrar("Ana", "Torres", cedula_valida("171003406"), "0991234567",
                              "ana@uce.edu.ec").correo == "ana@uce.edu.ec"


def test_un_registro_simultaneo_con_los_mismos_datos_es_duplicado(clientes, cliente, monkeypatch, conexion):
    # Simula que la verificación previa no vio al cliente que otro usuario guardó un instante antes.
    monkeypatch.setattr(ClienteRepositorio, "obtener_por_cedula", lambda self, cedula: None)
    monkeypatch.setattr(ClienteRepositorio, "existe_correo", lambda self, correo: False)
    with pytest.raises(ClienteDuplicadoError):
        clientes.registrar("Ana", "Torres", cliente.cedula, "0991234567", cliente.correo)
    assert _total_clientes(conexion) == 1


# ------------------------------------------------------------------- identificación
def test_identificar_con_cedula_y_correo_correctos(clientes, cliente):
    assert clientes.identificar(cliente.cedula, cliente.correo).id == cliente.id


def test_identificar_ignora_espacios_y_mayusculas_del_correo(clientes, cliente):
    assert clientes.identificar(f" {cliente.cedula} ", " ANA@Epn.edu.ec ").id == cliente.id


@pytest.mark.parametrize("cedula, correo", [
    ("1710034065", "otro@epn.edu.ec"),
    ("0100000009", "ana@epn.edu.ec"),
    ("", ""),
    (None, None),
])
def test_identificar_con_datos_que_no_corresponden_falla(clientes, cliente, cedula, correo):
    with pytest.raises(CredencialesInvalidasError, match="no corresponden"):
        clientes.identificar(cedula, correo)


def test_obtener_un_cliente_por_su_identificador(clientes, cliente):
    assert clientes.obtener(cliente.id).nombre_completo == "Ana Torres"
    assert clientes.obtener(999) is None


# ------------------------------------------------------------------------ personal
@pytest.fixture
def personal(conexion):
    """Servicio del personal sobre la base en memoria."""
    return PersonalServicio(conexion)


def test_registrar_personal_guarda_la_clave_como_hash(personal, conexion):
    personal.registrar("  María ", " María   Pérez ", "clave-segura-1")
    fila = PersonalRepositorio(conexion).obtener("maría")
    assert fila["nombre"] == "María Pérez"
    assert fila["hash_clave"] != "clave-segura-1"
    assert "clave-segura-1" not in fila["hash_clave"]


def test_la_misma_clave_produce_hashes_distintos_en_usuarios_distintos(personal, conexion):
    personal.registrar("maria", "María", "clave-segura-1")
    personal.registrar("juan", "Juan", "clave-segura-1")
    repositorio = PersonalRepositorio(conexion)
    assert repositorio.obtener("maria")["hash_clave"] != repositorio.obtener("juan")["hash_clave"]


def test_autenticar_devuelve_el_nombre_del_usuario(personal):
    personal.registrar("maria", "María Pérez", "clave-segura-1")
    assert personal.autenticar("maria", "clave-segura-1") == "María Pérez"
    assert personal.autenticar("  MARIA ", "clave-segura-1") == "María Pérez"


@pytest.mark.parametrize("usuario, clave", [
    ("maria", "otra-clave-1"), ("maria", "CLAVE-SEGURA-1"), ("nadie", "clave-segura-1"), ("", ""), (None, None),
])
def test_credenciales_incorrectas_no_autentican_y_no_revelan_cual_fallo(personal, usuario, clave):
    personal.registrar("maria", "María Pérez", "clave-segura-1")
    with pytest.raises(CredencialesInvalidasError, match="Usuario o clave incorrectos"):
        personal.autenticar(usuario, clave)


def test_la_clave_debe_tener_al_menos_ocho_caracteres(personal):
    with pytest.raises(ValidacionError, match=str(LONGITUD_MINIMA_CLAVE)):
        personal.registrar("maria", "María", "1234567")
    personal.registrar("maria", "María", "12345678")
    assert personal.hay_usuarios() is True


@pytest.mark.parametrize("usuario, nombre, clave", [
    ("", "María", "clave-segura-1"), ("   ", "María", "clave-segura-1"),
    ("maria", "", "clave-segura-1"), (None, None, "clave-segura-1"), ("maria", "María", None),
])
def test_el_registro_del_personal_exige_usuario_nombre_y_clave(personal, usuario, nombre, clave):
    with pytest.raises(ValidacionError):
        personal.registrar(usuario, nombre, clave)
    assert personal.hay_usuarios() is False


def test_no_se_repite_un_usuario_aunque_cambien_las_mayusculas(personal):
    personal.registrar("maria", "María", "clave-segura-1")
    with pytest.raises(ValidacionError, match="ya existe"):
        personal.registrar("MARIA", "Otra", "otra-clave-1")


def test_hay_usuarios_indica_si_existe_al_menos_uno(personal):
    assert personal.hay_usuarios() is False
    personal.registrar("maria", "María", "clave-segura-1")
    assert personal.hay_usuarios() is True
