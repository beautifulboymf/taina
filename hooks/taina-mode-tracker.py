#!/usr/bin/env python3
"""taina-mode-tracker — pre-prompt hook for Claude Code / Codex CLI / Gemini CLI.

Reads the per-turn JSON payload on stdin, detects taina activation and exit
triggers in the user's prompt, maintains a flag file representing mode state,
and emits hookSpecificOutput.additionalContext as reinforcement on every turn
while taina mode is active.

Output shape (compatible with Claude Code UserPromptSubmit, Codex CLI
UserPromptSubmit, and Gemini CLI BeforeAgent):

    {"hookSpecificOutput": {"hookEventName": "...", "additionalContext": "..."}}

Configuration (env vars):

    TAINA_FLAG       path to flag file (default: ~/.taina-active)
    TAINA_HOOK_EVENT name reported in hookEventName (default: UserPromptSubmit;
                     set to "BeforeAgent" when registering with Gemini CLI)

Behaviour:

  - exit trigger in prompt → delete flag, emit no context (model emits the
    §3.9 sign-off line from SKILL.md/persona card on its own)
  - activation trigger in prompt → create flag, emit reinforcement
  - flag exists, neither trigger → emit reinforcement
  - no flag, no trigger → emit empty object (no-op)

The reinforcement is intentionally short — full workflow rules live in
SKILL.md / persona-card.*.md, which the host CLI already loads into context.
This hook only keeps the model anchored across long conversations and
across context compaction.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

FLAG = Path(os.path.expanduser(os.environ.get("TAINA_FLAG", "~/.taina-active")))
HOOK_EVENT = os.environ.get("TAINA_HOOK_EVENT", "UserPromptSubmit")

ACTIVATE_RE = re.compile(
    r"看不懂|啥意思|白话讲讲|通俗讲|大白话|讲人话|零基础讲|太奶|像跟老人解释"
    r"|\bELI5\b"
    r"|explain like I[' ]?m (?:5|a kid)"
    r"|in plain English|no jargon|in simple terms|make it simple|break it down"
    r"|speak to me like a granny|like I[' ]?m 80",
    re.IGNORECASE,
)

EXIT_RE = re.compile(
    r"退出太奶|结束太奶|别装太奶了|不装了|正常说话|正常聊|正常模式|回到正常|停下太奶"
    r"|/taina\s+(?:exit|stop)\b"
    r"|exit taina|stop the granny|drop the granny|drop the act"
    r"|back to normal|normal mode|end taina",
    re.IGNORECASE,
)

REINFORCEMENT = (
    "TAINA MODE ACTIVE — the user is currently inside the taina-explainer skill. "
    "Stay in grandson voice (plain language, life metaphors, Socratic Q&A; "
    "address user as 太奶/Nan; never self-refer as the grandma). "
    "Stage 1.5 may use jargon; stages 0/1/2/3 must not. "
    "Exit triggers (any flips this off): 退出太奶 / 不装了 / 正常聊 / "
    "exit taina / drop the granny / back to normal / `/taina exit`."
)


def get_prompt(payload: object) -> str:
    """Extract the user's prompt text from any of the known payload shapes."""
    if not isinstance(payload, dict):
        return ""
    for key in ("prompt", "user_prompt", "userMessage", "message", "input", "text"):
        v = payload.get(key)
        if isinstance(v, str):
            return v
    for key in ("user", "request", "data"):
        v = payload.get(key)
        if isinstance(v, dict):
            for k2 in ("content", "text", "prompt", "message"):
                v2 = v.get(k2)
                if isinstance(v2, str):
                    return v2
    return ""


def emit(text: str | None) -> None:
    if text:
        out = {
            "hookSpecificOutput": {
                "hookEventName": HOOK_EVENT,
                "additionalContext": text,
            }
        }
    else:
        out = {}
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")


def write_flag() -> None:
    FLAG.parent.mkdir(parents=True, exist_ok=True)
    FLAG.touch(exist_ok=True)


def clear_flag() -> None:
    try:
        FLAG.unlink()
    except FileNotFoundError:
        pass


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        emit(None)
        return 0

    prompt = get_prompt(payload)

    if EXIT_RE.search(prompt):
        clear_flag()
        emit(None)
        return 0

    if ACTIVATE_RE.search(prompt):
        write_flag()
        emit(REINFORCEMENT)
        return 0

    if FLAG.exists():
        emit(REINFORCEMENT)
        return 0

    emit(None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
