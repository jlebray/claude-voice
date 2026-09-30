"""Turn Claude's markdown answers into text that sounds right when spoken."""

from __future__ import annotations

import re

FRENCH_ACCENTS = re.compile(r"[éèêëàâäùûüîïôöçœ]", re.IGNORECASE)
FRENCH_WORDS = frozenset(
    "le la les un une des du et est dans pour avec pas sur ce qui que je vous nous il elle "
    "mais ou donc ne plus fait fichier ligne erreur".split()
)
ENGLISH_WORDS = frozenset(
    "the a an and is are in for with not on this that which you we it but or so more done "
    "fixed check add remove file line error".split()
)

CODE_BLOCK = re.compile(r"```.*?(?:```|\Z)", re.DOTALL)
IMAGE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
URL = re.compile(r"https?://\S+")
FILE_PATH = re.compile(r"(?:~|\.{1,2})?/?(?:[\w.\-]+/){2,}([\w.\-]+)(?::\d+(?:-\d+)?)?")
LINE_NUMBER = re.compile(r"\b([\w\-]+\.\w+):\d+(?:-\d+)?\b")
TABLE_SEPARATOR = re.compile(r"[|:\-\s]+")
LINE_MARKER = re.compile(r"^(?:#+|>+|[-*+]|\d+[.)])\s+")
EMPHASIS = re.compile(r"\*\*|__|(?<!\w)[*_]|[*_](?!\w)")
TRAILING_PUNCTUATION = re.compile(r"[.!?:;,]$")
SENTENCE_BREAK = re.compile(r"(?<=[.!?;:])\s+|\n+")


def to_speech(markdown: str) -> str:
    """Drop what can't be spoken (code, URLs, table rulers) and keep the words.

    Every line ends with punctuation, so the voice pauses between list items.
    """
    text = CODE_BLOCK.sub("\n", markdown)
    text = IMAGE.sub("", text)
    text = LINK.sub(r"\1", text)
    text = URL.sub("", text)
    text = FILE_PATH.sub(r"\1", text)
    text = LINE_NUMBER.sub(r"\1", text)
    text = text.replace("`", "").replace("→", " to ")
    return "\n".join(filter(None, map(_speakable_line, text.splitlines())))


def _speakable_line(line: str) -> str:
    line = line.strip()
    if not line or TABLE_SEPARATOR.fullmatch(line):
        return ""
    if line.startswith("|"):
        line = ", ".join(cell.strip() for cell in line.strip("|").split("|") if cell.strip())
    line = EMPHASIS.sub("", LINE_MARKER.sub("", line)).strip()
    if line and not TRAILING_PUNCTUATION.search(line):
        line += "."
    return line


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_BREAK.split(text) if re.search(r"\w", part)]


def detect_language(text: str) -> str:
    """Return "fr" or "en". Accents settle it; otherwise the common words decide."""
    if FRENCH_ACCENTS.search(text):
        return "fr"
    words = re.findall(r"\w+", text.lower())
    french = sum(word in FRENCH_WORDS for word in words)
    english = sum(word in ENGLISH_WORDS for word in words)
    return "fr" if french > english else "en"
