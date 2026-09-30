"""Short spoken lines for when Claude is waiting on you."""

from __future__ import annotations

import random

PERMISSION = (
    "I need your permission to continue.",
    "Can I get the go-ahead?",
    "Waiting on your approval.",
    "Mind granting permission?",
    "I need you to approve this.",
    "Permission needed to keep going.",
    "Give me the green light?",
    "I'm blocked until you approve.",
    "Awaiting your permission.",
    "Okay to proceed?",
    "Can you take a look and approve this?",
    "I need the green light before I continue.",
    "Could you confirm you're okay with this?",
    "Waiting for your sign-off.",
    "Let me know if I can go ahead.",
    "I'd like your approval before proceeding.",
    "Just need a yes from you.",
    "Can you unblock me on this one?",
    "Ready to continue as soon as you approve.",
    "Is it alright if I proceed?",
)

INPUT = (
    "I need your input.",
    "Your turn.",
    "What would you like next?",
    "Waiting on you.",
    "I need a hand here.",
    "Over to you.",
    "Ready when you are.",
    "Need some direction.",
    "What's the next step?",
    "I'm waiting for you.",
    "Could you tell me what to do next?",
    "I need a bit of guidance here.",
    "Let me know how you'd like to proceed.",
    "Waiting for your instructions.",
    "What should I focus on next?",
    "Could you point me in the right direction?",
    "I'm ready for your next request.",
    "Tell me what you'd like me to do.",
    "I could use your guidance.",
    "What's on your mind?",
)

PHRASES_BY_NOTIFICATION = {
    "permission_prompt": PERMISSION,
    "worker_permission_prompt": PERMISSION,
    "agent_needs_input": INPUT,
    "elicitation_dialog": INPUT,
    "elicitation_url_dialog": INPUT,
}


def for_notification(notification_type: str | None) -> str | None:
    """A random line for notifications worth saying out loud, None for the rest (idle, auth...)."""
    phrases = PHRASES_BY_NOTIFICATION.get(notification_type or "")
    return random.choice(phrases) if phrases else None
