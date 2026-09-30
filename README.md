# claude-voice

Claude Code reads its answers out loud with a natural, local neural voice ([Kokoro](https://github.com/thewh1teagle/kokoro-onnx)).

- Reads the **whole final answer**, sentence by sentence. It skips code blocks, URLs, and markdown markup, and shortens file paths to file names.
- Says a short line when Claude **needs your permission or input**.
- **Stops talking** as soon as you send a new prompt, click 🔇 in the tmux status bar, or run `claude-voice stop`.
- English and French, detected from the text.
- Runs offline: your code and conversations never leave your machine.

## Requirements

- macOS or Linux, with Python 3.10 or later.
- Claude Code 2.1.285 or later. Older versions may not send the final answer to the `Stop` hook.
- [uv](https://docs.astral.sh/uv/) or [pipx](https://pipx.pypa.io/) to install the command, for example `brew install uv`.
- On Linux only, PortAudio: `sudo apt install libportaudio2`. On macOS it comes with the Python package.

## Install

Clone this repository, then run these commands from its folder:

```sh
uv tool install .    # or: pipx install .
claude-voice setup   # downloads the voice model, about 350 MB
claude-voice say "Hello, I can talk now."
```

If your shell cannot find `claude-voice`, run `uv tool update-shell` (or `pipx ensurepath`) and open a new terminal.

To update later, pull the repository and run `uv tool install --reinstall .` (or `pipx install --force .`).

## Connect it to Claude Code

Add the hooks to `~/.claude/settings.json`. If you already have hooks for these events, add the entries next to them:

```json
{
  "hooks": {
    "Stop": [{ "hooks": [{ "type": "command", "command": "claude-voice hook" }] }],
    "Notification": [{ "hooks": [{ "type": "command", "command": "claude-voice hook" }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": "claude-voice hook" }] }]
  }
}
```

The hook returns at once: the voice plays in a detached process.

## Stop button in tmux

Add to `~/.tmux.conf` (needs `set -g mouse on`):

```tmux
set -g status-interval 1
set -g status-right "#[range=user|claude-voice]#(claude-voice status -q && printf '🔇 stop voice ')#[norange] …your current status-right…"
bind-key -n MouseDown1Status if-shell -F '#{==:#{mouse_status_range},claude-voice}' 'run-shell -b "claude-voice stop"' 'select-window -t ='
bind-key v run-shell -b 'claude-voice stop'
```

If a theme builds your `status-right` over several lines, put the `#[range=…]…#[norange]` part at the start of the first one.

The button shows only while Claude speaks. `prefix + v` does the same from the keyboard: pick another key if `v` is already bound in your setup (`tmux list-keys -T prefix`).

## Configuration

| Variable             | Default    | Effect                                                                 |
| -------------------- | ---------- | ---------------------------------------------------------------------- |
| `CLAUDE_VOICE_EN`    | `af_heart` | English voice, e.g. `am_michael`, `bm_george` ([list][voices])         |
| `CLAUDE_VOICE_FR`    | `ff_siwis` | French voice                                                           |
| `CLAUDE_VOICE_SPEED` | `1.25`     | Speaking speed, `1.0` is normal                                        |
| `XDG_DATA_HOME`      | `~/.local/share` | The model goes in `$XDG_DATA_HOME/claude-voice`                  |

[voices]: https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md

Claude Code starts the hooks, so set these variables in the `env` section of `~/.claude/settings.json`:

```json
{
  "env": { "CLAUDE_VOICE_EN": "am_michael", "CLAUDE_VOICE_SPEED": "1.1" }
}
```

## Development

```sh
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest
```
