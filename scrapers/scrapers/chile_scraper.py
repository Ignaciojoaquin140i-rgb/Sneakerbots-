import logging
import re
import httpx
from bs4 import BeautifulSoup
from config import TIENDAS_CHILE, CATEGORIAS_CHILE, DESCUENTO_MINIMO_CHILE
from notifier import notificar, formato_chile

logger = logging.getLogger(__name__)
_ya_notificados: set = set()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-CL,es;q=0.9",
}

def _limpiar_precio(texto: str) -> int:
    numeros = re.sub(r"[^\d]", "", texto)
    return int(numeros) if numeros else 0

def _calcular_descuento(normal: int, oferta: int) -> int:
    if normal <= 0 or oferta <= 0 or oferta >= normal:
        return 0
    return round((1 - oferta / normal) * 100)

def _scrape_falabella(categoria: str) -> list[dict]:
    productos = []
    url = f"https://www.falabella.com/falabella-cl/category/{categoria}?sortBy=discount&isFiltered=true"
    try:
        with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("[class*='product-card'], [class*='ProductCard'], .pod")
        for item in items:
            try:
                titulo_el = item.select_one("[class*='product-name'], [class*='title'], .pod-title")
                precio_normal_el = item.select_one("[class*='original-price'], [class*='price-original'], .line-through")
                precio_oferta_el = item.select_one("[class*='offer-price'], [class*='price-offer'], [class*='sale-price']")
                url_el = item.select_one("a")
                img_el = item.select_one("img")
                if not all([titulo_el, precio_normal_el, precio_oferta_el, url_el]):
                    continue
                titulo = titulo_el.get_text(strip=True)
                precio_normal = _limpiar_precio(precio_normal_el.get_text())
                precio_oferta = _limpiar_precio(precio_oferta_el.get_text())
                descuento = _calcular_descuento(precio_normal, precio_oferta)
                href = url_el.get("href", "")
                link = href if href.startswith("http") else f"https://www.falabella.com{href}"
                imagen = img_el.get("src", "") if img_el else ""
                if descuento >= DESCUENTO_MINIMO_CHILE:
                    productos.append({"tienda": "Falabella", "titulo": titulo, "precio_normal": precio_normal, "precio_oferta": precio_oferta, "descuento": descuento, "url": link, "imagen": imagen, "categoria": categoria})
            except Exception as e:
                logger.debug(f"Falabella item error: {e}")
    except Exception as e:
        logger.error(f"Error scrapeando Falabella ({categoria}): {e}")
    return productos

def _scrape_ripley(categoria: str) -> list[dict]:
    productos = []
    url = f"https://simple.ripley.cl/{categoria}?sortBy=discountPercentage"
    try:
        with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
            resp = client.get(url)
            resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".catalog-product-item, .product-item, [class*='ProductCard']")
        for item in items:
            try:
                titulo_el = item.select_one(".catalog-product-details__name, .product-name, h3")
                precio_normal_el = item.select_one(".catalog-prices__before, .price-before, [class*='price-original']")
                precio_oferta_el = item.select_one(".catalog-prices__price, .price-now, [class*='price-sale']")
                url_el = item.select_one("a")
                img_el = item.select_one("
