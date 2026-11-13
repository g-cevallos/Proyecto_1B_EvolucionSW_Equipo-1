"""Repositorios: traducen entre filas de SQLite y entidades del dominio.

Los repositorios no aplican reglas de negocio; solo leen y escriben datos.
Las transacciones las controla la capa de servicios.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Iterable, Optional

from app.dominio.modelos import (
    CambioEstado,
    Categoria,
    Cliente,
    DetallePedido,
    EstadoPedido,
    Pedido,
    Producto,
)


def _a_producto(fila: sqlite3.Row) -> Producto:
    return Producto(
        id=fila["id"],
        codigo=fila["codigo"],
        nombre=fila["nombre"],
        categoria=Categoria(fila["categoria"]),
        precio_centavos=fila["precio_centavos"],
        disponible=bool(fila["disponible"]),
    )


def _a_cliente(fila: sqlite3.Row) -> Cliente:
    return Cliente(
        id=fila["id"],
        codigo=fila["codigo"],
        nombre=fila["nombre"],
        apellido=fila["apellido"],
        cedula=fila["cedula"],
        celular=fila["celular"],
        correo=fila["correo"],
    )


class ProductoRepositorio:
    """Acceso a la tabla ``producto``."""

    def __init__(self, conexion: sqlite3.Connection):
        self._con = conexion

    def listar(self, solo_disponibles: bool = False) -> list[Producto]:
        """Lista productos ordenados por categoría y nombre."""
        sql = "SELECT * FROM producto"
        if solo_disponibles:
            sql += " WHERE disponible = 1"
        sql += " ORDER BY categoria, nombre"
        return [_a_producto(f) for f in self._con.execute(sql)]

    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        """Devuelve el producto con el código indicado o ``None``."""
        fila = self._con.execute("SELECT * FROM producto WHERE codigo = ?", (codigo,)).fetchone()
        return _a_producto(fila) if fila else None

    def obtener_por_codigos(self, codigos: Iterable[str]) -> dict[str, Producto]:
        """Devuelve un diccionario código → producto para los códigos existentes."""
        codigos = list(codigos)
        if not codigos:
            return {}
        # La lista viaja como un único parámetro JSON: la sentencia SQL es fija y no
        # se construye concatenando texto (evita el aviso B608 de inyección SQL).
        filas = self._con.execute(
            "SELECT * FROM producto WHERE codigo IN (SELECT value FROM json_each(?))",
            (json.dumps(codigos),),
        )
        return {f["codigo"]: _a_producto(f) for f in filas}

    def crear(self, producto: Producto) -> Producto:
        """Inserta un producto y devuelve la entidad con su ``id``."""
        cursor = self._con.execute(
            "INSERT INTO producto (codigo, nombre, categoria, precio_centavos, disponible) "
            "VALUES (?, ?, ?, ?, ?)",
            (producto.codigo, producto.nombre, producto.categoria.value,
             producto.precio_centavos, int(producto.disponible)),
        )
        producto.id = cursor.lastrowid
        return producto

    def actualizar(self, producto: Producto) -> None:
        """Actualiza nombre, categoría, precio y disponibilidad de un producto."""
        self._con.execute(
            "UPDATE producto SET nombre = ?, categoria = ?, precio_centavos = ?, disponible = ? "
            "WHERE codigo = ?",
            (producto.nombre, producto.categoria.value, producto.precio_centavos,
             int(producto.disponible), producto.codigo),
        )

    def contar(self) -> int:
        """Número total de productos registrados."""
        return self._con.execute("SELECT COUNT(*) FROM producto").fetchone()[0]


class ClienteRepositorio:
    """Acceso a la tabla ``cliente``."""

    def __init__(self, conexion: sqlite3.Connection):
        self._con = conexion

    def crear(self, cliente: Cliente) -> Cliente:
        """Inserta el cliente y le asigna un código con formato ``CLI-00001``."""
        cursor = self._con.execute(
            "INSERT INTO cliente (nombre, apellido, cedula, celular, correo) VALUES (?, ?, ?, ?, ?)",
            (cliente.nombre, cliente.apellido, cliente.cedula, cliente.celular, cliente.correo),
        )
        cliente.id = cursor.lastrowid
        cliente.codigo = f"CLI-{cliente.id:05d}"
        self._con.execute("UPDATE cliente SET codigo = ? WHERE id = ?", (cliente.codigo, cliente.id))
        return cliente

    def obtener_por_id(self, cliente_id: int) -> Optional[Cliente]:
        """Devuelve el cliente con el ``id`` indicado o ``None``."""
        fila = self._con.execute("SELECT * FROM cliente WHERE id = ?", (cliente_id,)).fetchone()
        return _a_cliente(fila) if fila else None

    def obtener_por_cedula(self, cedula: str) -> Optional[Cliente]:
        """Devuelve el cliente con la cédula indicada o ``None``."""
        fila = self._con.execute("SELECT * FROM cliente WHERE cedula = ?", (cedula,)).fetchone()
        return _a_cliente(fila) if fila else None

    def existe_correo(self, correo: str) -> bool:
        """Indica si el correo ya está registrado."""
        return self._con.execute("SELECT 1 FROM cliente WHERE correo = ?", (correo,)).fetchone() is not None
