---
name: install
description: Use when the user asks to install, set up, enable, or activate the context status line from this plugin. Copies the statusline script into ~/.claude and wires it into settings.json.
---

# Install the context status line

Claude Code plugins cannot register the main status line directly, so this skill performs a one-time install into the user's own configuration.

## Steps

1. Copy the script to a stable path (the plugin cache path changes on every update, so never point settings at `${CLAUDE_PLUGIN_ROOT}` directly):

```bash
cp "${CLAUDE_PLUGIN_ROOT}/statusline.py" ~/.claude/statusline.py
chmod +x ~/.claude/statusline.py
```

2. Read `~/.claude/settings.json` first. Merge the following key into the existing JSON — preserve every existing key, never overwrite the whole file. If the file does not exist, create it with only this object:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.py",
    "padding": 0
  }
}
```

If a `statusLine` key already exists, show the user the current value and ask before replacing it.

3. Verify by piping a synthesized payload with a real transcript:

```bash
echo '{"model":{"display_name":"Test"},"workspace":{"current_dir":"/tmp/demo"},"transcript_path":"'"$(ls -t ~/.claude/projects/*/*.jsonl 2>/dev/null | head -1)"'"}' | ~/.claude/statusline.py
```

Expected output shape: `Test | demo | ctx 42k/200k [==--------] 21%`. If no transcripts exist yet, `Test | demo | ctx n/a` is also a pass.

4. Validate that `~/.claude/settings.json` is still parseable JSON (a malformed file silently disables all settings):

```bash
python3 -c "import json; json.load(open('$HOME/.claude/settings.json'))" && echo OK
```

5. Tell the user: the status line appears at the bottom of the next new session. Warnings appear at 75% (`! consider /compact`) and 90% (`!! compact imminent`) of the context window.
