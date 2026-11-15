"""Elementos compartidos de la capa web: conexión por petición, CSRF, filtros y errores."""

from __future__ import annotations

import functools
import sqlite3

from flask import current_app, g, redirect, request, session, url_for

from app.persistencia.db import conectar
from app.servicios.cliente_servicio import ClienteServicio
from app.servicios.menu_servicio import MenuServicio
from app.servicios.pedido_servicio import PedidoServicio


def obtener_conexion() -> sqlite3.Connection:
    """Conexión SQLite asociada a la petición actual (se cierra al terminarla)."""
    if "db" not in g:
        g.db = conectar(current_app.config["DATABASE"])
    return g.db


def servicio_menu() -> MenuServicio:
    """Servicio de menú para la petición actual."""
    return MenuServicio(obtener_conexion())


def servicio_pedidos() -> PedidoServicio:
    """Servicio de pedidos para la petición actual."""
    return PedidoServicio(obtener_conexion(), cantidad_maxima=current_app.config["CANTIDAD_MAXIMA"])


def servicio_clientes() -> ClienteServicio:
    """Servicio de clientes para la petición actual."""
    return ClienteServicio(obtener_conexion(), current_app.config["DOMINIO_CORREO"])


def cliente_requerido(vista):
    """Decorador: exige que el cliente se haya identificado."""
    @functools.wraps(vista)
    def envoltura(*args, **kwargs):
        if "cliente_id" not in session:
            return redirect(url_for("cliente.ingresar", siguiente=request.path))
        return vista(*args, **kwargs)
    return envoltura


def personal_requerido(vista):
    """Decorador: exige una sesión del personal de cafetería."""
    @functools.wraps(vista)
    def envoltura(*args, **kwargs):
        if "personal_usuario" not in session:
            return redirect(url_for("personal.ingresar"))
        return vista(*args, **kwargs)
    return envoltura


def ruta_local(destino: str | None, por_defecto: str) -> str:
    """Acepta solo rutas internas para evitar redirecciones abiertas."""
    if destino and destino.startswith("/") and not destino.startswith("//"):
        return destino
    return por_defecto
