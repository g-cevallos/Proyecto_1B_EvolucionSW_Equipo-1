"""Pruebas del esquema SQLite, sus restricciones y los repositorios."""

import sqlite3

import pytest

from app.datos_demo import PRODUCTOS_DEMO, cargar_datos_demo
from app.dominio.modelos import Categoria, Cliente, DetallePedido, EstadoPedido, Pedido, Producto
from app.persistencia.db import conectar, crear_esquema
from app.persistencia.repositorios import (
    ClienteRepositorio,
    PedidoRepositorio,
    PersonalRepositorio,
    ProductoRepositorio,
)

TABLAS = {"producto", "cliente", "pedido", "detalle_pedido", "historial_estado", "personal"}


def _producto(codigo="CAF1", nombre="Café", categoria=Categoria.BEBIDA, precio=150, disponible=True):
    return Producto(codigo, nombre, categoria, precio, disponible)


def _cliente(cedula="1710034065", correo="ana@epn.edu.ec"):
    return Cliente("Ana", "Torres", cedula, "0991234567", correo)


@pytest.fixture
def repositorios(conexion):
    """Repositorios de productos, clientes y pedidos sobre la base en memoria."""
    return ProductoRepositorio(conexion), ClienteRepositorio(conexion), PedidoRepositorio(conexion)


def _pedido(cliente_id, producto, codigo="AAAAAA", estado=EstadoPedido.PENDIENTE, cantidad=2):
    detalle = DetallePedido(producto.id, producto.codigo, producto.nombre, cantidad, producto.precio_centavos)
    return Pedido(codigo, cliente_id, estado, "2026-01-01 10:00:00", detalle.subtotal_centavos, [detalle])


# ----------------------------------------------------------------- conexión y esquema
def test_el_esquema_crea_todas_las_tablas(conexion):
    nombres = {fila["name"] for fila in conexion.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    assert TABLAS <= nombres


def test_crear_el_esquema_dos_veces_no_falla_ni_borra_datos(conexion):
    ProductoRepositorio(conexion).crear(_producto())
    conexion.commit()
    crear_esquema(conexion)
    assert ProductoRepositorio(conexion).contar() == 1


def test_la_conexion_activa_las_claves_foraneas_y_acceso_por_nombre(conexion):
    assert conexion.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert conexion.execute("SELECT 1 AS uno").fetchone()["uno"] == 1


def test_los_datos_persisten_al_reabrir_el_archivo(tmp_path):
    ruta = str(tmp_path / "datos.db")
    primera = conectar(ruta)
    crear_esquema(primera)
    with primera:
        ProductoRepositorio(primera).crear(_producto())
        ClienteRepositorio(primera).crear(_cliente())
    primera.close()

    segunda = conectar(ruta)
    try:
        assert ProductoRepositorio(segunda).obtener_por_codigo("CAF1").nombre == "Café"
        assert ClienteRepositorio(segunda).obtener_por_cedula("1710034065").correo == "ana@epn.edu.ec"
    finally:
        segunda.close()


# ------------------------------------------------------------------ restricciones
def test_no_se_repite_el_codigo_de_producto(conexion, repositorios):
    productos, _, _ = repositorios
    productos.crear(_producto())
    with pytest.raises(sqlite3.IntegrityError):
        productos.crear(_producto(nombre="Otro"))


@pytest.mark.parametrize("campo, valor", [
    ("categoria", "POSTRE"), ("precio_centavos", 0), ("precio_centavos", -5), ("disponible", 2),
])
def test_la_base_rechaza_productos_con_datos_fuera_de_rango(conexion, campo, valor):
    fila = {"codigo": "X1", "nombre": "X", "categoria": "BEBIDA", "precio_centavos": 100, "disponible": 1}
    fila[campo] = valor
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute("INSERT INTO producto (codigo, nombre, categoria, precio_centavos, disponible) "
                         "VALUES (:codigo, :nombre, :categoria, :precio_centavos, :disponible)", fila)


def test_no_se_repiten_la_cedula_ni_el_correo_de_un_cliente(repositorios):
    _, clientes, _ = repositorios
    clientes.crear(_cliente())
    with pytest.raises(sqlite3.IntegrityError):
        clientes.crear(_cliente(correo="otro@epn.edu.ec"))
    with pytest.raises(sqlite3.IntegrityError):
        clientes.crear(_cliente(cedula="0100000009"))


def test_un_pedido_exige_un_cliente_existente(repositorios):
    productos, _, pedidos = repositorios
    producto = productos.crear(_producto())
    with pytest.raises(sqlite3.IntegrityError):
        pedidos.crear(_pedido(999, producto), "cliente")


def test_no_se_repite_el_codigo_de_retiro(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    pedidos.crear(_pedido(cliente.id, producto), "cliente")
    with pytest.raises(sqlite3.IntegrityError):
        pedidos.crear(_pedido(cliente.id, producto), "cliente")


def test_la_base_rechaza_estados_y_cantidades_invalidos(conexion, repositorios):
    productos, clientes, _ = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute("INSERT INTO pedido (codigo_retiro, cliente_id, estado, fecha_registro, total_centavos) "
                         "VALUES ('ZZZZZZ', ?, 'CANCELADO', 'hoy', 100)", (cliente.id,))
    conexion.execute("INSERT INTO pedido (codigo_retiro, cliente_id, estado, fecha_registro, total_centavos) "
                     "VALUES ('YYYYYY', ?, 'PENDIENTE', 'hoy', 100)", (cliente.id,))
    with pytest.raises(sqlite3.IntegrityError):
        conexion.execute("INSERT INTO detalle_pedido (pedido_id, producto_id, codigo_producto, nombre_producto, "
                         "cantidad, precio_unitario_centavos) VALUES (1, ?, 'CAF1', 'Café', 0, 150)", (producto.id,))


def test_al_borrar_un_pedido_se_borran_su_detalle_y_su_historial(conexion, repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    pedido = pedidos.crear(_pedido(cliente.id, producto), "cliente")
    conexion.execute("DELETE FROM pedido WHERE id = ?", (pedido.id,))
    assert conexion.execute("SELECT COUNT(*) FROM detalle_pedido").fetchone()[0] == 0
    assert conexion.execute("SELECT COUNT(*) FROM historial_estado").fetchone()[0] == 0


# ------------------------------------------------------------ ProductoRepositorio
def test_listar_ordena_por_categoria_y_luego_por_nombre(repositorios):
    productos, _, _ = repositorios
    productos.crear(_producto("B2", "Té", Categoria.BEBIDA))
    productos.crear(_producto("A2", "Pan", Categoria.ALIMENTO))
    productos.crear(_producto("B1", "Agua", Categoria.BEBIDA))
    productos.crear(_producto("A1", "Bolón", Categoria.ALIMENTO))
    assert [p.codigo for p in productos.listar()] == ["A1", "A2", "B1", "B2"]


def test_listar_solo_disponibles_omite_los_demas(repositorios):
    productos, _, _ = repositorios
    productos.crear(_producto("A1"))
    productos.crear(_producto("A2", disponible=False))
    assert [p.codigo for p in productos.listar(solo_disponibles=True)] == ["A1"]
    assert len(productos.listar()) == 2


def test_obtener_por_codigo_devuelve_el_producto_o_none(repositorios):
    productos, _, _ = repositorios
    creado = productos.crear(_producto())
    assert productos.obtener_por_codigo("CAF1").id == creado.id
    assert productos.obtener_por_codigo("NOEXISTE") is None


def test_obtener_por_codigos_devuelve_solo_los_existentes(repositorios):
    productos, _, _ = repositorios
    productos.crear(_producto("A1"))
    productos.crear(_producto("A2"))
    assert set(productos.obtener_por_codigos(["A1", "A2", "ZZ"])) == {"A1", "A2"}
    assert productos.obtener_por_codigos([]) == {}


def test_obtener_por_codigos_trata_el_texto_como_dato_y_no_como_sql(repositorios):
    productos, _, _ = repositorios
    productos.crear(_producto("A1"))
    assert productos.obtener_por_codigos(["A1'); DROP TABLE producto;--"]) == {}
    assert productos.contar() == 1


def test_actualizar_modifica_nombre_categoria_precio_y_disponibilidad(repositorios):
    productos, _, _ = repositorios
    producto = productos.crear(_producto())
    producto.nombre, producto.categoria = "Café con leche", Categoria.ALIMENTO
    producto.precio_centavos, producto.disponible = 200, False
    productos.actualizar(producto)
    leido = productos.obtener_por_codigo("CAF1")
    assert (leido.nombre, leido.categoria, leido.precio_centavos, leido.disponible) == (
        "Café con leche", Categoria.ALIMENTO, 200, False)


def test_contar_productos(repositorios):
    productos, _, _ = repositorios
    assert productos.contar() == 0
    productos.crear(_producto("A1"))
    assert productos.contar() == 1


# ------------------------------------------------------------- ClienteRepositorio
def test_el_codigo_de_cliente_es_secuencial_con_cinco_digitos(repositorios):
    _, clientes, _ = repositorios
    primero = clientes.crear(_cliente())
    segundo = clientes.crear(_cliente("0100000009", "luis@epn.edu.ec"))
    assert (primero.codigo, segundo.codigo) == ("CLI-00001", "CLI-00002")


def test_consultas_de_clientes(repositorios):
    _, clientes, _ = repositorios
    creado = clientes.crear(_cliente())
    assert clientes.obtener_por_id(creado.id).cedula == "1710034065"
    assert clientes.obtener_por_id(999) is None
    assert clientes.obtener_por_cedula("1710034065").id == creado.id
    assert clientes.obtener_por_cedula("0000000000") is None
    assert clientes.existe_correo("ana@epn.edu.ec") is True
    assert clientes.existe_correo("nadie@epn.edu.ec") is False


# -------------------------------------------------------------- PedidoRepositorio
def test_crear_pedido_guarda_detalles_historial_y_nombre_del_cliente(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    creado = pedidos.crear(_pedido(cliente.id, producto), "cliente")
    leido = pedidos.obtener(creado.id)
    assert leido.cliente_nombre == "Ana Torres"
    assert leido.total_centavos == 300
    assert [(d.codigo_producto, d.cantidad, d.precio_unitario_centavos) for d in leido.detalles] == [("CAF1", 2, 150)]
    assert [(c.estado, c.usuario) for c in pedidos.historial(creado.id)] == [(EstadoPedido.PENDIENTE, "cliente")]


def test_consultas_de_pedidos_por_id_y_por_codigo(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    creado = pedidos.crear(_pedido(cliente.id, producto, "K7Q2MX"), "cliente")
    assert pedidos.obtener_por_codigo("K7Q2MX").id == creado.id
    assert pedidos.obtener_por_codigo("OTRO11") is None
    assert pedidos.obtener(999) is None
    assert pedidos.existe_codigo("K7Q2MX") is True
    assert pedidos.existe_codigo("OTRO11") is False


def test_actualizar_estado_solo_si_el_pedido_sigue_en_el_estado_esperado(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    creado = pedidos.crear(_pedido(cliente.id, producto), "cliente")
    assert pedidos.actualizar_estado(creado.id, EstadoPedido.PENDIENTE, EstadoPedido.EN_PREPARACION) is True
    assert pedidos.actualizar_estado(creado.id, EstadoPedido.PENDIENTE, EstadoPedido.EN_PREPARACION) is False
    assert pedidos.obtener(creado.id).estado is EstadoPedido.EN_PREPARACION


def test_listados_de_pedidos_por_orden_de_llegada_y_por_cliente(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    ana = clientes.crear(_cliente())
    luis = clientes.crear(_cliente("0100000009", "luis@epn.edu.ec"))
    primero = pedidos.crear(_pedido(ana.id, producto, "AAAAAA"), "cliente")
    segundo = pedidos.crear(_pedido(luis.id, producto, "BBBBBB"), "cliente")
    tercero = pedidos.crear(_pedido(ana.id, producto, "CCCCCC"), "cliente")
    assert [p.id for p in pedidos.listar()] == [primero.id, segundo.id, tercero.id]
    assert [p.id for p in pedidos.listar_por_cliente(ana.id)] == [tercero.id, primero.id]
    pedidos.actualizar_estado(segundo.id, EstadoPedido.PENDIENTE, EstadoPedido.EN_PREPARACION)
    assert [p.id for p in pedidos.listar(EstadoPedido.EN_PREPARACION)] == [segundo.id]


def test_contar_por_estado_incluye_los_estados_vacios(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    pedidos.crear(_pedido(cliente.id, producto, "AAAAAA"), "cliente")
    pedidos.crear(_pedido(cliente.id, producto, "BBBBBB"), "cliente")
    assert pedidos.contar_por_estado() == {
        EstadoPedido.PENDIENTE: 2, EstadoPedido.EN_PREPARACION: 0,
        EstadoPedido.LISTO_PARA_RETIRAR: 0, EstadoPedido.ENTREGADO: 0,
    }


def test_el_historial_se_devuelve_en_orden_cronologico(repositorios):
    productos, clientes, pedidos = repositorios
    producto = productos.crear(_producto())
    cliente = clientes.crear(_cliente())
    creado = pedidos.crear(_pedido(cliente.id, producto), "cliente")
    pedidos.registrar_historial(creado.id, EstadoPedido.EN_PREPARACION, "2026-01-01 10:05:00", "maria")
    assert [(c.estado, c.usuario) for c in pedidos.historial(creado.id)] == [
        (EstadoPedido.PENDIENTE, "cliente"), (EstadoPedido.EN_PREPARACION, "maria")]


# ------------------------------------------------------------ PersonalRepositorio
def test_repositorio_del_personal(conexion):
    personal = PersonalRepositorio(conexion)
    assert personal.contar() == 0
    assert personal.obtener("maria") is None
    personal.crear("maria", "María Pérez", "hash-de-prueba")
    fila = personal.obtener("maria")
    assert (fila["nombre"], fila["hash_clave"]) == ("María Pérez", "hash-de-prueba")
    assert personal.contar() == 1
    with pytest.raises(sqlite3.IntegrityError):
        personal.crear("maria", "Otra", "otro-hash")


# ---------------------------------------------------------------------- datos demo
def test_los_datos_demo_se_cargan_solo_si_el_menu_esta_vacio(conexion):
    assert cargar_datos_demo(conexion) == len(PRODUCTOS_DEMO)
    assert ProductoRepositorio(conexion).contar() == len(PRODUCTOS_DEMO)
    assert cargar_datos_demo(conexion) == 0
    assert ProductoRepositorio(conexion).contar() == len(PRODUCTOS_DEMO)


def test_los_datos_demo_no_se_cargan_si_ya_hay_un_producto(conexion):
    ProductoRepositorio(conexion).crear(_producto())
    assert cargar_datos_demo(conexion) == 0
    assert ProductoRepositorio(conexion).contar() == 1


def test_el_menu_demo_tiene_ambas_categorias_y_un_producto_no_disponible():
    assert {p.categoria for p in PRODUCTOS_DEMO} == set(Categoria)
    assert any(not p.disponible for p in PRODUCTOS_DEMO)
    assert len({p.codigo for p in PRODUCTOS_DEMO}) == len(PRODUCTOS_DEMO)
