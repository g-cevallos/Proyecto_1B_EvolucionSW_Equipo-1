"""Rutas del cliente: registro, menú, pedido y consulta de estado (RU-01 a RU-05)."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.dominio.excepciones import ErrorNegocio
from app.web.comun import ruta_local, servicio_clientes, servicio_menu

bp = Blueprint("cliente", __name__)

CAMPOS_REGISTRO = ("nombre", "apellido", "cedula", "celular", "correo")


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    """Formulario de registro de un cliente nuevo."""
    datos = {campo: request.form.get(campo, "") for campo in CAMPOS_REGISTRO}
    if request.method == "POST":
        try:
            cliente = servicio_clientes().registrar(**datos)
        except ErrorNegocio as error:
            flash(error.mensaje, "error")
            return render_template("cliente/registro.html", datos=datos), 422
        _iniciar_sesion(cliente)
        flash(f"Registro completo. Su código de cliente es {cliente.codigo}.", "exito")
        return redirect(url_for("cliente.menu"))
    return render_template("cliente/registro.html", datos=datos)


@bp.route("/ingresar", methods=["GET", "POST"])
def ingresar():
    """Identificación del cliente con cédula y correo institucional."""
    siguiente = ruta_local(request.values.get("siguiente"), url_for("cliente.menu"))
    if request.method == "POST":
        try:
            cliente = servicio_clientes().identificar(request.form.get("cedula", ""),
                                                      request.form.get("correo", ""))
        except ErrorNegocio as error:
            flash(error.mensaje, "error")
            return render_template("cliente/ingresar.html", siguiente=siguiente,
                                   cedula=request.form.get("cedula", "")), 401
        _iniciar_sesion(cliente)
        return redirect(siguiente)
    return render_template("cliente/ingresar.html", siguiente=siguiente, cedula="")


@bp.route("/salir", methods=["POST"])
def salir():
    """Cierra la sesión del cliente."""
    for clave in ("cliente_id", "cliente_nombre", "cliente_codigo", "carrito"):
        session.pop(clave, None)
    return redirect(url_for("inicio"))


@bp.route("/menu")
def menu():
    """Menú con productos disponibles y precios (RU-01) y selección de cantidades (RU-02)."""
    return render_template("cliente/menu.html", productos=servicio_menu().listar_menu(),
                           cantidades=session.get("carrito", {}))


def _iniciar_sesion(cliente) -> None:
    session["cliente_id"] = cliente.id
    session["cliente_nombre"] = cliente.nombre_completo
    session["cliente_codigo"] = cliente.codigo
