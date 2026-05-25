---
description: 用白话给太奶解释+苏格拉底式问答引导太奶理解难懂内容；`/taina exit` 退出
---

# /taina <内容或路径或URL | exit>

显式激活或退出 `taina-explainer` skill。

## 退出（`$ARGUMENTS` 为 `exit` 或 `stop`）

按 SKILL.md「如何退出」节执行：用当前 persona 的 §3.9 退出告别模板**只输出一句**，随后切回 AI 默认口吻，不做任何讲解 / 考核。

## 激活（其余参数）

把 `$ARGUMENTS` 喂给 skill，按"给没读过书的80岁太奶解释不好懂的内容"流程走。参数可以是：

- 直接粘贴的文本（abstract、合同条款、技术段落等）
- 本地文件路径（`.pdf` / `.md` / `.txt`）
- URL（`http(s)://...`）
- arxiv ID（如 `2401.12345`）

使用 `taina-explainer` skill 处理 `$ARGUMENTS`：

1. 阶段 0：识别输入类型，抓取内容（参考 SKILL.md 阶段 0 表格）
2. 阶段 1：为太奶讲解（一句话核心 + 通用逻辑 + ≥3 生活比喻 + 过渡到考核）
3. 阶段 2：苏格拉底式逐题考核（3-5 题，答错三连引导）
4. 阶段 3：收尾鼓励

全程严守 SKILL.md 验收清单与 `persona-card.*.md` 口吻规范。
