"""BBCode-style markup stripping shared by state rendering and codex lookups."""
import re

BBCODE_RE = re.compile(r"\[/?[^\]]+\]")


def strip_bbcode(text):
    """Remove BBCode-style markup tags from a string.

    Args:
        text: Raw label text that may contain [tag] markup.

    Returns:
        The text with markup tags removed; non-strings pass through unchanged.
    """
    return BBCODE_RE.sub("", text) if isinstance(text, str) else text


def strip_codex_markup(text):
    """Remove codex inline markup like [green]6[/green] or [sine]...[/sine].

    Args:
        text: Codex description string that may carry inline markup.

    Returns:
        Plain stripped text; empty string for non-strings.
    """
    if not isinstance(text, str):
        return ""
    return BBCODE_RE.sub("", text).strip()
