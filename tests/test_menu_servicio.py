"""Pruebas del servicio de menú: consulta y mantenimiento de productos."""

import pytest

from app.dominio.excepciones import ProductoDuplicadoError, ProductoNoEncontradoError, ValidacionError
from app.dominio.modelos import Categoria
from app.persistencia.repositorios import ProductoRepositorio


# ---------------------------------------------------------------------- registrar
def test_registrar_producto_normaliza_los_datos_y_lo_guarda(menu):
    producto = menu.registrar_producto(" caf1 ", "  Café   pasado ", "bebida", "1,50", True)
    assert producto.id is not None
    assert (producto.codigo, producto.nombre, producto.categoria, producto.precio_centavos, producto.disponible) == (
        "CAF1", "Café pasado", Categoria.BEBIDA, 150, True)
    assert menu.obtener("CAF1").id == producto.id


def test_producto_no_disponible_se_guarda_pero_no_aparece_en_el_menu_del_cliente(menu):
    menu.registrar_producto("ALM1", "Almuerzo", "ALIMENTO", "3.50", False)
    assert [p.codigo for p in menu.listar_todos()] == ["ALM1"]
    assert menu.listar_menu() == []


def test_no_se_puede_registrar_dos_veces_el_mismo_codigo(catalogo):
    with pytest.raises(ProductoDuplicadoError, match="CAF1"):
        catalogo.registrar_producto("caf1", "Otro café", "BEBIDA", "2.00", True)
    assert catalogo.obtener("CAF1").nombre == "Café pasado"
    assert len(catalogo.listar_todos()) == 4


@pytest.mark.parametrize("cambios", [
    {"codigo": "A"},
    {"codigo": "AB CD"},
    {"nombre": "A"},
    {"nombre": "   "},
    {"nombre": "x" * 81},
    {"categoria": "POSTRE"},
    {"categoria": ""},
    {"categoria": None},
    {"precio": "0"},
    {"precio": "abc"},
    {"precio": "1.555"},
])
def test_datos_invalidos_no_registran_nada(menu, cambios):
    datos = {"codigo": "CAF1", "nombre": "Café", "categoria": "BEBIDA", "precio": "1.50", "disponible": True}
    datos.update(cambios)
    with pytest.raises(ValidacionError):
        menu.registrar_producto(**datos)
    assert menu.listar_todos() == []


def test_si_otro_usuario_registra_el_mismo_codigo_a_la_vez_se_informa_el_duplicado(catalogo, monkeypatch):
    # Simula que la verificación previa no vio el producto que otro usuario insertó un instante antes.
    monkeypatch.setattr(ProductoRepositorio, "obtener_por_codigo", lambda self, codigo: None)
    with pytest.raises(ProductoDuplicadoError):
        catalogo.registrar_producto("CAF1", "Otro café", "BEBIDA", "2.00", True)
    assert len(catalogo.listar_todos()) == 4


# ------------------------------------------------------------------------ obtener
def test_obtener_acepta_el_codigo_en_minusculas_y_con_espacios(catalogo):
    assert catalogo.obtener(" caf1 ").codigo == "CAF1"


@pytest.mark.parametrize("codigo", ["NOEXISTE", "", None])
def test_obtener_un_producto_inexistente_falla(catalogo, codigo):
    with pytest.raises(ProductoNoEncontradoError):
        catalogo.obtener(codigo)


# ----------------------------------------------------------------------- listados
def test_el_menu_del_cliente_muestra_solo_disponibles_agrupados_por_categoria(catalogo):
    assert [p.codigo for p in catalogo.listar_menu()] == ["SAN1", "AGU1", "CAF1"]


def test_el_personal_ve_todos_los_productos(catalogo):
    assert [p.codigo for p in catalogo.listar_todos()] == ["ALM1", "SAN1", "AGU1", "CAF1"]


# --------------------------------------------------------------------- actualizar
def test_actualizar_cambia_nombre_categoria_precio_y_disponibilidad(catalogo):
    actualizado = catalogo.actualizar_producto("CAF1", "Café con leche", "ALIMENTO", "2.00", False)
    leido = catalogo.obtener("CAF1")
    assert (actualizado.nombre, leido.nombre) == ("Café con leche", "Café con leche")
    assert (leido.categoria, leido.precio_centavos, leido.disponible) == (Categoria.ALIMENTO, 200, False)
    assert "CAF1" not in [p.codigo for p in catalogo.listar_menu()]


@pytest.mark.parametrize("cambios", [{"nombre": "A"}, {"categoria": "POSTRE"}, {"precio": "0"}, {"precio": "x"}])
def test_una_actualizacion_invalida_conserva_los_valores_anteriores(catalogo, cambios):
    datos = {"nombre": "Café nuevo", "categoria": "BEBIDA", "precio": "9.99", "disponible": True}
    datos.update(cambios)
    with pytest.raises(ValidacionError):
        catalogo.actualizar_producto("CAF1", **datos)
    leido = catalogo.obtener("CAF1")
    assert (leido.nombre, leido.precio_centavos) == ("Café pasado", 150)


def test_actualizar_un_producto_inexistente_falla(menu):
    with pytest.raises(ProductoNoEncontradoError):
        menu.actualizar_producto("NOEXISTE", "Nombre", "BEBIDA", "1.00", True)


# ------------------------------------------------------------------ disponibilidad
def test_cambiar_disponibilidad_quita_y_devuelve_el_producto_al_menu(catalogo):
    assert catalogo.cambiar_disponibilidad("CAF1", False).disponible is False
    assert "CAF1" not in [p.codigo for p in catalogo.listar_menu()]
    assert catalogo.cambiar_disponibilidad("CAF1", True).disponible is True
    assert "CAF1" in [p.codigo for p in catalogo.listar_menu()]


def test_cambiar_disponibilidad_de_un_producto_inexistente_falla(menu):
    with pytest.raises(ProductoNoEncontradoError):
        menu.cambiar_disponibilidad("NOEXISTE", True)
