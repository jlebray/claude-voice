"""Speak text with Kokoro, one voice at a time, stoppable from anywhere.

A pidfile records which process owns the speakers. Starting a new speech or
running `claude-voice stop` terminates that process.
"""

from __future__ import annotations

import os
import queue
import signal
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from claude_voice import models
from claude_voice.text import detect_language, split_sentences

PIDFILE = Path(tempfile.gettempdir()) / "claude-voice.pid"
SENTENCES_AHEAD = 3


@dataclass(frozen=True)
class Voice:
    name: str
    lang: str


VOICES = {
    "en": Voice(os.environ.get("CLAUDE_VOICE_EN", "af_heart"), "en-us"),
    "fr": Voice(os.environ.get("CLAUDE_VOICE_FR", "ff_siwis"), "fr-fr"),
}
SPEED = float(os.environ.get("CLAUDE_VOICE_SPEED", "1.25"))


class ModelMissing(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Kokoro model not found. Run `claude-voice setup` first.")


def speaking_pid() -> int | None:
    try:
        pid = int(PIDFILE.read_text())
        os.kill(pid, 0)
    except (OSError, ValueError):
        return None
    return pid


def is_speaking() -> bool:
    return speaking_pid() is not None


def stop() -> None:
    pid = speaking_pid()
    if pid is not None and pid != os.getpid():
        os.kill(pid, signal.SIGTERM)
    PIDFILE.unlink(missing_ok=True)


def speak(text: str, language: str | None = None, speed: float = SPEED) -> None:
    """Speak until done, or until another process calls `stop()`."""
    if not models.is_installed():
        raise ModelMissing
    voice = VOICES[language or detect_language(text)]
    with _own_speakers():
        _play(_synthesize(split_sentences(text), voice, speed))


def speak_in_background(text: str, language: str | None = None) -> None:
    """Return at once and keep speaking in a detached process.

    Claude Code waits for hooks to exit, and kills slow ones: reading a long
    answer must not hold the hook.
    """
    if not models.is_installed():
        raise ModelMissing
    if os.fork():
        return
    os.setsid()
    devnull = os.open(os.devnull, os.O_RDWR)
    for fd in (0, 1, 2):
        os.dup2(devnull, fd)
    try:
        speak(text, language)
    finally:
        os._exit(0)


@contextmanager
def _own_speakers() -> Iterator[None]:
    stop()
    PIDFILE.write_text(str(os.getpid()))
    signal.signal(signal.SIGTERM, _exit_quietly)
    try:
        yield
    finally:
        if speaking_pid() == os.getpid():
            PIDFILE.unlink(missing_ok=True)


def _exit_quietly(*_: object) -> None:
    raise SystemExit(0)


def _synthesize(sentences: list[str], voice: Voice, speed: float) -> Iterator[tuple]:
    """Yield audio sentence by sentence, preparing the next ones while the current one plays."""
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(str(models.model_path()), str(models.voices_path()))
    ready: queue.Queue = queue.Queue(maxsize=SENTENCES_AHEAD)

    def produce() -> None:
        for sentence in sentences:
            ready.put(kokoro.create(sentence, voice=voice.name, speed=speed, lang=voice.lang))
        ready.put(None)

    threading.Thread(target=produce, daemon=True).start()
    while (audio := ready.get()) is not None:
        yield audio


def _play(audio_chunks: Iterator[tuple]) -> None:
    import sounddevice

    for samples, sample_rate in audio_chunks:
        sounddevice.play(samples, sample_rate)
        sounddevice.wait()
