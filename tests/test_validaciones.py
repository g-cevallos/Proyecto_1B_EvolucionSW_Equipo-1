"""Pruebas de las funciones de validación y conversión de datos de entrada."""

import pytest

from app.dominio.excepciones import ValidacionError
from app.dominio.validaciones import (
    PRECIO_MAXIMO_CENTAVOS,
    convertir_precio_a_centavos,
    formatear_centavos,
    validar_cedula,
    validar_celular,
    validar_codigo_producto,
    validar_correo_institucional,
    validar_nombre,
)


# ----------------------------------------------------------------------- cédula
@pytest.mark.parametrize("cedula", ["1710034065", "0100000009", "2400000002", "3000000004"])
def test_cedula_valida_es_aceptada(cedula):
    assert validar_cedula(cedula) == cedula


def test_cedula_ignora_espacios_alrededor():
    assert validar_cedula("  1710034065 ") == "1710034065"


def test_cedula_con_digito_verificador_incorrecto_es_rechazada():
    with pytest.raises(ValidacionError, match="verificador"):
        validar_cedula("1710034066")


@pytest.mark.parametrize("cedula", [
    "", None, "171003406", "17100340655", "17100340a5", "1710 34065", "١٧١٠٠٣٤٠٦٥",
])
def test_cedula_con_formato_invalido_es_rechazada(cedula):
    with pytest.raises(ValidacionError, match="10 dígitos"):
        validar_cedula(cedula)


@pytest.mark.parametrize("cedula", ["0010034065", "2510034065", "3110034065"])
def test_cedula_con_provincia_inexistente_es_rechazada(cedula):
    with pytest.raises(ValidacionError, match="provincia"):
        validar_cedula(cedula)


def test_cedula_con_tercer_digito_no_valido_para_personas_naturales_es_rechazada():
    with pytest.raises(ValidacionError, match="tercer dígito"):
        validar_cedula("1760034065")


# ------------------------------------------------------------- nombre y apellido
@pytest.mark.parametrize("entrada, esperado", [
    ("Ana", "Ana"),
    ("  Ana   Lucía ", "Ana Lucía"),
    ("María José", "María José"),
    ("O'Neil", "O'Neil"),
    ("Pérez-Gil", "Pérez-Gil"),
    ("Ñandú", "Ñandú"),
])
def test_nombre_valido_se_normaliza(entrada, esperado):
    assert validar_nombre(entrada, "nombre") == esperado


@pytest.mark.parametrize("entrada", ["", None, "A", "Ana3", "Ana_", "x" * 61, "   "])
def test_nombre_invalido_es_rechazado(entrada):
    with pytest.raises(ValidacionError):
        validar_nombre(entrada, "nombre")


def test_mensaje_de_nombre_indica_el_campo():
    with pytest.raises(ValidacionError, match="apellido"):
        validar_nombre("1", "apellido")


def test_nombre_de_60_letras_es_el_maximo_permitido():
    assert validar_nombre("a" * 60, "nombre") == "a" * 60


# ----------------------------------------------------------------------- celular
@pytest.mark.parametrize("entrada", ["0991234567", " 0991234567 ", "099 123 4567"])
def test_celular_valido_se_normaliza(entrada):
    assert validar_celular(entrada) == "0991234567"


@pytest.mark.parametrize("entrada", ["", None, "0891234567", "099123456", "09912345678", "09912345a7"])
def test_celular_invalido_es_rechazado(entrada):
    with pytest.raises(ValidacionError, match="09"):
        validar_celular(entrada)


# ------------------------------------------------------------ correo institucional
@pytest.mark.parametrize("correo", ["ana@epn.edu.ec", "ana.torres+1@epn.edu.ec", "ana@est.epn.edu.ec"])
def test_correo_del_dominio_o_de_un_subdominio_es_aceptado(correo):
    assert validar_correo_institucional(correo, "epn.edu.ec") == correo


def test_correo_se_pasa_a_minusculas():
    assert validar_correo_institucional("  Ana@EPN.edu.ec ", "epn.edu.ec") == "ana@epn.edu.ec"


def test_dominio_configurado_acepta_arroba_y_mayusculas():
    assert validar_correo_institucional("ana@epn.edu.ec", "@EPN.edu.ec") == "ana@epn.edu.ec"


@pytest.mark.parametrize("correo", [
    "", None, "ana", "ana@", "@epn.edu.ec", "ana@gmail.com", "ana@xepn.edu.ec",
    "ana@epn.edu.ec.evil.com", "an a@epn.edu.ec", "ana@@epn.edu.ec",
])
def test_correo_que_no_es_institucional_es_rechazado(correo):
    with pytest.raises(ValidacionError, match="epn.edu.ec"):
        validar_correo_institucional(correo, "epn.edu.ec")


def test_correo_se_valida_contra_el_dominio_que_se_indique():
    assert validar_correo_institucional("ana@uce.edu.ec", "uce.edu.ec") == "ana@uce.edu.ec"
    with pytest.raises(ValidacionError):
        validar_correo_institucional("ana@epn.edu.ec", "uce.edu.ec")


# --------------------------------------------------------------- código de producto
@pytest.mark.parametrize("entrada, esperado", [
    ("caf1", "CAF1"), (" a-01 ", "A-01"), ("AB", "AB"), ("X" * 10, "X" * 10),
])
def test_codigo_de_producto_valido_se_pasa_a_mayusculas(entrada, esperado):
    assert validar_codigo_producto(entrada) == esperado


@pytest.mark.parametrize("entrada", ["", None, "A", "X" * 11, "AB CD", "AB_CD", "ÑANDU"])
def test_codigo_de_producto_invalido_es_rechazado(entrada):
    with pytest.raises(ValidacionError):
        validar_codigo_producto(entrada)


# ------------------------------------------------------------------------ precios
@pytest.mark.parametrize("texto, centavos", [
    ("1.50", 150), ("1,50", 150), ("2", 200), ("0.05", 5), (" 3.5 ", 350), ("19.99", 1999),
    ("0.07", 7), ("1000", PRECIO_MAXIMO_CENTAVOS), ("1000.00", PRECIO_MAXIMO_CENTAVOS),
])
def test_precio_valido_se_convierte_a_centavos(texto, centavos):
    assert convertir_precio_a_centavos(texto) == centavos


@pytest.mark.parametrize("texto, motivo", [
    ("", "número"), (None, "número"), ("abc", "número"), ("1.2.3", "número"),
    ("1.505", "decimales"), ("0.001", "decimales"), ("NaN", "decimales"), ("Infinity", "decimales"),
    ("0", "mayor que cero"), ("0.00", "mayor que cero"), ("-1", "mayor que cero"),
    ("1000.01", "superar"), ("5000", "superar"),
])
def test_precio_invalido_es_rechazado_con_su_motivo(texto, motivo):
    with pytest.raises(ValidacionError, match=motivo):
        convertir_precio_a_centavos(texto)


@pytest.mark.parametrize("centavos, texto", [
    (250, "$2.50"), (5, "$0.05"), (0, "$0.00"), (100, "$1.00"), (PRECIO_MAXIMO_CENTAVOS, "$1000.00"),
])
def test_dinero_se_muestra_en_dolares_con_dos_decimales(centavos, texto):
    assert formatear_centavos(centavos) == texto


def test_ida_y_vuelta_entre_texto_y_centavos_conserva_el_valor():
    for texto in ("0.05", "1.10", "12.34", "999.99"):
        assert formatear_centavos(convertir_precio_a_centavos(texto)) == f"${texto}"
