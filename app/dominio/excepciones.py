"""Excepciones de negocio de la cafetería.

Todas heredan de :class:`ErrorNegocio`, de modo que la capa web puede capturarlas
en un solo lugar y mostrar su mensaje al usuario.
"""


class ErrorNegocio(Exception):
    """Error base de todas las violaciones de reglas o validaciones del dominio.

    Attributes:
        mensaje: Texto comprensible para el usuario final.
    """

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class ValidacionError(ErrorNegocio):
    """Un dato ingresado no cumple el formato o rango esperado."""


class PedidoVacioError(ErrorNegocio):
    """El pedido no contiene productos."""


class CantidadInvalidaError(ErrorNegocio):
    """La cantidad de un producto no es un entero positivo."""


class ProductoNoDisponibleError(ErrorNegocio):
    """Se intentó pedir un producto no disponible."""


class ProductoNoEncontradoError(ErrorNegocio):
    """El código de producto no existe en el menú."""


class ProductoDuplicadoError(ErrorNegocio):
    """Ya existe un producto con el mismo código."""


class TotalDesactualizadoError(ErrorNegocio):
    """El total mostrado al cliente ya no coincide con los precios vigentes."""


class TransicionEstadoInvalidaError(ErrorNegocio):
    """El cambio de estado solicitado no respeta el orden permitido."""


class EntregaInvalidaError(ErrorNegocio):
    """El pedido no puede entregarse: estado incorrecto o código no coincide."""


class PedidoNoEncontradoError(ErrorNegocio):
    """No existe un pedido con el identificador o código indicado."""


class ClienteDuplicadoError(ErrorNegocio):
    """Ya existe un cliente con la misma cédula o correo."""


class CredencialesInvalidasError(ErrorNegocio):
    """Los datos de acceso no corresponden a un usuario registrado."""
