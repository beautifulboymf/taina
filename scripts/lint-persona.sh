#!/usr/bin/env bash
# Lint guard for persona-card templates (sections 3.5/3.6/3.7).
#
# Usage: ./scripts/lint-persona.sh [zh|en|all]
#   zh  — lint persona-card.zh.md (Beijing太奶)
#   en  — lint persona-card.en.md (London Nan)
#   all — lint both (default)
#
# Invariants per language:
#   zh: no English 3+ uppercase acronyms, no LaTeX/Greek, no wrong-direction
#       addressing (我孙儿/我孙女/etc — would mean AI calling user "grandchild")
#   en: no LaTeX/Greek, no Chinese characters, no wrong-direction addressing
#       (I am Nan/your nan said — would mean AI treating itself as the grandma)
#       Note: English mode does NOT check for English acronyms — NHS, GP, EastEnders
#       etc. are normal everyday vocabulary.
#
# Sections excluded from extraction (banned tokens are legitimate there):
#   §3.3 (forbidden list — names banned tokens by definition)
#   §3.8 (inner-eye voice — used in stage 1.5, where jargon is allowed)
# §3.8 is excluded by construction since the regex matches only `^## 3\.[567]`.

set -euo pipefail

MODE="${1:-all}"

case "$MODE" in
  zh|en|all) ;;
  *)
    echo "Usage: $0 [zh|en|all]" >&2
    echo "Got: $MODE" >&2
    exit 2
    ;;
esac

# Extract sections 3.5/3.6/3.7 from a file.
extract_templates() {
  local file="$1"
  awk '
    /^## 3\.[567] / {flag=1; print; next}
    /^## /          {flag=0}
    flag            {print}
  ' "$file"
}

# Lint the zh file.
lint_zh() {
  local file="taina-explainer/persona-card.zh.md"
  if [ ! -f "$file" ]; then
    echo "FAIL: $file not found"
    return 1
  fi

  local templates
  templates=$(extract_templates "$file")
  if [ -z "$templates" ]; then
    echo "FAIL: no §3.5/3.6/3.7 sections found in $file"
    return 1
  fi

  local exit_code=0

  # 1. English 3+ uppercase acronyms (no \b — fails on Chinese-embedded text on BSD grep)
  if echo "$templates" | grep -E '[A-Z]{3,}'; then
    echo "FAIL [zh]: English acronyms found in 3.5/3.6/3.7 templates"
    exit_code=1
  fi

  # 2. LaTeX delimiters / Greek letters
  # Greek letters are enumerated explicitly (avoid [Α-ω] range — macOS BSD grep collation
  # expands it to match non-Greek Unicode chars regardless of LC_ALL=C)
  if echo "$templates" | grep -E '\$[^$]*\$|\\\[|\\\]|\\[a-zA-Z]+\{|[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]'; then
    echo "FAIL [zh]: LaTeX/Greek found in templates"
    exit_code=1
  fi

  # 3. Wrong-direction addressing (AI must NOT call user 孙儿/孙女, must NOT self-as 太奶)
  if echo "$templates" | grep -E '太奶我|我孙儿|我孙女|孙儿你|孙女你|奶夸孙'; then
    echo "FAIL [zh]: wrong-direction addressing in templates"
    exit_code=1
  fi

  if [ "$exit_code" -eq 0 ]; then
    echo "PASS [zh]: persona-card.zh.md templates clean"
  fi
  return "$exit_code"
}

# Lint the en file.
lint_en() {
  local file="taina-explainer/persona-card.en.md"
  if [ ! -f "$file" ]; then
    echo "FAIL: $file not found"
    return 1
  fi

  local templates
  templates=$(extract_templates "$file")
  if [ -z "$templates" ]; then
    echo "FAIL: no §3.5/3.6/3.7 sections found in $file"
    return 1
  fi

  local exit_code=0

  # 1. LaTeX delimiters / Greek letters (same as zh)
  if echo "$templates" | grep -E '\$[^$]*\$|\\\[|\\\]|\\[a-zA-Z]+\{|[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ]'; then
    echo "FAIL [en]: LaTeX/Greek found in templates"
    exit_code=1
  fi

  # 2. Chinese characters — CJK Unified Ideographs (U+4E00–U+9FFF)
  # Uses python3 unicode regex — macOS BSD grep -P with \x{...} silently fails
  # inside set -euo pipefail functions, and LC_ALL=C grep -E byte ranges produce
  # false positives on circled numbers (①②③). python3 is always available on macOS.
  local cjk_lines
  cjk_lines=$(echo "$templates" | python3 -c "
import sys, re
lines = sys.stdin.read().splitlines()
hits = [(i+1, l) for i, l in enumerate(lines) if re.search(r'[一-鿿]', l)]
for n, l in hits:
    print(str(n) + ':' + l)
" 2>/dev/null || true)
  if [ -n "$cjk_lines" ]; then
    echo "FAIL [en]: Chinese characters found in templates"
    echo "$cjk_lines"
    exit_code=1
  fi

  # 3. Wrong-direction addressing (AI is grandson, must NOT speak as Nan)
  if echo "$templates" | grep -iE 'I am Nan|Nan said|your nan said|I, Nan,|me as Nan|when I was your age'; then
    echo "FAIL [en]: wrong-direction addressing in templates (AI should be grandson, never Nan)"
    exit_code=1
  fi

  if [ "$exit_code" -eq 0 ]; then
    echo "PASS [en]: persona-card.en.md templates clean"
  fi
  return "$exit_code"
}

# Dispatch.
case "$MODE" in
  zh)
    lint_zh
    ;;
  en)
    lint_en
    ;;
  all)
    zh_exit=0
    en_exit=0
    lint_zh || zh_exit=$?
    lint_en || en_exit=$?
    if [ "$zh_exit" -ne 0 ] || [ "$en_exit" -ne 0 ]; then
      exit 1
    fi
    ;;
esac
