"""Pruebas del registro de pedidos: selección, importe, confirmación y consulta del cliente."""

import sqlite3

import pytest

from app.dominio.excepciones import (
    CantidadInvalidaError,
    PedidoNoEncontradoError,
    PedidoVacioError,
    ProductoNoDisponibleError,
    ProductoNoEncontradoError,
    TotalDesactualizadoError,
)
from app.dominio.modelos import EstadoPedido
from app.servicios.generador_codigo import ALFABETO
from app.servicios.pedido_servicio import INTENTOS_CODIGO, PedidoServicio


# --------------------------------------------------------- interpretar las cantidades
def test_los_campos_vacios_o_en_cero_no_forman_parte_de_la_seleccion(pedidos):
    entradas = {"A": "", "B": "0", "C": "   ", "D": None, "E": "3"}
    assert pedidos.interpretar_cantidades(entradas) == {"E": 3}


def test_las_cantidades_se_convierten_a_enteros_ignorando_espacios(pedidos):
    assert pedidos.interpretar_cantidades({"CAF1": " 2 ", "SAN1": "10"}) == {"CAF1": 2, "SAN1": 10}


@pytest.mark.parametrize("texto", ["-1", "1.5", "1,5", "abc", "1e2", "+2", "2 3", "٣"])
def test_una_cantidad_que_no_es_entero_positivo_se_rechaza(pedidos, texto):
    with pytest.raises(CantidadInvalidaError, match="entero positivo"):
        pedidos.interpretar_cantidades({"SAN1": texto})


def test_el_mensaje_de_cantidad_invalida_indica_el_producto(pedidos):
    with pytest.raises(CantidadInvalidaError, match="SAN1"):
        pedidos.interpretar_cantidades({"SAN1": "x"})


# ------------------------------------------------------------------ calcular el resumen
def test_el_total_es_la_suma_de_precio_por_cantidad(catalogo, pedidos):
    resumen = pedidos.calcular_resumen({"CAF1": 2, "SAN1": 1})
    assert resumen.total_centavos == 550
    assert [(d.codigo_producto, d.cantidad, d.precio_unitario_centavos, d.subtotal_centavos)
            for d in resumen.detalles] == [("CAF1", 2, 150, 300), ("SAN1", 1, 250, 250)]


def test_el_resumen_usa_el_precio_vigente(catalogo, pedidos):
    catalogo.actualizar_producto("CAF1", "Café pasado", "BEBIDA", "2.00", True)
    assert pedidos.calcular_resumen({"CAF1": 2, "SAN1": 1}).total_centavos == 650


def test_una_seleccion_vacia_se_rechaza(catalogo, pedidos):
    with pytest.raises(PedidoVacioError, match="al menos un producto"):
        pedidos.calcular_resumen({})


@pytest.mark.parametrize("cantidad", [0, -1, True, 1.5, "2", None])
def test_una_cantidad_que_no_es_entero_positivo_no_forma_un_resumen(catalogo, pedidos, cantidad):
    with pytest.raises(CantidadInvalidaError):
        pedidos.calcular_resumen({"CAF1": cantidad})


def test_la_cantidad_maxima_es_configurable(catalogo, conexion):
    servicio = PedidoServicio(conexion, cantidad_maxima=5)
    assert servicio.calcular_resumen({"CAF1": 5}).total_centavos == 750
    with pytest.raises(CantidadInvalidaError, match="máxima por producto es 5"):
        servicio.calcular_resumen({"CAF1": 6})


def test_por_defecto_se_permiten_hasta_cincuenta_unidades(catalogo, pedidos):
    assert pedidos.calcular_resumen({"AGU1": 50}).total_centavos == 3750
    with pytest.raises(CantidadInvalidaError):
        pedidos.calcular_resumen({"AGU1": 51})


def test_un_producto_inexistente_se_rechaza(catalogo, pedidos):
    with pytest.raises(ProductoNoEncontradoError, match="ZZZ"):
        pedidos.calcular_resumen({"CAF1": 1, "ZZZ": 1})


def test_un_producto_no_disponible_se_rechaza(catalogo, pedidos):
    with pytest.raises(ProductoNoDisponibleError, match="Almuerzo del día"):
        pedidos.calcular_resumen({"CAF1": 1, "ALM1": 1})


# ------------------------------------------------------------------ confirmar el pedido
def test_confirmar_registra_un_pedido_pendiente_con_su_codigo_de_retiro(pedido, cliente):
    assert pedido.id is not None
    assert (pedido.cliente_id, pedido.estado, pedido.total_centavos) == (cliente.id, EstadoPedido.PENDIENTE, 550)
    assert len(pedido.codigo_retiro) == 6 and set(pedido.codigo_retiro) <= set(ALFABETO)
    assert pedido.fecha_registro == "2026-01-01 10:00:00"
    assert pedido.cliente_nombre == "Ana Torres"


def test_el_pedido_guarda_el_detalle_con_el_precio_de_ese_momento(pedido):
    assert [(d.codigo_producto, d.nombre_producto, d.cantidad, d.precio_unitario_centavos)
            for d in pedido.detalles] == [("CAF1", "Café pasado", 2, 150), ("SAN1", "Sánduche de pollo", 1, 250)]


def test_el_historial_empieza_con_el_registro_del_cliente(pedido, pedidos):
    assert [(c.estado, c.usuario, c.fecha) for c in pedidos.historial(pedido.id)] == [
        (EstadoPedido.PENDIENTE, "cliente", "2026-01-01 10:00:00")]


@pytest.mark.parametrize("total_mostrado", [None, 0, 549, 551])
def test_si_el_total_mostrado_no_coincide_el_pedido_no_se_registra(catalogo, pedidos, cliente, total_mostrado):
    with pytest.raises(TotalDesactualizadoError):
        pedidos.confirmar_pedido(cliente.id, {"CAF1": 2, "SAN1": 1}, total_mostrado)
    assert pedidos.listar_pedidos() == []


def test_si_el_precio_cambia_mientras_el_cliente_revisa_debe_confirmar_otra_vez(catalogo, pedidos, cliente):
    items = {"CAF1": 2, "SAN1": 1}
    total_revisado = pedidos.calcular_resumen(items).total_centavos
    catalogo.actualizar_producto("CAF1", "Café pasado", "BEBIDA", "2.00", True)
    with pytest.raises(TotalDesactualizadoError, match=r"\$6\.50"):
        pedidos.confirmar_pedido(cliente.id, items, total_revisado)
    assert pedidos.listar_pedidos() == []
    assert pedidos.confirmar_pedido(cliente.id, items, 650).total_centavos == 650


def test_si_un_producto_deja_de_estar_disponible_antes_de_confirmar_no_se_registra(catalogo, pedidos, cliente):
    catalogo.cambiar_disponibilidad("SAN1", False)
    with pytest.raises(ProductoNoDisponibleError):
        pedidos.confirmar_pedido(cliente.id, {"CAF1": 2, "SAN1": 1}, 550)
    assert pedidos.listar_pedidos() == []


def test_al_confirmar_tambien_se_aplica_la_cantidad_maxima(catalogo, pedidos, cliente):
    with pytest.raises(CantidadInvalidaError):
        pedidos.confirmar_pedido(cliente.id, {"AGU1": 51}, 3825)


def test_un_cambio_posterior_de_precio_no_altera_pedidos_ya_registrados(catalogo, pedidos, pedido):
    catalogo.actualizar_producto("CAF1", "Café pasado", "BEBIDA", "9.00", True)
    guardado = pedidos.obtener(pedido.id)
    assert guardado.total_centavos == 550
    assert [d.precio_unitario_centavos for d in guardado.detalles] == [150, 250]


# ------------------------------------------------------------- códigos de retiro únicos
def test_si_el_codigo_generado_ya_existe_se_genera_otro(catalogo, conexion, reloj, cliente):
    codigos = iter(["AAAAAA", "AAAAAA", "BBBBBB"])
    servicio = PedidoServicio(conexion, generador_codigo=lambda: next(codigos), reloj=reloj)
    primero = servicio.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    segundo = servicio.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    assert (primero.codigo_retiro, segundo.codigo_retiro) == ("AAAAAA", "BBBBBB")


def test_si_no_se_consigue_un_codigo_unico_el_pedido_no_se_registra(catalogo, conexion, reloj, cliente):
    llamadas = []

    def repetido():
        llamadas.append(1)
        return "AAAAAA"

    servicio = PedidoServicio(conexion, generador_codigo=repetido, reloj=reloj)
    servicio.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    llamadas.clear()
    with pytest.raises(RuntimeError, match="código de retiro único"):
        servicio.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    assert len(llamadas) == INTENTOS_CODIGO
    assert len(servicio.listar_pedidos()) == 1


def test_muchos_pedidos_reciben_codigos_distintos(catalogo, pedidos, cliente):
    codigos = [pedidos.confirmar_pedido(cliente.id, {"AGU1": 1}, 75).codigo_retiro for _ in range(40)]
    assert len(set(codigos)) == 40
    assert all(set(codigo) <= set(ALFABETO) for codigo in codigos)


def test_un_cliente_inexistente_no_puede_registrar_pedidos(catalogo, pedidos):
    with pytest.raises(sqlite3.IntegrityError):
        pedidos.confirmar_pedido(999, {"AGU1": 1}, 75)
    assert pedidos.listar_pedidos() == []


# ------------------------------------------------------------ consulta del cliente
def test_el_cliente_ve_solo_sus_pedidos_del_mas_reciente_al_mas_antiguo(catalogo, pedidos, cliente, otro_cliente):
    primero = pedidos.confirmar_pedido(cliente.id, {"AGU1": 1}, 75)
    ajeno = pedidos.confirmar_pedido(otro_cliente.id, {"CAF1": 1}, 150)
    segundo = pedidos.confirmar_pedido(cliente.id, {"SAN1": 1}, 250)
    assert [p.id for p in pedidos.consultar_pedidos_cliente(cliente.id)] == [segundo.id, primero.id]
    assert [p.id for p in pedidos.consultar_pedidos_cliente(otro_cliente.id)] == [ajeno.id]


def test_un_cliente_sin_pedidos_recibe_una_lista_vacia(pedidos, cliente):
    assert pedidos.consultar_pedidos_cliente(cliente.id) == []


def test_el_cliente_consulta_el_detalle_de_su_pedido(pedidos, pedido, cliente):
    assert pedidos.consultar_pedido_cliente(cliente.id, pedido.id).codigo_retiro == pedido.codigo_retiro


def test_un_cliente_no_puede_consultar_el_pedido_de_otro(pedidos, pedido, otro_cliente):
    with pytest.raises(PedidoNoEncontradoError, match="No se encontró"):
        pedidos.consultar_pedido_cliente(otro_cliente.id, pedido.id)


def test_consultar_un_pedido_inexistente_falla_con_el_mismo_mensaje(pedidos, cliente):
    with pytest.raises(PedidoNoEncontradoError, match="No se encontró"):
        pedidos.consultar_pedido_cliente(cliente.id, 999)
