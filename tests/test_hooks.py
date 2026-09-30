from claude_voice import phrases
from claude_voice.hooks import Speak, StopSpeaking, action_for


def test_reads_the_final_answer_when_claude_stops():
    event = {"hook_event_name": "Stop", "last_assistant_message": "**All green**"}

    assert action_for(event) == Speak("All green.")


def test_stays_silent_when_the_final_answer_is_empty():
    assert action_for({"hook_event_name": "Stop", "last_assistant_message": "```\ncode\n```"}) is None
    assert action_for({"hook_event_name": "Stop"}) is None


def test_asks_for_permission():
    action = action_for({"hook_event_name": "Notification", "notification_type": "permission_prompt"})

    assert isinstance(action, Speak)
    assert action.text in phrases.PERMISSION


def test_asks_for_input():
    action = action_for({"hook_event_name": "Notification", "notification_type": "elicitation_dialog"})

    assert isinstance(action, Speak)
    assert action.text in phrases.INPUT


def test_ignores_idle_notifications():
    assert action_for({"hook_event_name": "Notification", "notification_type": "idle_prompt"}) is None


def test_stops_speaking_when_you_send_a_prompt():
    assert action_for({"hook_event_name": "UserPromptSubmit", "prompt": "next"}) == StopSpeaking()
    assert action_for({"hook_event_name": "UserPromptSubmit", "source": "user"}) == StopSpeaking()


def test_keeps_speaking_on_automated_prompts():
    assert action_for({"hook_event_name": "UserPromptSubmit", "source": "loop_wakeup"}) is None


def test_ignores_other_events():
    assert action_for({"hook_event_name": "PreToolUse"}) is None
