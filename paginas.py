"""
Page Objects de Sauce Demo (https://www.saucedemo.com).

Cada clase representa una pagina de la aplicacion y reune sus localizadores y
las acciones que se pueden hacer en ella. Las clases NO contienen aserciones:
las verificaciones se escriben en los casos de prueba (test_saucedemo.py).
"""

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---------------------------------------------------------------------------
# Configuracion y datos de prueba (credenciales publicas del sitio de practica)
# ---------------------------------------------------------------------------
BASE_URL = "https://www.saucedemo.com"
TIEMPO_ESPERA = 10  # segundos maximos de espera por un elemento

USUARIO_VALIDO = "standard_user"
CLAVE_VALIDA = "secret_sauce"

PRODUCTO_ID = "sauce-labs-backpack"      # identificador del producto en la pagina
PRODUCTO_NOMBRE = "Sauce Labs Backpack"  # nombre visible del producto


def paso(texto):
    """Imprime un paso en la consola para dejar evidencia de lo que hace el script."""
    print(f"  -> {texto}")


# ---------------------------------------------------------------------------
# Clase base: acciones comunes con esperas explicitas
# ---------------------------------------------------------------------------
class PaginaBase:
    def __init__(self, driver):
        self.driver = driver
        # Si un elemento queda obsoleto (la pagina se redibuja), la espera reintenta.
        self.espera = WebDriverWait(
            driver, TIEMPO_ESPERA, ignored_exceptions=(StaleElementReferenceException,)
        )

    def _visible(self, localizador):
        return self.espera.until(EC.visibility_of_element_located(localizador))

    def _clicable(self, localizador):
        return self.espera.until(EC.element_to_be_clickable(localizador))

    def escribir(self, localizador, texto):
        elemento = self._visible(localizador)
        elemento.clear()
        elemento.send_keys(texto)

    def clic(self, localizador):
        self._clicable(localizador).click()

    def texto(self, localizador):
        return self._visible(localizador).text


# ---------------------------------------------------------------------------
# Pagina de login
# ---------------------------------------------------------------------------
class LoginPage(PaginaBase):
    URL = f"{BASE_URL}/"

    CAMPO_USUARIO = (By.ID, "user-name")
    CAMPO_CLAVE = (By.ID, "password")
    BOTON_LOGIN = (By.ID, "login-button")
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def abrir(self):
        paso(f"Abriendo la pagina: {self.URL}")
        self.driver.get(self.URL)

    def iniciar_sesion(self, usuario, clave):
        paso(f"Escribiendo usuario: {usuario or '(vacio)'}")
        self.escribir(self.CAMPO_USUARIO, usuario)
        paso(f"Escribiendo contrasena: {'********' if clave else '(vacia)'}")
        self.escribir(self.CAMPO_CLAVE, clave)
        paso("Haciendo clic en el boton Login")
        self.clic(self.BOTON_LOGIN)

    def obtener_error(self):
        mensaje = self.texto(self.MENSAJE_ERROR)
        paso(f"Mensaje de error mostrado: {mensaje}")
        return mensaje

    def boton_login_visible(self):
        try:
            self._visible(self.BOTON_LOGIN)
            return True
        except TimeoutException:
            return False


# ---------------------------------------------------------------------------
# Pagina de productos (inventario)
# ---------------------------------------------------------------------------
class InventoryPage(PaginaBase):
    TITULO = (By.CSS_SELECTOR, ".title")
    ENLACE_CARRITO = (By.CSS_SELECTOR, ".shopping_cart_link")
    CONTADOR_CARRITO = (By.CSS_SELECTOR, ".shopping_cart_badge")
    BOTON_MENU = (By.ID, "react-burger-menu-btn")
    ENLACE_CERRAR_SESION = (By.ID, "logout_sidebar_link")

    def obtener_titulo(self):
        titulo = self.texto(self.TITULO)
        paso(f"Titulo de la pagina: {titulo}")
        return titulo

    def agregar_producto(self, producto_id):
        paso(f"Agregando al carrito el producto: {producto_id}")
        self.clic((By.ID, f"add-to-cart-{producto_id}"))

    def contador_carrito(self):
        """Devuelve el numero que muestra el icono del carrito (0 si no hay)."""
        try:
            elemento = WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.CONTADOR_CARRITO)
            )
            cantidad = int(elemento.text)
        except TimeoutException:
            cantidad = 0
        paso(f"Productos en el icono del carrito: {cantidad}")
        return cantidad

    def abrir_carrito(self):
        paso("Abriendo el carrito")
        self.clic(self.ENLACE_CARRITO)

    def cerrar_sesion(self):
        paso("Abriendo el menu lateral")
        self.clic(self.BOTON_MENU)
        paso("Haciendo clic en Logout")
        self.clic(self.ENLACE_CERRAR_SESION)


# ---------------------------------------------------------------------------
# Pagina del carrito
# ---------------------------------------------------------------------------
class CartPage(PaginaBase):
    NOMBRES_PRODUCTOS = (By.CSS_SELECTOR, ".inventory_item_name")
    BOTON_CHECKOUT = (By.ID, "checkout")

    def nombres_productos(self):
        # Los elementos se buscan de nuevo en cada intento: la pagina puede
        # redibujarse y dejar obsoletas las referencias ya encontradas.
        def leer(driver):
            textos = [e.text for e in driver.find_elements(*self.NOMBRES_PRODUCTOS)]
            return textos if any(textos) else False

        nombres = self.espera.until(leer)
        paso(f"Productos en el carrito: {nombres}")
        return nombres

    def ir_a_checkout(self):
        paso("Haciendo clic en Checkout")
        self.clic(self.BOTON_CHECKOUT)


# ---------------------------------------------------------------------------
# Paginas del proceso de compra (datos, resumen y confirmacion)
# ---------------------------------------------------------------------------
class CheckoutPage(PaginaBase):
    CAMPO_NOMBRE = (By.ID, "first-name")
    CAMPO_APELLIDO = (By.ID, "last-name")
    CAMPO_CODIGO_POSTAL = (By.ID, "postal-code")
    BOTON_CONTINUAR = (By.ID, "continue")
    BOTON_FINALIZAR = (By.ID, "finish")
    MENSAJE_ERROR = (By.CSS_SELECTOR, "[data-test='error']")
    TITULO_CONFIRMACION = (By.CSS_SELECTOR, ".complete-header")

    def llenar_datos(self, nombre, apellido, codigo_postal):
        paso(f"Llenando datos de envio: {nombre} {apellido}, {codigo_postal}")
        self.escribir(self.CAMPO_NOMBRE, nombre)
        self.escribir(self.CAMPO_APELLIDO, apellido)
        self.escribir(self.CAMPO_CODIGO_POSTAL, codigo_postal)

    def continuar(self):
        paso("Haciendo clic en Continue")
        self.clic(self.BOTON_CONTINUAR)

    def finalizar(self):
        paso("Haciendo clic en Finish")
        self.clic(self.BOTON_FINALIZAR)

    def obtener_error(self):
        mensaje = self.texto(self.MENSAJE_ERROR)
        paso(f"Mensaje de error mostrado: {mensaje}")
        return mensaje

    def obtener_confirmacion(self):
        mensaje = self.texto(self.TITULO_CONFIRMACION)
        paso(f"Mensaje de confirmacion: {mensaje}")
        return mensaje
