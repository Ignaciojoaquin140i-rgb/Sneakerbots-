import logging
import httpx
from bs4 import BeautifulSoup
from config import EBAY_BUSQUEDAS, EBAY_MAX_PRECIO_USD
from notifier import notificar, formato_ebay

logger = logging.getLogger(__name__)
_ya_notificados: set = set()

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "es-419,es;q=0.9,en;q=0.8",
}

def _construir_url(query: str) -> str:
    q = query.replace(" ", "+")
    return (
        f"https://www.ebay.com/sch/i.html"
        f"?_nkw={q}"
        f"&_sacat=15709"
        f"&_udhi={EBAY_MAX_PRECIO_USD}"
        f"&LH_BIN=1"
        f"&LH_ItemCondition=3"
        f"&_sop=15"
    )

def _parsear_resultados(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    productos = []
    items = soup.select("li.s-item")
    for item in items:
        try:
            titulo_el = item.select_one(".s-item__title span")
            if not titulo_el:
                continue
            titulo = titulo_el.get_text(strip=True)
            if "Shop on eBay" in titulo:
                continue
            precio_el = item.select_one(".s-item__price")
            if not precio_el:
                continue
            precio_texto = precio_el.get_text(strip=True)
            if " to " in precio_texto:
                precio_texto = precio_texto.split(" to ")[0]
            precio_texto = precio_texto.replace("$", "").replace(",", "").strip()
            precio = float(precio_texto)
            if precio > EBAY_MAX_PRECIO_USD:
                continue
            url_el = item.select_one("a.s-item__link")
            url = url_el["href"] if url_el else ""
            img_el = item.select_one("img.s-item__image-img")
            imagen = img_el.get("src", "") if img_el else ""
            vendedor_el = item.select_one(".s-item__seller-info-text")
            vendedor = vendedor_el.get_text(strip=True) if vendedor_el else "N/A"
            envio_el = item.select_one(".s-item__shipping")
            envio = envio_el.get_text(strip=True) if envio_el else "Consultar"
            productos.append({
                "titulo": titulo,
                "precio": precio,
                "moneda": "USD",
                "url": url,
                "imagen": imagen,
                "vendedor": vendedor,
                "envio": envio,
            })
        except Exception as e:
            logger.debug(f"Error parseando item: {e}")
            continue
    return productos

def buscar_jordan_ebay():
    logger.info("🔍 Buscando Jordan Retro OG en eBay...")
    nuevas = 0
    for query in EBAY_BUSQUEDAS:
        url = _construir_url(query)
        try:
            with httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True) as client:
                resp = client.get(url)
                resp.raise_for_status()
            productos = _parsear_resultados(resp.text)
            logger.info(f"  [{query}] → {len(productos)} resultado(s)")
            for p in productos:
                if p["url"] not in _ya_notificados:
                    _ya_notificados.add(p["url"])
                    mensaje = formato_ebay(p)
                    notificar(mensaje, foto_url=p["imagen"] if p["imagen"] else None)
                    nuevas += 1
        except Exception as e:
            logger.error(f"Error buscando '{query}' en eBay: {e}")
    logger.info(f"✅ eBay: {nuevas} nueva(s) oferta(s) notificada(s).")
