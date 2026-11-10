"""
Fixtures compartidas de pytest para las pruebas de Sauce Demo.

pytest carga este archivo automaticamente: las fixtures definidas aqui estan
disponibles en test_saucedemo.py sin importarlas.
"""

import time

import pytest
from selenium import webdriver

from paginas import CLAVE_VALIDA, USUARIO_VALIDO, InventoryPage, LoginPage

PAUSA_VISUAL = 2  # segundos que el navegador queda abierto al final (0 = sin pausa)


@pytest.fixture
def driver():
    """Abre Chrome antes de cada prueba y lo cierra al terminar."""
    opciones = webdriver.ChromeOptions()
    opciones.add_argument("--window-size=1280,800")
    opciones.add_argument("--incognito")
    # Evita el aviso de "cambiar contrasena" de Chrome, que puede tapar la pagina.
    opciones.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    # opciones.add_argument("--headless=new")  # descomentar para no ver el navegador
    navegador = webdriver.Chrome(options=opciones)
    yield navegador
    time.sleep(PAUSA_VISUAL)
    navegador.quit()


@pytest.fixture
def login_page(driver):
    """Pagina de login ya abierta."""
    pagina = LoginPage(driver)
    pagina.abrir()
    return pagina


@pytest.fixture
def inventario(driver, login_page):
    """Sesion iniciada con un usuario valido; devuelve la pagina de productos."""
    login_page.iniciar_sesion(USUARIO_VALIDO, CLAVE_VALIDA)
    pagina = InventoryPage(driver)
    pagina.obtener_titulo()  # espera a que la pagina de productos haya cargado
    return pagina
