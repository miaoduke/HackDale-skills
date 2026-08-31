---
name: opencode-compose-max
description: >
  智能混合模式（Compose-Max）— 自动评估任务特征，在 opencode-compose-next（交互式）与
  opencode-max（全自动）之间动态选择最佳工作模式。需求明确+低风险+时间紧迫用 max； 需求模糊或决策影响高用
  compose-next。当用户说 "compose-max"、"智能混合"、 "你来判断用哪种模式"、"auto mode"
  时启用。本技能负责路由与切换判定，选定后按对应技能执行。
version: 1.0.0
agent_created: true
license: MIT
---

# Compose-Max（WorkBuddy 适配版）

> **与 WorkBuddy 内置模式的关系**：本技能是"模式选择器"，本身不替代 Craft/Plan/Ask，
> 而是根据任务特征在 `opencode-max`（≈极致 Craft）与 `opencode-compose-next`（≈结构化 Plan）
> 之间做决策路由。它是这两个技能的入口与调度器。
> 调用方式：说出上面的触发词，或用 Skill 工具加载 `opencode-compose-max`。

智能混合 agent：自动评估任务，在 compose-next（交互式）和 max（全自动）之间选择。

## 工作流程

### Phase 0: 模式评估（必须首先执行）

分析任务特征，选择工作模式：

| 特征 | compose-next 信号 | max 信号 |
|------|------------------|----------|
| 需求明确度 | 模糊 / 需要探索 | 明确 / 具体 |
| 决策影响 | 高 / 不可逆 | 低 / 可逆 |
| 时间压力 | 低 | 高 |
| 技术确定性 | 低 / 需要调研 | 高 / 熟悉技术栈 |
| 代码影响范围 | 大 / 核心模块 | 小 / 边缘功能 |

**选择规则**：
- 任何高影响决策 → compose-next
- 需求模糊 + 高不确定性 → compose-next
- 需求明确 + 低风险 + 时间紧迫 → max
- 其他情况 → max（快速执行）+ 事后审查

在输出中明确声明选择的模式和原因（一句话即可）。

### Phase 1: 执行路由

根据选择的模式，加载并执行对应技能：

- **compose-next 路径** → 用 Skill 工具加载 `opencode-compose-next`，按其流程执行：
  定向 → Grill → Spec → Workspace → Implement → Verify → Review → Finalize → Finish
- **max 路径** → 用 Skill 工具加载 `opencode-max`，按其流程执行：
  定向 → Spec → Workspace → Implement → Verify → Review → Finalize → Finish（无暂停，保守决策）

> 若运行环境不支持在技能内再加载技能，可直接把对应技能（opencode-max / opencode-compose-next）
> 的完整流程内联执行——两个技能的 SKILL.md 已包含全部步骤，本技能只负责路由判定。

## 模式切换规则

执行过程中，若发现：
- 任务比预期复杂 → 切换到 compose-next
- 决策影响范围扩大 → 切换到 compose-next
- 遇到阻塞性问题 → 切换到 compose-next

**向下切换（max → compose-next）允许**，无需用户确认（更安全）。
**向上切换（compose-next → max）需要用户确认**（减少自主度需用户同意）。

每次切换都用一句话说明原因。

## 记忆集成（映射到 WorkBuddy）

写入项目 `.workbuddy/memory/MEMORY.md` 或当日 `YYYY-MM-DD.md`：
- 模式选择决策和原因
- 任务特征评估结果
- 执行过程中的模式切换记录

跨项目的模式偏好可写入用户级 `~/.workbuddy/MEMORY.md`。
