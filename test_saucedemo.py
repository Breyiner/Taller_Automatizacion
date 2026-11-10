"""
Pruebas funcionales automatizadas de Sauce Demo (https://www.saucedemo.com)
con Selenium + pytest.

Modulo probado: login, catalogo, carrito, compra y cierre de sesion.

Casos:
  CP-01  Login con credenciales validas
  CP-02  Login con usuario bloqueado
  CP-03  Login con contrasena incorrecta
  CP-04  Login con contrasena vacia
  CP-05  Login con usuario vacio
  CP-06  Agregar un producto al carrito
  CP-07  El producto agregado aparece en el carrito
  CP-08  Compra completa (checkout hasta la confirmacion)
  CP-09  Checkout sin llenar los datos
  CP-10  Cerrar sesion

Cada paso se imprime en la consola para poder documentarlo con capturas.
Ejecutar con:  py -m pytest -v -s
"""

import pytest

from paginas import (
    CLAVE_VALIDA,
    PRODUCTO_ID,
    PRODUCTO_NOMBRE,
    USUARIO_VALIDO,
    CartPage,
    CheckoutPage,
    LoginPage,
)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
def test_login_correcto(driver, login_page, inventario):
    """CP-01: Con credenciales validas se llega a la pagina de productos."""
    print("\n[CP-01] Login con credenciales validas")
    # La fixture 'inventario' ya inicio sesion con el usuario valido.
    assert "/inventory.html" in driver.current_url
    assert inventario.obtener_titulo() == "Texto incorrecto"


@pytest.mark.parametrize(
    "cp, usuario, clave, mensaje_esperado",
    [
        ("CP-02", "locked_out_user", CLAVE_VALIDA, "Sorry, this user has been locked out."),
        ("CP-03", USUARIO_VALIDO, "clave_incorrecta", "Username and password do not match any user in this service"),
        ("CP-04", USUARIO_VALIDO, "", "Password is required"),
        ("CP-05", "", CLAVE_VALIDA, "Username is required"),
    ],
    ids=["usuario_bloqueado", "clave_incorrecta", "clave_vacia", "usuario_vacio"],
)
def test_login_incorrecto(driver, login_page, cp, usuario, clave, mensaje_esperado):
    """CP-02 a CP-05: Con datos invalidos se muestra un error y no se accede."""
    print(f"\n[{cp}] Login incorrecto (esperado: {mensaje_esperado})")
    login_page.iniciar_sesion(usuario, clave)

    mensaje = login_page.obtener_error()
    assert mensaje_esperado in mensaje
    assert "/inventory.html" not in driver.current_url
    print("  -> Verificacion OK: se mostro el error y no se accedio")


# ---------------------------------------------------------------------------
# Carrito
# ---------------------------------------------------------------------------
def test_agregar_producto_al_carrito(inventario):
    """CP-06: Al agregar un producto, el icono del carrito muestra 1."""
    print("\n[CP-06] Agregar un producto al carrito")
    assert inventario.contador_carrito() == 0

    inventario.agregar_producto(PRODUCTO_ID)

    assert inventario.contador_carrito() == 1
    print("  -> Verificacion OK: el carrito paso de 0 a 1 producto")


def test_producto_aparece_en_el_carrito(driver, inventario):
    """CP-07: El producto agregado se ve en la pagina del carrito."""
    print("\n[CP-07] El producto agregado aparece en el carrito")
    inventario.agregar_producto(PRODUCTO_ID)
    inventario.abrir_carrito()

    carrito = CartPage(driver)
    nombres = carrito.nombres_productos()

    assert "/cart.html" in driver.current_url
    assert PRODUCTO_NOMBRE in nombres
    print("  -> Verificacion OK: el producto esta en el carrito")


# ---------------------------------------------------------------------------
# Compra
# ---------------------------------------------------------------------------
def test_compra_completa(driver, inventario):
    """CP-08: Se completa una compra y se muestra la confirmacion."""
    print("\n[CP-08] Compra completa")
    inventario.agregar_producto(PRODUCTO_ID)
    inventario.abrir_carrito()
    CartPage(driver).ir_a_checkout()

    checkout = CheckoutPage(driver)
    checkout.llenar_datos("Estudiante", "Prueba", "680001")
    checkout.continuar()
    checkout.finalizar()

    confirmacion = checkout.obtener_confirmacion()
    assert "checkout-complete" in driver.current_url
    assert "Thank you for your order" in confirmacion
    print("  -> Verificacion OK: la compra se confirmo")


def test_checkout_sin_datos(driver, inventario):
    """CP-09: Sin llenar los datos de envio, el checkout muestra un error."""
    print("\n[CP-09] Checkout sin llenar los datos")
    inventario.agregar_producto(PRODUCTO_ID)
    inventario.abrir_carrito()
    CartPage(driver).ir_a_checkout()

    checkout = CheckoutPage(driver)
    checkout.continuar()

    mensaje = checkout.obtener_error()
    assert "First Name is required" in mensaje
    assert "checkout-step-one" in driver.current_url
    print("  -> Verificacion OK: se mostro el error y no se avanzo")


# ---------------------------------------------------------------------------
# Sesion
# ---------------------------------------------------------------------------
def test_cerrar_sesion(driver, inventario):
    """CP-10: Al cerrar sesion se vuelve a la pagina de login."""
    print("\n[CP-10] Cerrar sesion")
    inventario.cerrar_sesion()

    login = LoginPage(driver)
    assert login.boton_login_visible()
    assert "/inventory.html" not in driver.current_url
    print("  -> Verificacion OK: se volvio a la pagina de login")
