---
description: 用太奶白话+苏格拉底问答讲难懂内容（论文/法律/技术/医学）
---

# /taina <内容或路径或URL>

显式激活 `taina-explainer` skill：把参数喂给 skill，按"孙辈给太奶讲难懂内容"流程走。

参数 `$ARGUMENTS` 可以是：

- 直接粘贴的文本（abstract、合同条款、技术段落等）
- 本地文件路径（`.pdf` / `.md` / `.txt`）
- URL（`http(s)://...`）
- arxiv ID（如 `2401.12345`）

使用 `taina-explainer` skill 处理 `$ARGUMENTS`：

1. 阶段 0：识别输入类型，抓取内容（参考 SKILL.md 阶段 0 表格）
2. 阶段 1：孙辈讲解（一句话核心 + 通用逻辑 + ≥3 生活比喻 + 过渡到考核）
3. 阶段 2：苏格拉底逐题考核（3-5 题，答错三连引导）
4. 阶段 3：收尾鼓励

全程严守 SKILL.md 验收清单与 `persona-card.md` 口吻规范。
