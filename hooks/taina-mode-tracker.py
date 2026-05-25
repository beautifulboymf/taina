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

    TAINA_FLAG       path to flag file (default: <cwd>/.taina-active —
                     per-project scope, so taina mode in project A does not
                     leak into project B; override to ~/.taina-active for the
                     old global behaviour)
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

FLAG = (
    Path(os.path.expanduser(os.environ["TAINA_FLAG"]))
    if "TAINA_FLAG" in os.environ
    else Path.cwd() / ".taina-active"
)
HOOK_EVENT = os.environ.get("TAINA_HOOK_EVENT", "UserPromptSubmit")

# Activation triggers. Deliberately strict: ONLY explicit role-assignment
# phrases (user actively assigning the 太奶/granny/Nan role to themselves) or
# the `/taina <content>` slash command count as activation. Generic confusion
# phrases (啥意思 / 看不懂 / in simple terms / break it down / ELI5 …) are
# everyday language and would cause false positives — they are intentionally
# OUT. If the user is confused but doesn't want the granny persona, the host
# AI handles it normally. taina is opt-in by name.
ACTIVATE_RE = re.compile(
    # `/taina <content>` at the start of the prompt (excluding exit/stop forms)
    r"^/taina\s+(?!exit\b|stop\b)\S"
    # 中文 — 显式把"太奶"角色分配给自己（句子里必含"太奶"+受话人方向词）
    r"|给太奶讲|跟太奶讲|讲给太奶|说给太奶"
    r"|当我是太奶|当作太奶|当成太奶|把我当(?:作|成)?太奶"
    # English — explicit self-assignment as the granny / Nan listener
    # (covers "I'm", "Im", "I m", "I am" contractions)
    r"|pretend I(?:[' ]?m| am) a granny|treat me like a granny"
    r"|like I(?:[' ]?m| am) (?:a granny|your nan)",
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
    "Stay in taina persona voice per persona-card.zh.md / persona-card.en.md "
    "(plain language, life metaphors, Socratic Q&A; address user as 太奶/Nan; "
    "AI = explainer, never self-refer as 太奶/Nan). "
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
