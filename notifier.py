import asyncio
import logging
from telegram import Bot
from telegram.constants import ParseMode
from config import TELEGRAM_TOKEN, CHAT_ID

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

async def enviar_mensaje(texto: str, foto_url: str = None):
    try:
        if foto_url:
            await bot.send_photo(
                chat_id=CHAT_ID,
                photo=foto_url,
                caption=texto,
                parse_mode=ParseMode.HTML,
            )
        else:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=texto,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
        logger.info("Notificación enviada correctamente.")
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")

def notificar(texto: str, foto_url: str = None):
    asyncio.run(enviar_mensaje(texto, foto_url))

def formato_ebay(producto: dict) -> str:
    return (
        f"👟 <b>OFERTA EBAY — Jordan Retro OG</b>\n\n"
        f"🏷️ <b>{producto['titulo']}</b>\n"
        f"💵 <b>${producto['precio']} {producto['moneda']}</b>\n"
        f"🚚 Envío: {producto.get('envio', 'Consultar')}\n"
        f"🛒 Vendedor: {producto.get('vendedor', 'N/A')}\n\n"
        f"🔗 <a href=\"{producto['url']}\">Ver en eBay</a>"
    )

def formato_chile(producto: dict) -> str:
    precio_normal_fmt = f"${producto['precio_normal']:,}".replace(",", ".")
    precio_oferta_fmt = f"${producto['precio_oferta']:,}".replace(",", ".")
    return (
        f"🔥 <b>FALLO DE PRECIO — {producto['tienda']}</b>\n\n"
        f"📱 <b>{producto['titulo']}</b>\n"
        f"📂 Categoría: {producto['categoria']}\n\n"
        f"~~{precio_normal_fmt}~~ → <b>{precio_oferta_fmt} CLP</b>\n"
        f"💥 <b>{producto['descuento']}% de descuento</b>\n\n"
        f"🔗 <a href=\"{producto['url']}\">Ver oferta en {producto['tienda']}</a>"
    )
