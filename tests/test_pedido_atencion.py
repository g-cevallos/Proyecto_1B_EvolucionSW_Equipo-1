"""Pruebas de la atención de pedidos por el personal: estados, entrega con código y seguimiento."""

import pytest

from app.dominio.excepciones import EntregaInvalidaError, PedidoNoEncontradoError, TransicionEstadoInvalidaError
from app.dominio.modelos import EstadoPedido


def _llevar_a(pedidos, pedido, estado):
    """Avanza un pedido recién confirmado hasta el estado indicado, siguiendo el flujo normal."""
    if estado is EstadoPedido.PENDIENTE:
        return pedidos.obtener(pedido.id)
    pedidos.avanzar_estado(pedido.id, EstadoPedido.EN_PREPARACION, "maria")
    if estado is not EstadoPedido.EN_PREPARACION:
        pedidos.avanzar_estado(pedido.id, EstadoPedido.LISTO_PARA_RETIRAR, "maria")
    if estado is EstadoPedido.ENTREGADO:
        pedidos.entregar_pedido(pedido.id, pedido.codigo_retiro, "juan")
    return pedidos.obtener(pedido.id)


# ---------------------------------------------------------------------- listados
def test_los_pedidos_se_listan_por_orden_de_llegada_y_se_filtran_por_estado(catalogo, pedidos, cliente, otro_cliente):
    primero = pedidos.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    segundo = pedidos.confirmar_pedido(otro_cliente.id, {"CAF1": 1}, 150)
    tercero = pedidos.confirmar_pedido(cliente.id, {"SAN1": 1}, 250)
    pedidos.avanzar_estado(segundo.id, EstadoPedido.EN_PREPARACION, "maria")
    assert [p.id for p in pedidos.listar_pedidos()] == [primero.id, segundo.id, tercero.id]
    assert [p.id for p in pedidos.listar_pedidos(EstadoPedido.PENDIENTE)] == [primero.id, tercero.id]
    assert [p.id for p in pedidos.listar_pedidos(EstadoPedido.EN_PREPARACION)] == [segundo.id]
    assert pedidos.listar_pedidos(EstadoPedido.ENTREGADO) == []


def test_el_conteo_por_estado_incluye_todos_los_estados(catalogo, pedidos, cliente):
    uno = pedidos.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    pedidos.confirmar_pedido(cliente.id, {"CAF1": 1}, 150)
    pedidos.avanzar_estado(uno.id, EstadoPedido.EN_PREPARACION, "maria")
    assert pedidos.contar_por_estado() == {
        EstadoPedido.PENDIENTE: 1, EstadoPedido.EN_PREPARACION: 1,
        EstadoPedido.LISTO_PARA_RETIRAR: 0, EstadoPedido.ENTREGADO: 0,
    }


def test_obtener_un_pedido_inexistente_falla(pedidos):
    with pytest.raises(PedidoNoEncontradoError, match="#999"):
        pedidos.obtener(999)


# ------------------------------------------------------------------- avanzar estado
def test_el_pedido_avanza_de_pendiente_a_en_preparacion_y_a_listo(pedidos, pedido):
    en_preparacion = pedidos.avanzar_estado(pedido.id, EstadoPedido.EN_PREPARACION, "maria")
    assert en_preparacion.estado is EstadoPedido.EN_PREPARACION
    listo = pedidos.avanzar_estado(pedido.id, EstadoPedido.LISTO_PARA_RETIRAR, "juan")
    assert listo.estado is EstadoPedido.LISTO_PARA_RETIRAR


def test_cada_cambio_de_estado_queda_en_el_historial_con_fecha_y_responsable(pedidos, pedido):
    pedidos.avanzar_estado(pedido.id, EstadoPedido.EN_PREPARACION, "maria")
    pedidos.avanzar_estado(pedido.id, EstadoPedido.LISTO_PARA_RETIRAR, "juan")
    assert [(c.estado, c.usuario, c.fecha) for c in pedidos.historial(pedido.id)] == [
        (EstadoPedido.PENDIENTE, "cliente", "2026-01-01 10:00:00"),
        (EstadoPedido.EN_PREPARACION, "maria", "2026-01-01 10:00:01"),
        (EstadoPedido.LISTO_PARA_RETIRAR, "juan", "2026-01-01 10:00:02"),
    ]


TRANSICIONES_NO_PERMITIDAS = [
    (origen, destino) for origen in EstadoPedido for destino in EstadoPedido
    if destino is not origen.siguiente() and destino is not EstadoPedido.ENTREGADO
]


@pytest.mark.parametrize("origen, destino", TRANSICIONES_NO_PERMITIDAS,
                         ids=[f"{o.name}-a-{d.name}" for o, d in TRANSICIONES_NO_PERMITIDAS])
def test_no_se_puede_saltar_retroceder_ni_repetir_un_estado(pedidos, pedido, origen, destino):
    _llevar_a(pedidos, pedido, origen)
    cambios_antes = len(pedidos.historial(pedido.id))
    with pytest.raises(TransicionEstadoInvalidaError, match="no puede pasar"):
        pedidos.avanzar_estado(pedido.id, destino, "maria")
    assert pedidos.obtener(pedido.id).estado is origen
    assert len(pedidos.historial(pedido.id)) == cambios_antes


@pytest.mark.parametrize("origen", list(EstadoPedido))
def test_avanzar_estado_nunca_permite_marcar_como_entregado(pedidos, pedido, origen):
    _llevar_a(pedidos, pedido, origen)
    with pytest.raises(TransicionEstadoInvalidaError):
        pedidos.avanzar_estado(pedido.id, EstadoPedido.ENTREGADO, "maria")
    assert pedidos.obtener(pedido.id).estado is origen


def test_marcar_como_entregado_sin_codigo_indica_que_hay_que_verificarlo(pedidos, pedido):
    _llevar_a(pedidos, pedido, EstadoPedido.LISTO_PARA_RETIRAR)
    with pytest.raises(TransicionEstadoInvalidaError, match="código de retiro"):
        pedidos.avanzar_estado(pedido.id, EstadoPedido.ENTREGADO, "maria")


def test_avanzar_un_pedido_inexistente_falla(pedidos):
    with pytest.raises(PedidoNoEncontradoError):
        pedidos.avanzar_estado(999, EstadoPedido.EN_PREPARACION, "maria")


def test_dos_empleados_no_pueden_aplicar_el_mismo_avance(pedidos, pedido, monkeypatch):
    desactualizado = pedidos.obtener(pedido.id)
    pedidos.avanzar_estado(pedido.id, EstadoPedido.EN_PREPARACION, "maria")
    # El segundo empleado todavía ve el pedido como Pendiente cuando guarda su cambio.
    monkeypatch.setattr(pedidos, "obtener", lambda _id: desactualizado)
    with pytest.raises(TransicionEstadoInvalidaError, match="otro usuario"):
        pedidos.avanzar_estado(pedido.id, EstadoPedido.EN_PREPARACION, "juan")
    assert [c.usuario for c in pedidos.historial(pedido.id)] == ["cliente", "maria"]


# ------------------------------------------------------------------------ entrega
@pytest.mark.parametrize("presentar", [
    lambda codigo: codigo,
    lambda codigo: codigo.lower(),
    lambda codigo: f" {codigo[:3]}-{codigo[3:]} ".lower(),
    lambda codigo: f"{codigo[:2]} {codigo[2:4]} {codigo[4:]}",
], ids=["exacto", "minusculas", "con-guion-y-espacios", "con-espacios"])
def test_la_entrega_acepta_el_codigo_sin_importar_mayusculas_espacios_o_guiones(pedidos, pedido, presentar):
    _llevar_a(pedidos, pedido, EstadoPedido.LISTO_PARA_RETIRAR)
    entregado = pedidos.entregar_pedido(pedido.id, presentar(pedido.codigo_retiro), "juan")
    assert entregado.estado is EstadoPedido.ENTREGADO
    ultimo = pedidos.historial(pedido.id)[-1]
    assert (ultimo.estado, ultimo.usuario) == (EstadoPedido.ENTREGADO, "juan")


@pytest.mark.parametrize("codigo", ["ZZZZZZ", "", None, "K7Q"])
def test_un_codigo_que_no_corresponde_impide_la_entrega(pedidos, pedido, codigo):
    _llevar_a(pedidos, pedido, EstadoPedido.LISTO_PARA_RETIRAR)
    with pytest.raises(EntregaInvalidaError, match="no corresponde"):
        pedidos.entregar_pedido(pedido.id, codigo, "juan")
    assert pedidos.obtener(pedido.id).estado is EstadoPedido.LISTO_PARA_RETIRAR


def test_el_codigo_de_otro_pedido_no_sirve(catalogo, pedidos, pedido, cliente):
    otro = pedidos.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    _llevar_a(pedidos, pedido, EstadoPedido.LISTO_PARA_RETIRAR)
    _llevar_a(pedidos, otro, EstadoPedido.LISTO_PARA_RETIRAR)
    with pytest.raises(EntregaInvalidaError, match="no corresponde"):
        pedidos.entregar_pedido(pedido.id, otro.codigo_retiro, "juan")
    assert pedidos.obtener(pedido.id).estado is EstadoPedido.LISTO_PARA_RETIRAR
    assert pedidos.obtener(otro.id).estado is EstadoPedido.LISTO_PARA_RETIRAR


@pytest.mark.parametrize("estado", [EstadoPedido.PENDIENTE, EstadoPedido.EN_PREPARACION])
def test_solo_se_entregan_pedidos_listos_aunque_el_codigo_sea_correcto(pedidos, pedido, estado):
    _llevar_a(pedidos, pedido, estado)
    with pytest.raises(EntregaInvalidaError, match="solo se entregan pedidos Listos"):
        pedidos.entregar_pedido(pedido.id, pedido.codigo_retiro, "juan")
    assert pedidos.obtener(pedido.id).estado is estado


def test_un_pedido_ya_entregado_no_se_entrega_otra_vez(pedidos, pedido):
    _llevar_a(pedidos, pedido, EstadoPedido.ENTREGADO)
    with pytest.raises(EntregaInvalidaError, match="Entregado"):
        pedidos.entregar_pedido(pedido.id, pedido.codigo_retiro, "juan")
    assert [c.estado for c in pedidos.historial(pedido.id)].count(EstadoPedido.ENTREGADO) == 1


def test_entregar_un_pedido_inexistente_falla(pedidos):
    with pytest.raises(PedidoNoEncontradoError):
        pedidos.entregar_pedido(999, "ABCDEF", "juan")


def test_dos_empleados_no_pueden_entregar_el_mismo_pedido(pedidos, pedido, monkeypatch):
    _llevar_a(pedidos, pedido, EstadoPedido.LISTO_PARA_RETIRAR)
    desactualizado = pedidos.obtener(pedido.id)
    pedidos.entregar_pedido(pedido.id, pedido.codigo_retiro, "maria")
    monkeypatch.setattr(pedidos, "obtener", lambda _id: desactualizado)
    with pytest.raises(TransicionEstadoInvalidaError, match="otro usuario"):
        pedidos.entregar_pedido(pedido.id, pedido.codigo_retiro, "juan")
    assert [c.estado for c in pedidos.historial(pedido.id)].count(EstadoPedido.ENTREGADO) == 1


# ----------------------------------------------------------------- buscar por código
def test_el_pedido_se_busca_por_el_codigo_que_presenta_el_cliente(pedidos, pedido):
    presentado = f" {pedido.codigo_retiro[:3]}-{pedido.codigo_retiro[3:]} ".lower()
    assert pedidos.buscar_por_codigo(presentado).id == pedido.id


@pytest.mark.parametrize("codigo", ["ZZZZZZ", "", None])
def test_buscar_un_codigo_inexistente_falla(pedidos, pedido, codigo):
    with pytest.raises(PedidoNoEncontradoError, match="código de retiro"):
        pedidos.buscar_por_codigo(codigo)
