"""Pure text helpers for the Code Reviewer output.

Kept free of Streamlit imports so they can be unit-tested directly.
"""

import html
import re

# Matches a section header, tolerating markdown decoration (##, **, -, >) and
# an optional colon, whether the header stands on its own line or is inline.
_HEADER_RE = re.compile(
    r"(?im)^[^\S\n]*(?:[#>*\-\u2022]+\s*)*\**\s*"
    r"(BUGS|OPTIMIZATIONS|BEST PRACTICES|CORRECTED CODE)"
    r"[ \t*:#>]*"
)
_INLINE_HEADER_RE = re.compile(
    r"(BUGS|OPTIMIZATIONS|BEST PRACTICES|CORRECTED CODE)[ \t]*:?[ \t]*",
    re.IGNORECASE,
)


def safe_block(text):
    """Escape text for safe HTML embedding, preserving line breaks."""
    if not text:
        return ""
    return html.escape(str(text)).replace("\n", "<br>")


def parse_review(text):
    """Split a reviewer response into its four sections."""
    if not text:
        return {}

    matches = list(_HEADER_RE.finditer(text))
    if not matches:
        matches = list(_INLINE_HEADER_RE.finditer(text))

    sections = {}
    for i, match in enumerate(matches):
        name = match.group(1).upper()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()
    return sections


def extract_code(section):
    """Return (language, code) from a corrected-code section."""
    if not section:
        return "text", ""

    fence = re.search(r"```([a-zA-Z0-9_+-]*)[ \t]*\r?\n(.*?)```", section, re.DOTALL)
    if fence:
        language = (fence.group(1) or "text").lower()
        return language, fence.group(2).strip()

    cleaned = section.replace("```", "").strip()
    return "text", cleaned
