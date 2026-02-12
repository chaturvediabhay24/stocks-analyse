import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import TELEGRAM_BOT_TOKEN
from core.formatter import escape_md
from core.registry import PluginRegistry

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "*Welcome to Stock Analyzer Bot\\!* 📈\n\n"
        "I can help you analyze NSE\\-listed Indian stocks "
        "with technical and fundamental analysis\\.\n\n"
        "*Commands:*\n"
        "/analyze — Analyze a stock\n"
        "/help — Show all commands\n\n"
        "Let's get started\\! Use /analyze"
    )
    await update.message.reply_text(welcome, parse_mode="MarkdownV2")


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register /start
    app.add_handler(CommandHandler("start", start))

    # Discover and register all plugins
    registry = PluginRegistry()
    registry.discover("plugins")
    registry.register_all(app)

    logger.info(
        "Bot started with %d plugins: %s",
        len(registry.plugins),
        ", ".join(p.name for p in registry.plugins),
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
