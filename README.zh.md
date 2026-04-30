# 👵 taina

<p align="center">
  <img src="assets/grandma.png" alt="读论文的卡通奶奶" width="320" />
</p>

> **没读过书的奶奶，比博士更适合读论文——只要你装得像。**
>
> ***A grandma who never went to school reads papers better than any PhD — as long as you fake it well.***

[English README](README.md)

---

## 这是什么

一个把硬核文本翻成"奶奶口吻"的解说层。用户喂进去一篇论文、一段合同、一段代码或者一份诊断书，它会输出一段大白话讲解，串上三个生活比喻，再一题一题考你三到五道题，最后用"活到老学到老"这种暖色调收尾。

孙辈是装的。奶奶可能也是装的。只有论文是真的。

---

## 凌晨三点的一份 prompt

一个"完全入戏"的用户大概长这样：

> 太奶是假的，80 岁是假的。只有论文看不懂是真的。
>
> 我是个研究生，第三杯咖啡下肚，导师明天十点要听我讲这篇 paper——看到第 12 页，还没懂第 1 页。
>
> 所以我决定装成我奶奶。
>
> 我奶奶有 SCI 论文吗？没有。但她活下来了。**这就是答案**。

---

## 工作流

五个阶段，按顺序走：

1. **抓内容** —— 文本、本地文件、URL，或者一个 arxiv ID。
2. **奶奶讲一遍** —— 一句话核心 + "比以前的法子新在哪儿" + 至少三个生活比喻（取自当前 persona 的比喻库）。
3. **内行复盘** —— 输入含公式或代码时自动启用，法律 / 医学文本则跳过。包含公式 / 符号小表、关键代码加注，以及一句话把比喻和公式 / 代码串回去。
4. **考你** —— 出 3 到 5 道题，一题一题问。答得不到位时，孙辈用三步把你引回来：换个比喻 → 反问引导 → 直接给答案。
5. **收尾** —— 真心夸一句，"活到老学到老" 的味道。

同一套工作流支持两种人格：

- **中文** —— **北京太奶**：早点摊大爷扫一圈整桌、胡同口街坊唠嗑、全家围在一起揉面。
- **English** —— **London Nan**（伦敦工人阶级 East End）：Sunday roast、the postman's round、brewing one big pot of tea。

---

## 示例

| 文件 | 演示什么 |
|------|---------|
| [📄 examples/01-paper-attention.md](examples/01-paper-attention.md) | Transformer abstract —— 北京太奶口吻，含完整内行复盘（带公式表） |
| [📄 examples/01-paper-attention.en.md](examples/01-paper-attention.en.md) | 同一篇论文，London Nan 口吻 |
| [⚖️ examples/02-legal-contract.md](examples/02-legal-contract.md) | 不可抗力条款 —— 内行复盘整段跳过（法律豁免路径） |
| [💻 examples/03-code-reading.md](examples/03-code-reading.md) | PyTorch self-attention —— 内行复盘含行级代码注释 |

---

## 安装

仓库根目录提供 **Claude Code**、**Codex CLI**、**Cursor**、**Gemini CLI** 各自的入口文件，skill 内容统一放在 `taina-explainer/` 下。

### Claude Code

```bash
cp -r taina-explainer ~/.claude/skills/
mkdir -p ~/.claude/commands && cp commands/taina.md ~/.claude/commands/
# 然后在 Claude Code 里跑 /reload-plugins
```

### Codex CLI / Cursor

仓库根目录的 `AGENTS.md` 已经把整套 skill（SKILL.md + 两份 persona card）inline 进去，Codex CLI 和 Cursor 打开仓库时会自动加载。

项目级安装：

```bash
git clone https://github.com/beautifulboymf/taina.git
cd taina   # AGENTS.md 自动作为上下文加载
```

全局安装（把 inlined 后的 skill 追加到全局 AGENTS.md）：

```bash
git clone https://github.com/beautifulboymf/taina.git /tmp/taina
mkdir -p ~/.codex
cat /tmp/taina/AGENTS.md >> ~/.codex/AGENTS.md
```

> `AGENTS.md` 由 `scripts/build-agents.sh` 从 `taina-explainer/{SKILL.md,persona-card.*.md}` 生成。改 skill 内容请改源文件，然后重跑脚本——**别**直接编辑 `AGENTS.md`。

### Gemini CLI

```bash
gemini extensions install https://github.com/beautifulboymf/taina.git
```

或者手动 clone 到 `~/.gemini/extensions/taina-explainer/`。

---

## 可选：基于 hook 的状态保持

只靠 SKILL.md 散文约束模型，长对话里口吻可能飘。把 `hooks/taina-mode-tracker.py` 注册成 pre-prompt hook 就能拿到确定性强化：检测到激活短语时建一个 flag 文件，检测到退出短语时删掉；flag 在的时候每回合往上下文里塞一句 `TAINA MODE ACTIVE` 提醒。

脚本是单文件、零依赖、纯 Python。把它放到一个稳定路径，然后按 CLI 注册：

**Claude Code** — 加到 `~/.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "type": "command", "command": "python3 /absolute/path/to/taina-mode-tracker.py" }
    ]
  }
}
```

**Codex CLI** — 加到 `~/.codex/config.toml`：

```toml
[[hooks.UserPromptSubmit]]
command = ["python3", "/absolute/path/to/taina-mode-tracker.py"]
```

**Gemini CLI** — 加到 `~/.gemini/settings.json`（注意 hook 事件名不一样）：

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

**Cursor** — 暂不支持。Cursor 1.7 的 `beforeSubmitPrompt` hook 是 observe-only，返回的 context 会被忽略，没法做强化注入。Cursor 用户只能走 prose-only 路径。

flag 文件默认是 `~/.taina-active`，可以用 `TAINA_FLAG` 环境变量改路径。各 CLI 的 hook schema 可能随版本调整——注册失败时拿对应 CLI 官方 hook 文档跟上面的片段对一下。

---

## 触发方式

skill 在用户消息里出现以下任一短语、且伴有难懂内容时自动激活。语言路由跟着用户消息走：含汉字进 北京太奶；纯英文进 London Nan。

| 北京太奶 (中文) | London Nan (English) |
|----------------|----------------------|
| 看不懂 | ELI5 |
| 白话讲讲 | explain like I'm 5 |
| 通俗讲 / 讲人话 | in plain English |
| 太奶讲讲 | speak to me like a granny |
| 啥意思 | no jargon / in simple terms |

显式调用：

```
/taina <粘贴文本 | 文件路径 | URL | arxiv ID>
```

会话中途切换语言：

```
用英文讲 / in English / 用中文 / in Chinese
```

### 退出

退出后当前会话余下回合 AI 用默认口吻回应；想重新进入再用上面的入口短语即可。

| 北京太奶 (中文) | London Nan (English) |
|----------------|----------------------|
| 退出太奶 | exit taina |
| 正常聊 / 正常说话 | back to normal |
| 不装了 | drop the granny |
| 回到正常 | normal mode |

显式：

```
/taina exit
```

---

## 自定义口吻

工作流逻辑在 [`taina-explainer/SKILL.md`](taina-explainer/SKILL.md)。两套人格分别放在 [`taina-explainer/persona-card.zh.md`](taina-explainer/persona-card.zh.md) 和 [`taina-explainer/persona-card.en.md`](taina-explainer/persona-card.en.md)。persona 文件只放比喻库、夸赞模板、三连话术这类纯内容，不掺工作流逻辑。换比喻、调夸赞口吻、或者 fork 出第三种方言版本，都只需要改 persona 文件。

---

## 验证

```bash
./scripts/lint-persona.sh all
```

这个脚本扫两份 persona 卡片的模板段，确认里面没有英文缩写、公式、希腊字母，也没有"AI 反过来叫用户孙儿"这类称呼方向反了的错。

---

## CLI 支持矩阵

| CLI | 加载 skill | Hook 强化 |
|-----|-----------|-----------|
| Claude Code | skill 目录放在 `~/.claude/skills/taina-explainer/`；斜杠命令放在 `~/.claude/commands/taina.md` | `UserPromptSubmit` hook |
| Codex CLI | 根目录 `AGENTS.md`（已完整 inline skill）会被自动作为项目上下文加载 | `UserPromptSubmit` hook |
| Gemini CLI | `gemini-extension.json` manifest + `GEMINI.md` 的 import 指令 | `BeforeAgent` hook |
| Cursor | 根目录 `AGENTS.md` 会被原生读取为项目上下文 | 不支持（pre-prompt hook 是 observe-only） |

各平台覆盖度可能有差异——遇到加载不上的情况请提 issue。

---

## License

MIT，详见 [LICENSE](LICENSE)。
