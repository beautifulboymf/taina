# 👵 taina

<p align="center">
  <img src="assets/grandma.png" alt="Cartoon grandma reading a paper" width="320" />
</p>

> **没读过书的奶奶，比博士更适合读论文——只要你装得像。**
>
> ***A grandma who never went to school reads papers better than any PhD — as long as you fake it well.***

[中文版 README](README.zh.md)

---

## What it is

A grandma-voice translation layer for hard text. Hand it a paper, a contract, a code snippet, or a hospital discharge summary; it produces a plain-language explanation built around three life metaphors, runs you through three to five questions one at a time, and closes with a warm "you're never too old to learn."

The grandson is fake. The grandma might be too. Only the papers are real.

---

## A prompt from 3 a.m.

Roughly what a fully-committed user looks like in the wild:

> The grandma is fake. The 80-year-old part is fake. Only the paper being incomprehensible is real.
>
> I'm a grad student. Third cup of coffee. My advisor wants me to walk her through this paper at 10 a.m. tomorrow. I'm on page 12, still don't get page 1.
>
> So I've decided to pretend to be my grandma.
>
> Does my grandma have any SCI publications? No. But she's still alive at 78. **That's the answer.**

---

## How it works

Five stages, in order:

1. **Fetch** — plain text, a local file, a URL, or an arxiv ID.
2. **Explanation** — one-line core, "what's new versus the old way", and at least three life metaphors drawn from the persona's domain library.
3. **Insider recap** — auto-enabled when the input contains formulas or code, skipped for legal and medical text. Includes a formula / symbol table, an annotated code snippet (where applicable), and a one-line tie-back to the metaphors used in stage 2.
4. **Quiz** — three to five questions delivered one at a time. A wrong answer triggers a three-step nudge: a fresh metaphor, then a reflective question, then the straight answer.
5. **Sign-off** — a warm, in-character closing.

The same workflow drives two voices:

- **Chinese** — 北京太奶 (Beijing great-grandma): the morning-stall vendor scanning a whole counter at once, alley gossip, the whole family kneading dough together.
- **English** — London Nan (working-class East End): Sunday roast, the postman's round, brewing one big pot of tea.

---

## Examples

| File | What it shows |
|------|---------------|
| [📄 examples/01-paper-attention.md](examples/01-paper-attention.md) | Transformer abstract — 北京太奶 voice, full insider recap with formula table |
| [📄 examples/01-paper-attention.en.md](examples/01-paper-attention.en.md) | Same paper, London Nan voice |
| [⚖️ examples/02-legal-contract.md](examples/02-legal-contract.md) | Force majeure clause — insider recap skipped (legal exemption path) |
| [💻 examples/03-code-reading.md](examples/03-code-reading.md) | PyTorch self-attention — insider recap with annotated code |

---

## Installation

The repository ships entry files for **Claude Code**, **Codex CLI**, **Cursor**, and **Gemini CLI**. The shared skill content lives under `taina-explainer/`.

### Claude Code

```bash
cp -r taina-explainer ~/.claude/skills/
mkdir -p ~/.claude/commands && cp commands/taina.md ~/.claude/commands/
# Then in Claude Code: /reload-plugins
```

### Codex CLI / Cursor

The repo's root `AGENTS.md` inlines the full skill (SKILL.md + both persona cards) and is loaded automatically by Codex CLI and Cursor.

Per-project install:

```bash
git clone https://github.com/beautifulboymf/taina.git
cd taina   # AGENTS.md is now in scope as project context
```

Global install (append the inlined skill to your global AGENTS.md):

```bash
git clone https://github.com/beautifulboymf/taina.git /tmp/taina
mkdir -p ~/.codex
cat /tmp/taina/AGENTS.md >> ~/.codex/AGENTS.md
```

> `AGENTS.md` is regenerated from `taina-explainer/{SKILL.md,persona-card.*.md}` by `scripts/build-agents.sh`. Edit the source files, then re-run the script — never edit `AGENTS.md` directly.

### Gemini CLI

```bash
gemini extensions install https://github.com/beautifulboymf/taina.git
```

Or clone manually into `~/.gemini/extensions/taina-explainer/`.

---

## Optional: hook-based mode persistence

Prose-only enforcement (the description and persona files) relies on the model honoring SKILL.md across turns. In long conversations or after context compaction the persona can drift. Registering `hooks/taina-mode-tracker.py` as a pre-prompt hook gives deterministic reinforcement: a flag file flips on when an activation phrase appears and flips off on an exit phrase, and while the flag is on the hook injects a one-line `TAINA MODE ACTIVE` reminder into every turn.

The script is a single zero-dependency Python file. Copy it somewhere stable, then register it per CLI:

**Claude Code** — add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "type": "command", "command": "python3 /absolute/path/to/taina-mode-tracker.py" }
    ]
  }
}
```

**Codex CLI** — add to `~/.codex/config.toml`:

```toml
[[hooks.UserPromptSubmit]]
command = ["python3", "/absolute/path/to/taina-mode-tracker.py"]
```

**Gemini CLI** — add to `~/.gemini/settings.json` (note the different hook event name):

```json
{
  "hooks": {
    "BeforeAgent": [
      {
        "command": ["python3", "/absolute/path/to/taina-mode-tracker.py"],
        "env": { "TAINA_HOOK_EVENT": "BeforeAgent" }
      }
    ]
  }
}
```

**Cursor** — not supported. Cursor 1.7's `beforeSubmitPrompt` hook is observe-only and ignores returned context, so reinforcement injection isn't possible today. Cursor users get prose-only enforcement.

The flag file defaults to `~/.taina-active`. Override with the `TAINA_FLAG` environment variable. Each CLI's exact hook schema may evolve — if registration fails, check that CLI's hook docs against the snippets above.

---

## Activation

The skill auto-activates when the user message contains any of the phrases below (alongside dense input). Voice routing follows the message language: Chinese phrases route to 北京太奶, English phrases route to London Nan.

| 北京太奶 (中文) | London Nan (English) |
|----------------|----------------------|
| 看不懂 | ELI5 |
| 白话讲讲 | explain like I'm 5 |
| 通俗讲 / 讲人话 | in plain English |
| 太奶讲讲 | speak to me like a granny |
| 啥意思 | no jargon / in simple terms |

Explicit invocation:

```
/taina <pasted text | file path | URL | arxiv ID>
```

Mid-conversation language switch:

```
用英文讲 / in English / 用中文 / in Chinese
```

### Exit

Drop the persona for the rest of the conversation; the AI replies in default style. Re-trigger anytime with the activation phrases above.

| 北京太奶 (中文) | London Nan (English) |
|----------------|----------------------|
| 退出太奶 | exit taina |
| 正常聊 / 正常说话 | back to normal |
| 不装了 | drop the granny |
| 回到正常 | normal mode |

Explicit:

```
/taina exit
```

---

## Customisation

The workflow logic lives in [`taina-explainer/SKILL.md`](taina-explainer/SKILL.md). The two voices live in [`taina-explainer/persona-card.zh.md`](taina-explainer/persona-card.zh.md) and [`taina-explainer/persona-card.en.md`](taina-explainer/persona-card.en.md). Persona files are pure content — metaphor libraries, praise templates, three-tier escalation lines — and contain no workflow logic. Swapping metaphors, tweaking praise lines, or forking a third dialect requires editing only the persona file.

---

## Verification

```bash
./scripts/lint-persona.sh all
```

Scans both persona templates for English acronyms, formulas, Greek letters, and inverted addressing (i.e. the AI accidentally calling the user "grandson" rather than the other way round).

---

## CLI support matrix

| CLI | Skill loading | Hook reinforcement |
|-----|---------------|--------------------|
| Claude Code | Skill directory at `~/.claude/skills/taina-explainer/`; slash command at `~/.claude/commands/taina.md` | `UserPromptSubmit` hook |
| Codex CLI | Root `AGENTS.md` (full skill inlined) is auto-loaded as project context | `UserPromptSubmit` hook |
| Gemini CLI | `gemini-extension.json` manifest + `GEMINI.md` import directives | `BeforeAgent` hook |
| Cursor | Root `AGENTS.md` is read natively as project context | Not supported (CLI's pre-prompt hook is observe-only) |

Coverage on each platform varies — please open an issue if you hit something that doesn't load.

---

## License

MIT — see [LICENSE](LICENSE).
