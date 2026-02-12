import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from core.analysis import technical_analysis, fundamental_analysis, piotroski_fscore, canslim_analysis
from core.base_plugin import BasePlugin
from core.formatter import build_message, chunk_message, escape_md

logger = logging.getLogger(__name__)

AWAITING_SYMBOL, AWAITING_ANALYSIS_TYPE = range(2)


def _sections_to_telegram(title: str, generator) -> str:
    """Convert analysis generator output to a Telegram-formatted message."""
    sections = []
    for section_data in generator:
        section_name = section_data["section"]
        is_summary = section_data.get("is_summary", False)

        if not is_summary:
            sections.append((f"— {section_name} —", ""))

        for row in section_data["rows"]:
            sections.append((row["label"], row["value"]))

        sections.append(("", ""))

    return build_message(title, sections)


class StockAnalysisPlugin(BasePlugin):

    def __init__(self, registry):
        self.registry = registry

    @property
    def name(self) -> str:
        return "Stock Analysis"

    @property
    def description(self) -> str:
        return "Technical & fundamental analysis for NSE stocks. Use /analyze"

    async def _start_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "Send me a stock symbol to analyze\\.\n"
            "Examples: `RELIANCE`, `TCS`, `INFY`, `HDFCBANK`",
            parse_mode="MarkdownV2",
        )
        return AWAITING_SYMBOL

    async def _receive_symbol(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        symbol = update.message.text.strip().upper()
        context.user_data["symbol"] = symbol

        keyboard = [
            [
                InlineKeyboardButton("📊 Technical", callback_data="technical"),
                InlineKeyboardButton("📋 Fundamental", callback_data="fundamental"),
            ],
            [
                InlineKeyboardButton("🏆 Piotroski F-Score", callback_data="piotroski"),
                InlineKeyboardButton("📈 CAN SLIM", callback_data="canslim"),
            ],
            [InlineKeyboardButton("📊📋 Both", callback_data="both")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"What analysis do you want for *{escape_md(symbol)}*?",
            reply_markup=reply_markup,
            parse_mode="MarkdownV2",
        )
        return AWAITING_ANALYSIS_TYPE

    async def _handle_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        choice = query.data
        symbol = context.user_data.get("symbol", "RELIANCE")

        await query.edit_message_text(
            f"Analyzing *{escape_md(symbol)}*\\.\\.\\. please wait ⏳",
            parse_mode="MarkdownV2",
        )

        try:
            messages = []
            if choice in ("technical", "both"):
                msg = _sections_to_telegram(
                    f"📊 Technical Analysis — {symbol}",
                    technical_analysis(symbol),
                )
                messages.append(msg)
            if choice in ("fundamental", "both"):
                msg = _sections_to_telegram(
                    f"📋 Fundamental Analysis — {symbol}",
                    fundamental_analysis(symbol),
                )
                messages.append(msg)
            if choice == "piotroski":
                msg = _sections_to_telegram(
                    f"🏆 Piotroski F-Score — {symbol}",
                    piotroski_fscore(symbol),
                )
                messages.append(msg)
            if choice == "canslim":
                msg = _sections_to_telegram(
                    f"📈 CAN SLIM Analysis — {symbol}",
                    canslim_analysis(symbol),
                )
                messages.append(msg)

            for msg in messages:
                for chunk in chunk_message(msg):
                    await query.message.reply_text(chunk, parse_mode="MarkdownV2")

        except ValueError as e:
            await query.message.reply_text(
                f"Error: {escape_md(str(e))}",
                parse_mode="MarkdownV2",
            )
        except Exception as e:
            logger.exception("Analysis failed for %s", symbol)
            await query.message.reply_text(
                f"Something went wrong: {escape_md(str(e))}",
                parse_mode="MarkdownV2",
            )

        await query.message.reply_text(
            "Send another stock symbol or /analyze to start again\\.",
            parse_mode="MarkdownV2",
        )
        return AWAITING_SYMBOL

    async def _cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Analysis cancelled. Use /analyze to start again.")
        return ConversationHandler.END

    def get_handlers(self) -> list:
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("analyze", self._start_analyze)],
            states={
                AWAITING_SYMBOL: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self._receive_symbol),
                ],
                AWAITING_ANALYSIS_TYPE: [
                    CallbackQueryHandler(self._handle_choice),
                ],
            },
            fallbacks=[CommandHandler("cancel", self._cancel)],
        )
        return [conv_handler]
