# claude-context-statusline

A zero-dependency status line for [Claude Code](https://claude.com/claude-code) that shows **live context window usage** — so you always know how full your session is before it compacts.

```
Fable 5 | my-project | ctx 261k/500k [=====-----] 52% | $1.23
```

- Live context usage after every turn, read from the real session transcript
- Progress bar with warnings at 75% (`! consider /compact`) and 90% (`!! compact imminent`)
- Auto-detects standard (200k) and extended (500k / 1M) context windows — no configuration
- Shows model, project directory, and session cost
- Pure Python 3 standard library, single file, no dependencies
- Degrades gracefully (`ctx n/a`) instead of breaking your prompt

## Why

Claude Code sessions don't warn you as context fills up. When the window is full the conversation gets compacted (summarized), and if you're not paying attention you can lose the thread of long work. This puts the number in front of you on every turn, so `/compact` and `/clear` become deliberate decisions instead of surprises.

## Install as a plugin (recommended)

Inside any Claude Code session:

```
/plugin marketplace add slimt623/claude-context-statusline
/plugin install claude-context-statusline@claude-context-statusline
```

Then ask Claude to run the installer:

```
/claude-context-statusline:install
```

The install skill copies the script to `~/.claude/statusline.py` and wires it into your `settings.json` (plugins cannot register the main status line directly, so this one-time step is required — the skill does it for you and verifies the result).

## Install manually

```bash
mkdir -p ~/.claude
curl -o ~/.claude/statusline.py https://raw.githubusercontent.com/slimt623/claude-context-statusline/main/statusline.py
chmod +x ~/.claude/statusline.py
```

Then add to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.py",
    "padding": 0
  }
}
```

Open a new Claude Code session and the bar appears under the prompt.

## How it works

Claude Code pipes a JSON payload to the status line command on every update. The payload includes `transcript_path` — the session's JSONL transcript. The script reads the last main-thread assistant message and sums its `usage` block:

```
context = input_tokens + cache_read_input_tokens + cache_creation_input_tokens
```

That sum is the actual size of the conversation as sent to the model — the same number that drives auto-compaction. Sidechain (subagent) messages are excluded so subagent activity doesn't distort the reading.

## Test it manually

```bash
echo '{"model":{"display_name":"Test"},"workspace":{"current_dir":"/tmp/demo"},"transcript_path":"'"$(ls -t ~/.claude/projects/*/*.jsonl | head -1)"'"}' | ~/.claude/statusline.py
```

## Customize

Everything is in one small file — edit freely:

- Warning thresholds: the `>= 90` / `>= 75` checks
- Bar width: the `10` in the `filled` calculation
- Window sizes: the `(200_000, 500_000, 1_000_000)` tuple
- Drop the cost segment by deleting the final `if` block

## License

MIT
