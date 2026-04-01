import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update
from scrapers.ebay_scraper import buscar_jordan_ebay
from scrapers.chile_scraper import buscar_ofertas_chile
from config import TELEGRAM_TOKEN, INTERVALO_MINUTOS

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"👋 ¡Hola! Bot de ofertas activo.\n\n"
        f"🆔 Tu Chat ID es: <code>{chat_id}</code>\n\n"
        f"📋 Comandos:\n"
        f"/buscar_ebay — Buscar Jordan Retro OG ahora\n"
        f"/buscar_chile — Buscar fallos de precio ahora\n"
        f"/estado — Ver configuración\n"
        f"/ayuda — Todos los comandos",
        parse_mode="HTML"
    )

async def cmd_buscar_ebay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Buscando en eBay... te aviso si encuentro algo.")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, buscar_jordan_ebay)

async def cmd_buscar_chile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Revisando tiendas chilenas...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, buscar_ofertas_chile)

async def cmd_estado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"⚙️ <b>Estado del bot</b>\n\n"
        f"⏱ Revisión cada {INTERVALO_MINUTOS} minutos\n"
        f"👟 eBay: Jordan Retro OG bajo $100 USD\n"
        f"🇨🇱 Tiendas: Falabella, Ripley, Paris, PC Factory, AbcDin\n"
        f"💥 Descuento mínimo Chile: 40%",
        parse_mode="HTML"
    )

async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 <b>Comandos disponibles</b>\n\n"
        "/start — Iniciar bot y ver tu Chat ID\n"
        "/buscar_ebay — Buscar Jordan Retro OG en eBay ahora\n"
        "/buscar_chile — Revisar tiendas chilenas ahora\n"
        "/estado — Ver configuración actual\n"
        "/ayuda — Este mensaje",
        parse_mode="HTML"
    )

def tarea_programada():
    logger.info("⏰ Revisión automática iniciada...")
    buscar_jordan_ebay()
    buscar_ofertas_chile()

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("buscar_ebay", cmd_buscar_ebay))
    app.add_handler(CommandHandler("buscar_chile", cmd_buscar_chile))
    app.add_handler(CommandHandler("estado", cmd_estado))
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(tarea_programada, "interval", minutes=INTERVALO_MINUTOS)
    scheduler.start()

    logger.info(f"🚀 Bot iniciado. Revisión cada {INTERVALO_MINUTOS} minutos.")
    app.run_polling()

if __name__ == "__main__":
    main()
