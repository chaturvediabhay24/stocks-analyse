import re


def escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(special_chars)}])", r"\\\1", str(text))


def fmt_number(value, prefix: str = "", suffix: str = "", decimals: int = 2) -> str:
    """Format a number for display. Returns 'N/A' if value is None."""
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        if abs(value) >= 1e7:  # 1 crore+
            cr = value / 1e7
            return f"{prefix}{cr:,.{decimals}f} Cr{suffix}"
        return f"{prefix}{value:,.{decimals}f}{suffix}"
    return str(value)


def fmt_percent(value) -> str:
    """Format a decimal as percentage. Returns 'N/A' if None."""
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def build_message(title: str, sections: list[tuple[str, str]]) -> str:
    """Build a Telegram MarkdownV2 message from title and key-value sections.

    Args:
        title: Bold header text.
        sections: List of (label, value) tuples.

    Returns:
        MarkdownV2-formatted string.
    """
    lines = [f"*{escape_md(title)}*", ""]
    for label, value in sections:
        if not label and not value:
            lines.append("")
        elif not value:
            # Section header
            lines.append(f"*{escape_md(label)}*")
        else:
            lines.append(f"*{escape_md(label)}:* {escape_md(str(value))}")
    return "\n".join(lines)


def chunk_message(text: str, max_len: int = 4096) -> list[str]:
    """Split a message into chunks that fit Telegram's message size limit."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break
        # Try to split at a newline
        split_at = text.rfind("\n", 0, max_len)
        if split_at == -1:
            split_at = max_len
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks
