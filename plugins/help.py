from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from core.base_plugin import BasePlugin
from core.formatter import escape_md


class HelpPlugin(BasePlugin):
    """Lists all available plugins and commands."""

    def __init__(self, registry):
        self.registry = registry

    @property
    def name(self) -> str:
        return "Help"

    @property
    def description(self) -> str:
        return "Show available commands"

    async def _help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        lines = ["*Available Commands:*", ""]
        for plugin in self.registry.plugins:
            lines.append(f"• *{escape_md(plugin.name)}* — {escape_md(plugin.description)}")
        lines.append("")
        lines.append("Use /analyze to get started\\!")

        await update.message.reply_text("\n".join(lines), parse_mode="MarkdownV2")

    def get_handlers(self) -> list:
        return [CommandHandler("help", self._help)]
