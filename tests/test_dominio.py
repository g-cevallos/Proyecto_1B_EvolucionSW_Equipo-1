"""Pruebas de las entidades del dominio, las excepciones de negocio y el generador de códigos."""

import pytest

from app.dominio import excepciones
from app.dominio.modelos import Categoria, Cliente, DetallePedido, EstadoPedido, ResumenPedido
from app.servicios.generador_codigo import ALFABETO, LONGITUD, generar_codigo_retiro, normalizar_codigo


# --------------------------------------------------------------------- estados
def test_los_estados_se_declaran_en_el_orden_de_atencion():
    assert list(EstadoPedido) == [
        EstadoPedido.PENDIENTE,
        EstadoPedido.EN_PREPARACION,
        EstadoPedido.LISTO_PARA_RETIRAR,
        EstadoPedido.ENTREGADO,
    ]


@pytest.mark.parametrize("estado, siguiente", [
    (EstadoPedido.PENDIENTE, EstadoPedido.EN_PREPARACION),
    (EstadoPedido.EN_PREPARACION, EstadoPedido.LISTO_PARA_RETIRAR),
    (EstadoPedido.LISTO_PARA_RETIRAR, EstadoPedido.ENTREGADO),
    (EstadoPedido.ENTREGADO, None),
])
def test_cada_estado_conoce_su_siguiente(estado, siguiente):
    assert estado.siguiente() is siguiente


@pytest.mark.parametrize("estado, etiqueta", [
    (EstadoPedido.PENDIENTE, "Pendiente"),
    (EstadoPedido.EN_PREPARACION, "En preparación"),
    (EstadoPedido.LISTO_PARA_RETIRAR, "Listo para retirar"),
    (EstadoPedido.ENTREGADO, "Entregado"),
])
def test_cada_estado_tiene_una_etiqueta_legible(estado, etiqueta):
    assert estado.etiqueta == etiqueta


def test_un_estado_se_reconstruye_desde_su_valor_guardado():
    assert EstadoPedido("EN_PREPARACION") is EstadoPedido.EN_PREPARACION
    with pytest.raises(ValueError):
        EstadoPedido("CANCELADO")


# ------------------------------------------------------------------- categorías
def test_categorias_con_su_etiqueta():
    assert Categoria.ALIMENTO.etiqueta == "Alimento"
    assert Categoria.BEBIDA.etiqueta == "Bebida"


def test_solo_existen_las_categorias_alimento_y_bebida():
    assert {categoria.value for categoria in Categoria} == {"ALIMENTO", "BEBIDA"}
    with pytest.raises(ValueError):
        Categoria("POSTRE")


# ------------------------------------------------------------ importes y entidades
def test_subtotal_es_precio_unitario_por_cantidad():
    detalle = DetallePedido(producto_id=1, codigo_producto="CAF1", nombre_producto="Café",
                            cantidad=3, precio_unitario_centavos=150)
    assert detalle.subtotal_centavos == 450


def test_total_del_resumen_suma_los_subtotales():
    resumen = ResumenPedido([
        DetallePedido(1, "CAF1", "Café", 2, 150),
        DetallePedido(2, "SAN1", "Sánduche", 1, 250),
    ])
    assert resumen.total_centavos == 550


def test_resumen_sin_detalles_tiene_total_cero():
    assert ResumenPedido([]).total_centavos == 0


def test_nombre_completo_del_cliente():
    cliente = Cliente("Ana", "Torres", "1710034065", "0991234567", "ana@epn.edu.ec")
    assert cliente.nombre_completo == "Ana Torres"


# ------------------------------------------------------------------ excepciones
NEGOCIO = [
    excepciones.ValidacionError, excepciones.PedidoVacioError, excepciones.CantidadInvalidaError,
    excepciones.ProductoNoDisponibleError, excepciones.ProductoNoEncontradoError,
    excepciones.ProductoDuplicadoError, excepciones.TotalDesactualizadoError,
    excepciones.TransicionEstadoInvalidaError, excepciones.EntregaInvalidaError,
    excepciones.PedidoNoEncontradoError, excepciones.ClienteDuplicadoError,
    excepciones.CredencialesInvalidasError,
]


@pytest.mark.parametrize("clase", NEGOCIO)
def test_toda_excepcion_de_negocio_hereda_de_error_negocio(clase):
    assert issubclass(clase, excepciones.ErrorNegocio)


@pytest.mark.parametrize("clase", NEGOCIO)
def test_la_excepcion_conserva_el_mensaje_para_el_usuario(clase):
    error = clase("Mensaje para el usuario")
    assert error.mensaje == "Mensaje para el usuario"
    assert str(error) == "Mensaje para el usuario"


# ---------------------------------------------------------- generador de códigos
def test_el_codigo_de_retiro_tiene_seis_caracteres_del_alfabeto():
    codigo = generar_codigo_retiro()
    assert len(codigo) == LONGITUD == 6
    assert set(codigo) <= set(ALFABETO)


def test_el_codigo_admite_otra_longitud():
    assert len(generar_codigo_retiro(10)) == 10


def test_el_alfabeto_no_incluye_caracteres_que_se_confunden():
    assert set("0O1IL").isdisjoint(ALFABETO)
    assert len(set(ALFABETO)) == len(ALFABETO)


def test_los_codigos_generados_solo_usan_caracteres_legibles():
    usados = set("".join(generar_codigo_retiro() for _ in range(300)))
    assert usados <= set(ALFABETO)


@pytest.mark.parametrize("entrada, esperado", [
    ("k7q2mx", "K7Q2MX"),
    (" k7q-2mx ", "K7Q2MX"),
    ("K7Q 2MX", "K7Q2MX"),
    ("k7-q2-mx", "K7Q2MX"),
    ("", ""),
    (None, ""),
])
def test_el_codigo_presentado_se_normaliza(entrada, esperado):
    assert normalizar_codigo(entrada) == esperado
