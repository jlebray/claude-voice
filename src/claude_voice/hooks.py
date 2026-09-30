"""Decide what to do for each Claude Code hook event.

One entry point serves every hook, so the settings stay the same for all of them:

    Stop              -> read the final answer out loud
    Notification      -> say a short line when Claude waits on you
    UserPromptSubmit  -> stop talking, you have moved on
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from claude_voice import phrases
from claude_voice.text import to_speech


@dataclass(frozen=True)
class Speak:
    text: str


@dataclass(frozen=True)
class StopSpeaking:
    pass


Action = Speak | StopSpeaking | None


def action_for(event: Mapping[str, Any]) -> Action:
    match event.get("hook_event_name"):
        case "Stop":
            return _speak(to_speech(event.get("last_assistant_message") or ""))
        case "Notification":
            return _speak(phrases.for_notification(event.get("notification_type")))
        case "UserPromptSubmit" if event.get("source", "user") == "user":
            return StopSpeaking()
    return None


def _speak(text: str | None) -> Speak | None:
    return Speak(text) if text and text.strip() else None
