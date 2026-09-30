"""claude-voice command line: `hook` for Claude Code, the rest for you."""

from __future__ import annotations

import argparse
import json
import sys

from claude_voice import models, speaker
from claude_voice.hooks import Speak, StopSpeaking, action_for
from claude_voice.text import to_speech


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        return args.run(args)
    except speaker.ModelMissing as error:
        print(f"claude-voice: {error}", file=sys.stderr)
        return 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claude-voice", description=__doc__)
    commands = parser.add_subparsers(required=True, metavar="COMMAND")

    hook = commands.add_parser("hook", help="handle a Claude Code hook event read from stdin")
    hook.set_defaults(run=_hook)

    say = commands.add_parser("say", help="speak text given as arguments or on stdin")
    say.add_argument("text", nargs="*")
    say.add_argument("--lang", choices=speaker.VOICES, help="default: detected from the text")
    say.add_argument("--markdown", action="store_true", help="strip markdown before speaking")
    say.add_argument("--background", action="store_true", help="return at once, keep speaking")
    say.set_defaults(run=_say)

    stop = commands.add_parser("stop", help="stop speaking")
    stop.set_defaults(run=_stop)

    status = commands.add_parser("status", help="exit 0 while speaking, 1 otherwise")
    status.add_argument("-q", "--quiet", action="store_true")
    status.set_defaults(run=_status)

    setup = commands.add_parser("setup", help="download the voice model (about 350 MB)")
    setup.set_defaults(run=_setup)

    return parser


def _hook(_: argparse.Namespace) -> int:
    match action_for(json.load(sys.stdin)):
        case Speak(text):
            speaker.speak_in_background(text)
        case StopSpeaking():
            speaker.stop()
    return 0


def _say(args: argparse.Namespace) -> int:
    text = " ".join(args.text) if args.text else sys.stdin.read()
    if args.markdown:
        text = to_speech(text)
    if args.background:
        speaker.speak_in_background(text, args.lang)
    else:
        speaker.speak(text, args.lang)
    return 0


def _stop(_: argparse.Namespace) -> int:
    speaker.stop()
    return 0


def _setup(_: argparse.Namespace) -> int:
    models.download()
    return 0


def _status(args: argparse.Namespace) -> int:
    speaking = speaker.is_speaking()
    if not args.quiet:
        print("speaking" if speaking else "silent")
    return 0 if speaking else 1
