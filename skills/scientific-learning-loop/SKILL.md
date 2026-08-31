---
name: scientific-learning-loop
description: >
  Run a science-based, 10-step closed-loop learning method to deeply master any
  new topic with an AI assistant (Claude/Codex/WorkBuddy alike). The loop fuses
  Stanford STORM multi-perspective research, contradiction mapping, a synthesis
  briefing, a peer-review self-check, curated resource selection, Vygotsky's
  learning ladder (Zone of Proximal Development), Pareto 20% core study, active
  recall testing (testing effect / retrieval practice), the Feynman learning
  technique, and a one-page cheat sheet. It also bundles the built-in Feynman
  perspective advisor (naming != understanding, cargo-cult detection,
  anti-self-deception) for on-demand "explain like Feynman" or "is this cargo
  cult" requests. Supports two modes: (A) run the full 1->10 loop, or (B) invoke
  any single step or the Feynman perspective on demand. Use when the user wants
  to systematically learn, study, research, or master a subject; prepare for a
  talk, report, interview, or exam; build a structured, challenge-ready
  understanding of an unfamiliar domain; or apply a Feynman lens to a problem.
  Trigger phrases include "学习 X", "研究 X", "搞懂 X", "系统学习", "用 AI 学习", "10倍速学习",
  "备考", "梳理 X", "用费曼视角看", "这是不是 cargo cult", "命名不等于理解", "feynman perspective",
  "费曼学习法".
agent_created: true
disable-model-invocation: true
---

# 科学生产力学习闭环（Scientific Learning Loop）

## 用途
把任意陌生主题，用 AI 跑完「调研 → 深化 → 记忆 → 回顾」的 10 步闭环，达成**可对话、可上手、可复用**的真理解，而不是「收藏即学会」的假习得。该方法是大刘《用 Claude/Codex/Workbuddy 10 倍速学习任何知识》一文的适配版，融合了 Stanford STORM 论文与 Rahul（@sairahul1）的十倍速学习法，并补上了 STORM 原作者自承缺失的自我批判环节。

内置**费曼能力**（见 `references/feynman.md`）：「费曼学习法」用于第 9 步；「费曼视角思维框架」作为按需顾问，可独立调用，也可增强第 2/3/4 步的自我批判。原独立 `feynman-skill` 已整合进本技能并删除。

## 何时使用
- 用户想系统学习 / 研究 / 搞懂某个新领域、新概念、新技术。
- 用户要准备演讲、汇报、面试、考试前的结构化梳理。
- 用户表达「用 AI 学习 X」「十倍速学习」「系统搞懂 X」「给我做个学习闭环」等意图。
- 用户要「用费曼视角看 X」「这方案是不是 cargo cult」「我真的理解还是只记住了名字」。

## 两种运行模式
- **模式 A · 完整闭环**：顺序执行 1→10，适合从零系统拿下陌生领域。每步使用 `references/prompts.md` 中对应提示词（已适配占位符）。
- **模式 B · 按需调用**：只跑需要的那一步，或只调用内置费曼视角。例如：
  - 只做第 8 步备考、只做第 10 步生成速查卡、只做第 1–4 步做主题调研。
  - 「用费曼视角看 X」「这方案是不是 cargo cult」「我真的理解还是只记住了名字」→ 加载 `references/feynman.md` B 部分，按费曼思维框架回应。
  - 单步可串接：调研（1–4）后单独接费曼视角做自我批判，再接第 10 步压缩。

## 领域专属视角库（按需加载）

当主题命中「建议即责任」的高风险领域时，第 4 步的第 6 视角应优先从 `references/domain-lens.md` 取对应领域视角（投资=合规红线、医疗=循证等级、法律=法域资质、工程=失效模式）。**该文件默认不进上下文，仅在主题命中时按需载入**，不撑默认体积。加载后仍叠加 🔒 费曼安全闸。详见 `domain-lens.md` 的「加载规则」。

## 闭环总览（10 步）
1. **五视角 STORM**——让 5 类专家（实践者 / 学者 / 怀疑者 / 经济学家 / 历史学家）各给一份截然不同的解读。
2. **矛盾图谱**——让视角互相冲突，定位全领域共识（大概率是真）与盲区（可能是最大发现）。
3. **综合简报**——收拢成可决策简报：一句话总结 + 5 个按可靠性排序的发现 + 隐藏关联 + 行动建议 + 前沿问题。
4. **同行评审自检**——给结论逐条打分、找出最没把握的环节、补第 6 视角 + **默认叠加费曼视角**（货物崇拜检测 + 反自欺审查，见 `prompts.md` 第 4 步）。若主题命中投资 / 医疗 / 法律 / 工程安全等高风险领域，第 6 视角应优先从 `references/domain-lens.md` 取对应领域视角（按需加载）。**此步不可跳过**：STORM 存在来源偏差、事实错配的已知短板，靠它补齐自我批判。
5. **资源筛选**——只留 5 个最值钱资源，排成一周路径，明确标出被高估的坑；收藏夹里的 500 个先让它们躺着。
6. **学习阶梯**——按维果茨基「最近发展区」拆 5 级（初学者→自信实践者），永远知道自己在第几级、下一步去哪。
7. **2 小时啃核心 20%**——Pareto：先拿下次级就能上手干活的那 20%，而非从第一级慢爬。
8. **考到我崩溃**——主动回忆 / 检索练习（testing effect）：由易到难逐题考，定位理解边界，把"感觉懂了"的水分挤出来。
9. **费曼循环**——用 12 岁能懂的话讲清，卡住处回炉，直到解释简单、准确、完整（内置「费曼学习法」，见 `references/feynman.md` A 部分）。
10. **一页速查表**——压缩成 5 分钟可过完的速查卡：定义 + 核心条目 + 真实场景 + 易错点 + 上场清单 + 快问快答。

## 如何运行
- **占位符替换**：`{{TOPIC}}`（研究主题）、`{{CONCEPT}}`（具体概念）、`{{MY_ROLE}}`（用户角色 / 身份）。
- 第 4 步务必认真：它是对抗 STORM 来源偏差的关键安全闸，且**默认启用货物崇拜检测 + 反自欺审查**（费曼视角，无需手动追加）。
- 跑完一轮后，建议用户进入「21 天坚持周期」：每学一个主题就跑一遍闭环，而非收藏即止。
- **费曼能力已内置**：原独立 `feynman-skill` 已整合进本技能并删除；其「费曼学习法」（第 9 步）与「费曼视角思维框架」（按需顾问）现统一在 `references/feynman.md`，无需再调用独立技能。

## 科学依据（详见 `references/evidence.md`）
| 原理 | 来源 | 可信度 |
|------|------|--------|
| STORM 多视角 + 检索 | Stanford OVAL, NAACL 2024（Shao et al., `2024.naacl-long.347`） | 高 |
| 测试效应 / 检索练习 | Roediger & Karpicke 2006；Karpicke & Roediger 2008 | 高 |
| 最近发展区（ZPD） | Vygotsky，教育心理学标准构念 | 高 |
| 费曼技巧（学习法） | 流行教学法启发，与测试效应 / 精细加工逻辑一致 | 中 |
| 费曼视角框架 | 基于费曼著作 / 演讲 / 访谈提炼的思维顾问（原 feynman-skill 整合） | 中（方法论启发，非实验验证） |
| Rahul 四要素（路径/测试/压缩/反馈环） | 社媒经验帖，未同行评审 | 中低 |

## 局限与边界（运行前须知）
- 「10 倍速」「18 个月窗口期」为文章激励性表述，**无实证支撑**，仅作动机，不当事实。
- 「博士级调研 40–60h → 几分钟」为作者转述，论文摘要未直接给出该数字，视作示意性夸张。
- 闭环强依赖用户**主动执行 + 诚实自评**；AI 不替代真实输入与练习，"收藏不看"等于没学。
- 第 1 步的多视角模拟依赖模型角色扮演质量；对高度专业 / 快速变化的领域，建议在第 4 步补充真实检索（如联网查证）而非纯靠模型内知识。
- 费曼视角框架含诚实边界：不辩护费曼个人行为问题；对哲学 / 社科有偏见盲点；无法预测其对当代 AI 的真实立场。
