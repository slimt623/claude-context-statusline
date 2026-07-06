#!/usr/bin/env python3
# Claude Code status line: live context usage, project, model, and session cost.
# Reads the status line JSON from stdin, computes current context size from the
# session transcript (last main-thread assistant message's usage block), and
# prints one line. Degrades to "ctx n/a" if anything is missing.
import json, sys, os

try:
    data = json.load(sys.stdin)
except Exception:
    print("ctx: n/a")
    sys.exit(0)

model = (data.get("model") or {}).get("display_name") or "?"
cwd = os.path.basename((data.get("workspace") or {}).get("current_dir") or "")
cost = (data.get("cost") or {}).get("total_cost_usd")
transcript = data.get("transcript_path") or ""

ctx = None
try:
    with open(transcript) as f:
        for line in f:
            try:
                j = json.loads(line)
            except Exception:
                continue
            if j.get("type") != "assistant" or j.get("isSidechain"):
                continue
            u = (j.get("message") or {}).get("usage")
            if u:
                ctx = (
                    (u.get("input_tokens") or 0)
                    + (u.get("cache_read_input_tokens") or 0)
                    + (u.get("cache_creation_input_tokens") or 0)
                )
except Exception:
    pass

parts = [model]
if cwd:
    parts.append(cwd)

if ctx is not None:
    # Pick the smallest plausible window that fits — adapts to standard (200k)
    # and extended (500k / 1M) context models without configuration.
    limit = next((l for l in (200_000, 500_000, 1_000_000) if ctx <= l), 1_000_000)
    pct = min(100, round(ctx * 100 / limit))
    filled = pct // 10
    bar = "=" * filled + "-" * (10 - filled)
    seg = f"ctx {ctx//1000}k/{limit//1000}k [{bar}] {pct}%"
    if pct >= 90:
        seg += " !! compact imminent"
    elif pct >= 75:
        seg += " ! consider /compact"
    parts.append(seg)
else:
    parts.append("ctx n/a")

if isinstance(cost, (int, float)) and cost > 0:
    parts.append(f"${cost:.2f}")

print(" | ".join(parts))
