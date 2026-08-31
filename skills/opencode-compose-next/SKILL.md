---
name: opencode-compose-next
description: >
  交互式紧凑工作流（Compose Next）— 一体化端到端合约：定向 → Grill（结构化提问）→ Spec → Workspace →
  Implement → Verify → Review → Finalize → Finish，一个 agent 完成整个周期。
  适合需求或设计模糊、需要用户拍板高影响决策的任务。当用户说 "compose-next"、"交互式"、 "先问我再动手"、"走完整流程"、"guided
  workflow" 时启用。关键决策用 AskUserQuestion 工具问用户。
version: 1.0.0
agent_created: true
license: MIT
---

# Compose Next（WorkBuddy 适配版）

> **与 WorkBuddy 内置模式的关系**：本技能 ≈ 内置 **Plan（先想后做）** 的结构化增强版——
> 在 Plan 的"先规划"基础上，加入 Grill 决策门、Spec 文档契约、TDD 验证与 subagent 审查。
> 调用方式：说出上面的触发词，或用 Skill 工具加载 `opencode-compose-next`。

紧凑的端到端合约：定向 → Grill → Spec → Workspace → Implement → Verify → Review → Finalize → Finish。一个 agent 加载，无内部技能交接。

## Step 0 — 定向

**先读再问**：检查工作区、其指令文件（AGENTS.md / README / 现有规范）、最近更改和记忆文件，再问任何问题。不要问环境已回答的事实。

检查 `.workbuddy/memory/` 了解上下文：
- `MEMORY.md` — 项目功能状态、设计契约
- `~/.workbuddy/MEMORY.md` — 用户跨项目偏好
- 当日 `YYYY-MM-DD.md` — 近期决策与进展

决定工作形状：
- **完全约束的机械更改，无持久设计表面** → 跳过 Grill 和 Spec，直接 Workspace 然后 Implement
- **需求或设计模糊** → 先 Grill
- **需求清晰，功能值得持久文档** → 先 Spec

每条路径在 Implement 之前都经过 Workspace；没有分支跳过它。

## Grill — 结构化决策（映射到 AskUserQuestion）

一次解决一个决策轴。单个决策可在一次提问中捆绑多个依赖字段；不相关的决策需要分开轮次。

### 交互模式

使用 `AskUserQuestion` 工具处理每个用户决策：

- **先检查对话** — 如果答案已在其中或可推断，直接使用，不重复询问
- 将已知选择放在 `options` 中，每项有简洁 `label` 和解释后果的 `description`。先列出推荐项并标记 `(Recommended)`
- 对于重要选择，包含 2-3 个可行替代方案
- 当选择无法枚举时，使用自由文本问题（options 留空让用户自填）
- **每次最多 3 个问题** — 三个是上限，不是目标
- 当没有剩余决策时，不要请求继续许可

### Never-Ask 处理

如果 `AskUserQuestion` 因故不可用，**自己解决这一个决策**并继续：

1. 选择标记 `(Recommended)` 的选项，当工作区证据仍支持且可无人值守运行时
2. 否则选择证据支持的最接近最小范围选项；优先纯文本、非交互工作
3. 如果决策包括破坏性或不可逆操作，选择保留进度的非破坏性路径；永远不要自动批准破坏性选项
4. 在响应中说明选择的选项和原因

Never-Ask 仅适用于当前决策。在每个后续决策点，再次调用 `AskUserQuestion` — 不禁用未来问题或暂停工作流。

## Spec — 每功能一个文档（带版本控制）

在仓库根目录维护功能文档 `docs/compose/spec/<feature-name>.md`（不要加日期；用户指定位置可覆盖）。原地编辑现有文档；不创建单独的计划或报告文件。

### 模板

```markdown
---
feature: <feature-name>
status: designed | in-progress | delivered
updated: YYYY-MM-DD
branch: <branch-name>
commits: <base-sha>..<head-sha> # 交付时填充
version: 1 # 每次重大更新递增
---

# <功能名称>

## 报告

## [S1] 问题
描述用户可见的问题。

## [S2] 设计
记录选择的行为和实现所需的契约。

## [S3] 范围外
声明明确边界。

## 决策记录
- [决策] <决策内容> — 原因：<原因> — 替代：<替代方案> — 代价：<代价>

## 任务
- [ ] T1: <工作项> — 验收：<可观察结果> (covers: S2)
- [ ] T2: <工作项> — 验收：<可观察结果> (covers: S2; depends: T1)
```

### 设计时规则

- 保持 `Report` 空白并设置 `status: designed`
- 标题更改时保持 `[Sn]` 锚点稳定；永不重新编号现有锚点
- 记录已确定的决策和精确契约，不是探索历史或文件级代码转储
- 每个任务是最小独立可验证工作项，给它可观察的验收标准
- 移除占位符（TBD、"处理边缘情况"、对未指定类似工作的引用）
- 根据更改缩放细节

实现前，修复模糊需求、矛盾、未解析引用和不可验证验收标准。

## Workspace — 工作区隔离

**永远不要在 main 或 master 上开始实现**，除非用户明确同意。

1. 比较 `git rev-parse --git-dir` 与 `git rev-parse --git-common-dir`；若不同，使用当前链接工作区，不嵌套另一个
2. 除非用户或工具已选工作区，在 `.worktrees/` 下创建链接工作区；验证被忽略：`git check-ignore -q <directory>`，否则写 `*` 到 `.worktrees/.gitignore`
3. **强制读取项目指令**：实现前必须读取 AGENTS.md、README、package.json 等，了解项目约定

## Implement

使用功能文档作为需求来源。存在功能文档时，在第一个实现提交设 `status: in-progress`。按依赖顺序执行任务。

### TDD 流程

对有廉价重现的行为更改：写失败测试 → 确认因预期原因失败（**强制**）→ 实现最小修复 → 确认通过 → 提交。

### 测试原则

- 测试公共行为；不要在期望值中复制生产逻辑，不要添加仅测试的生产 API，优先真实实现 over mock
- 故障前先重现并从错误、diff、最近提交识别根本原因
- **两次修复失败后，停止补丁并重新推导原因**

继续执行任务，不要例行公事地暂停检查进度。只在以下情况停止：无法解决的未决产品决策、无法绕过的阻塞、需要同意的破坏性操作、或完成。

## Verify — 证据驱动验证

**铁律：无验证证据 = 无完成声明**

按复杂度缩放证据收集（同 max）：单一事实 1-2 命令 / 中等 3-5 / 深度 5-10。

验证清单：从正确目录运行相关测试/类型检查/构建 → 阅读输出并记录每个命令和结果 → 标记已知基线失败为 `PRE-EXISTING` → 不要以前次输出或 subagent 报告代替新鲜证据。

验证和审查严格顺序：等待所有验证命令退出后再派遣审查者。

## Review

实现已验证且在最终化功能文档之前，派遣一个 fresh subagent（Agent 工具）审查完整更改：
- 适用规范章节和验收标准
- 工作区路径、base 分支、base SHA、head SHA 和精确 diff 命令
- 紧凑验证摘要：每个命令一行，带 `PASS`/`FAIL`/`PRE-EXISTING`

要求独立结论：规范合规 / 正确性 / 代码库一致性。将未满足或不可验证的验收标准和正确性 bug 分类为 critical，修复后重新验证并重新审查。

## Finalize — 提交功能文档

审查通过后，完成分支之前，最终化功能文档：
1. 设 `status: delivered`，更新 `updated:`，记录审查范围 `<base-sha>..<head-sha>`
2. 检查完成的任务；未完成任务留空，若阻止验收则不要声称交付
3. 用以下内容替换 `Report`：

```markdown
## 报告

**构建了什么** — 1-3 段简洁描述最终行为。
**验证** — 运行的命令和观察到的结果。
**决策日志** — 关键选择及其原因。
**历程日志** — 最多 5 个条目：死胡同、转折或可转移教训。
```

## Finish

不要自动完成。最终化后，报告分支、base、head SHA、工作区、功能文档路径，并建议关闭操作（本地合并 / 开 PR / 仅推送 / 保留分支）。

若关闭路径不明确，用 `AskUserQuestion` 确定：关闭操作、目标基础分支、保留或删除工作区。

## 记忆集成（映射到 WorkBuddy）

| 时机 | 写入位置 | 内容 |
|------|----------|------|
| Grill 决策后 | 项目 `.workbuddy/memory/MEMORY.md` 或当日日志 | 决策、原因、替代方案 |
| Spec 完成后 | `docs/compose/spec/<feature>.md` 本身含状态 | 功能状态、设计契约 |
| Finalize 后 | 项目 `.workbuddy/memory/MEMORY.md` | 交付状态、SHA 范围 |

**写入规则**：写在对话中不在结束时 — 单一明确陈述就足够立即写入；先写再延迟（即将问澄清或搜索时先写已知）；每行测试"用户说了这个吗？没说就不写"；不写本技能的研究输出或建议，只写用户确认。
