"""Prueba de sistema con navegador que genera las capturas del manual de usuario.

Levanta la aplicación con una base de datos nueva y temporal, recorre en Chromium el flujo
completo de un cliente y del personal (registro, pedido, confirmación, atención, entrega y
mantenimiento del menú), comprueba en cada paso que la pantalla muestre lo esperado y guarda
las 16 capturas que usa ``docs/08_manual_usuario.md``.

Uso (con las dependencias de desarrollo instaladas)::

    python -m playwright install chromium
    python scripts/capturas.py docs/img

La variable de entorno ``CAPTURAS_NAVEGADOR`` permite indicar la ruta de otro ejecutable de
Chrome o Chromium. Si una comprobación falla, el script termina con un error.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# pylint: disable=wrong-import-position
from playwright.sync_api import Page, sync_playwright  # noqa: E402
from werkzeug.serving import make_server  # noqa: E402

from app import create_app  # noqa: E402

PUERTO = 5055
URL = f"http://127.0.0.1:{PUERTO}"
OPCIONES = {"viewport": {"width": 1280, "height": 800}, "color_scheme": "light",
            "locale": "es-EC", "reduced_motion": "reduce"}


class Recorrido:
    """Recorre la aplicación como cliente y como personal, comprueba cada paso y toma capturas."""

    def __init__(self, salida: Path):
        self.salida = salida

    def foto(self, pagina: Page, nombre: str, completa: bool = False) -> None:
        """Guarda la captura de la página actual."""
        pagina.wait_for_timeout(500)
        pagina.screenshot(path=str(self.salida / nombre), full_page=completa)
        print(f"  ✓ {nombre}")

    @staticmethod
    def comprobar(pagina: Page, texto: str) -> None:
        """Falla si la página no contiene el texto esperado."""
        if texto not in pagina.inner_text("body"):
            raise AssertionError(f"No se encontró «{texto}» en {pagina.url}")

    @staticmethod
    def registrar(pagina: Page, datos: dict[str, str]) -> None:
        """Completa el formulario de registro de un cliente."""
        pagina.goto(URL + "/registro")
        for campo, valor in datos.items():
            pagina.fill(f"#{campo}", valor)

    @staticmethod
    def pedir(pagina: Page, cantidades: dict[str, int]) -> str:
        """Registra un pedido completo y devuelve su código de retiro."""
        pagina.goto(URL + "/menu")
        for codigo, cantidad in cantidades.items():
            pagina.fill(f"#cant_{codigo}", str(cantidad))
        pagina.click("text=Revisar pedido")
        pagina.click("text=Confirmar pedido")
        return pagina.inner_text("#codigo-retiro").strip()

    def clientes(self, cli: Page, luis: Page) -> str:
        """Flujo del cliente: registro, pedido, confirmación y aviso de error."""
        cli.goto(URL)
        self.foto(cli, "01_inicio.png")

        self.registrar(cli, {"nombre": "Ana", "apellido": "Pérez", "cedula": "1710034065",
                             "celular": "0991234567", "correo": "ana.perez@epn.edu.ec"})
        self.foto(cli, "02_registro.png", True)
        cli.click("button:has-text('Crear mi cuenta')")
        self.comprobar(cli, "Registro completo. Su código de cliente es CLI-00001.")

        cli.fill("#cant_A01", "2")
        cli.fill("#cant_B02", "1")
        self.foto(cli, "03_menu.png", True)
        cli.click("text=Revisar pedido")
        self.comprobar(cli, "$6.75")
        self.foto(cli, "04_revisar.png")
        cli.click("text=Confirmar pedido")
        self.comprobar(cli, "Pedido confirmado")
        codigo = cli.inner_text("#codigo-retiro").strip()
        self.foto(cli, "05_confirmado.png", True)

        # Se quita el límite del navegador para que el aviso lo dé el servidor.
        cli.goto(URL + "/menu")
        cli.evaluate("document.querySelector('#cant_A03').removeAttribute('max')")
        cli.fill("#cant_A03", "51")
        cli.click("text=Revisar pedido")
        self.comprobar(cli, "La cantidad máxima por producto es 50.")
        cli.evaluate("window.scrollTo(0, 0)")
        self.foto(cli, "06_error_cantidad.png")

        self.registrar(luis, {"nombre": "Luis", "apellido": "Mora", "cedula": "1705123451",
                              "celular": "0987654321", "correo": "luis.mora@epn.edu.ec"})
        luis.click("button:has-text('Crear mi cuenta')")
        self.pedir(luis, {"B01": 1, "A03": 1})
        self.pedir(cli, {"B03": 2})
        return codigo

    def personal(self, per: Page, cli: Page, codigo: str) -> None:
        """Flujo del personal: atención, entrega con código y mantenimiento del menú."""
        per.goto(URL + "/personal/ingresar")
        per.fill("#usuario", "admin")
        per.fill("#clave", "cafeteria2026")
        self.foto(per, "07_personal_ingreso.png")
        per.click("button:has-text('Ingresar')")
        self.comprobar(per, "Pedido #1")
        self.foto(per, "08_pedidos_pendientes.png", True)

        per.click("button:has-text('Iniciar preparación') >> nth=0")
        self.comprobar(per, "Pedido #1 ahora está «En preparación».")
        per.goto(URL + "/personal/pedidos?estado=EN_PREPARACION")
        self.foto(per, "09_en_preparacion.png", True)
        per.click("button:has-text('Marcar listo para retirar') >> nth=0")
        self.comprobar(per, "Pedido #1 ahora está «Listo para retirar».")

        cli.goto(URL + "/mis-pedidos")
        self.foto(cli, "10_mis_pedidos.png", True)

        per.goto(URL + "/personal/entrega")
        per.fill("#codigo", codigo.lower())
        per.click("button:has-text('Buscar pedido')")
        self.comprobar(per, "Pedido #1 · Ana Pérez")
        self.foto(per, "11_entrega_busqueda.png", True)
        per.click("button:has-text('Registrar entrega')")
        self.comprobar(per, "Pedido #1 de Ana Pérez registrado como Entregado.")
        self.foto(per, "12_entrega_registrada.png")

        cli.goto(URL + "/mis-pedidos/1")
        self.comprobar(cli, "Entregado")
        self.foto(cli, "13_seguimiento_entregado.png", True)

        per.goto(URL + "/personal/productos")
        self.foto(per, "14_productos.png", True)
        per.click("text=Agregar producto")
        per.fill("#codigo", "B05")
        per.fill("#nombre", "Té de hierbas")
        per.select_option("#categoria", "BEBIDA")
        per.fill("#precio", "0.90")
        self.foto(per, "15_nuevo_producto.png", True)


def main() -> None:
    """Levanta la aplicación en un hilo, ejecuta el recorrido y detiene el servidor."""
    salida = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/img")
    salida.mkdir(parents=True, exist_ok=True)
    temporal = tempfile.mkdtemp()
    aplicacion = create_app({"DATABASE": os.path.join(temporal, "cafeteria.db"),
                             "SECRET_KEY": "solo-para-capturas", "CARGAR_DATOS_DEMO": True})
    servidor = make_server("127.0.0.1", PUERTO, aplicacion, threaded=True)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    recorrido = Recorrido(salida)
    print(f"Capturas en {salida}:")
    try:
        with sync_playwright() as playwright:
            navegador = playwright.chromium.launch(executable_path=os.environ.get("CAPTURAS_NAVEGADOR"))
            cli, luis, per = (navegador.new_context(**OPCIONES).new_page() for _ in range(3))
            codigo = recorrido.clientes(cli, luis)
            recorrido.personal(per, cli, codigo)
            movil = navegador.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2,
                                          is_mobile=True, color_scheme="light", locale="es-EC",
                                          reduced_motion="reduce").new_page()
            movil.goto(URL + "/menu")
            recorrido.foto(movil, "16_menu_movil.png")
            navegador.close()
    finally:
        servidor.shutdown()
    print("Recorrido completo: todas las comprobaciones pasaron.")


if __name__ == "__main__":
    main()
