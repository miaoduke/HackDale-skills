---
name: ponytail-toolkit
description: >
  Ponytail 的五合一按需工具箱（不改代码、一次性输出），配合常驻的 ponytail 懒人模式使用。含五个子命令： (1) review ——
  针对单次 diff 的"过度工程"审查，触发："审查过度设计"/"这段是否过度设计"/"what can we
  delete"/"ponytail-review"； (2) audit —— 全仓库过度工程审计（排序清单），触发："审计过度设计"/"audit
  this codebase"/"find bloat"/"ponytail-audit"； (3) debt —— 把仓库里的 `ponytail:`
  注释收集成技术债台账，触发："ponytail debt"/"列出 deferred 的捷径"/"ponytail-debt"； (4) gain ——
  展示 ponytail 实测影响计分卡，触发："展示 ponytail 收益"/"what does ponytail
  save"/"ponytail-gain"； (5) help —— ponytail 模式/命令速查卡，触发："ponytail
  怎么用"/"ponytail help"/"ponytail-help"。
  仅用于编码/代码库相关请求；这些工具只列出发现、绝不擅自改代码。写代码本身的懒人行为由 ponytail 技能负责，不在此。
version: 4.8.4
agent_created: true
---

# Ponytail Toolkit

Ponytail 的按需工具箱：五个无状态、一次性的子命令。它们**只列出发现或展示信息，绝不擅自修改代码、不改变 ponytail 模式、不写标志文件**。

先判断用户要哪一个子命令，然后**只执行那一个**，用对应的输出格式：

| 用户意图 / 触发词 | 子命令 | 段落 |
|---|---|---|
| "审查过度设计"、"这段是否过度设计"、"what can we delete"、`ponytail-review` | review | § 1 |
| "审计过度设计"、"audit this codebase"、"find bloat"、`ponytail-audit` | audit | § 2 |
| "ponytail debt"、"列出 deferred 的捷径"、`ponytail-debt` | debt | § 3 |
| "展示 ponytail 收益"、"what does ponytail save"、`ponytail-gain` | gain | § 4 |
| "ponytail 怎么用"、"ponytail help"、`ponytail-help` | help | § 5 |

---

## § 1 · review — 单次 diff 的过度工程审查

Review diffs for unnecessary complexity. One line per finding: location, what
to cut, what replaces it. The diff's best outcome is getting shorter.

**Format:** `L<line>: <tag> <what>. <replacement>.`，多文件用 `<file>:L<line>: ...`。

**Tags:**
- `delete:` dead code, unused flexibility, speculative feature. Replacement: nothing.
- `stdlib:` hand-rolled thing the standard library ships. Name the function.
- `native:` dependency or code doing what the platform already does. Name the feature.
- `yagni:` abstraction with one implementation, config nobody sets, layer with one caller.
- `shrink:` same logic, fewer lines. Show the shorter form.

**Examples:**
- ✅ `L12-38: stdlib: 27-line validator class. "@" in email, 1 line, real validation is the confirmation mail.`
- ✅ `L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.`
- ✅ `repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.`
- ✅ `L52-71: delete: retry wrapper around an idempotent local call. Nothing replaces it.`
- ✅ `L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line.`

**Scoring:** 以唯一重要的指标收尾：`net: -<N> lines possible.`。无可删则输出 `Lean already. Ship.` 并停止。

**Scope:** 只管过度工程与复杂度。正确性 bug、安全漏洞、性能问题明确不在范围，交给正常 review。单个 smoke test / `assert` 自检是 ponytail 的最低要求，不是臃肿，绝不建议删除。只列出，不应用修复。

---

## § 2 · audit — 全仓库过度工程审计

ponytail-review 的仓库级版本：扫整个树而非单次 diff，按"能砍的量"从大到小排序。

**Tags:** 同 § 1（delete / stdlib / native / yagni / shrink）。

**Hunt:** 标准库或平台已自带的依赖、单实现接口、只有一个产品的工厂、只做转发的包装层、只导出一个东西的文件、死掉的 flag 和 config、手搓的标准库功能。

**Output:** 一行一条，排序：`<tag> <what to cut>. <replacement>. [path]`。以 `net: -<N> lines, -<M> deps possible.` 收尾。无可删则 `Lean already. Ship.`。

**Scope:** 同 § 1，只列不改，一次性。

---

## § 3 · debt — `ponytail:` 技术债台账

每个刻意的 ponytail 捷径都用 `ponytail:` 注释标注了它的天花板与升级路径。此命令把它们汇总成一份台账，防止 deferral 悄悄变永久。

**Scan:** grep 仓库中的注释标记，跳过 `node_modules`、`.git`、构建产物：

`grep -rnE '(#|//) ?ponytail:' .`（按你的技术栈补充其他注释前缀）

**Output:** 一行一条，按文件分组：

`<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.`

约定是 `ponytail: <ceiling>, <upgrade path>`，直接从注释里提取天花板与触发条件。需要每行归属人可加 `git blame -L<line>,<line>`。

**Rot flag:** 任何 `ponytail:` 注释若没写升级路径或触发条件，标 `no-trigger` —— 那些是会 silently rot 的。

以 `<N> markers, <M> with no trigger.` 收尾。无则 `No ponytail: debt. Clean ledger.`。

**Boundaries:** 只读只报，不改任何东西。用户要求持久化时，写入文件（如 `PONYTAIL-DEBT.md`）。一次性。

---

## § 4 · gain — 实测影响计分卡

被调用时展示以下计分卡。一次性：不改模式、不写标志文件、不持久化任何东西。

数字为已发布的基准中位数（5 个日常任务：邮箱校验、debounce、CSV 求和、倒计时、限流器；三个模型 Haiku/Sonnet/Opus），是**实测**而非按当前仓库计算。来源：上游 `benchmarks/` 与 README。

```
  ponytail gain                     benchmark median · 5 tasks · 3 models

  Lines of code   no-skill  ████████████████████  100%
                  ponytail  ██▌·················    6–20%   ▼ 80–94%
  Cost            no-skill  ████████████████████  100%
                  ponytail  █████▌··············   23–53%  ▼ 47–77%
  Speed           ponytail  ▸ 3–6× faster

  This repo:  ponytail-toolkit debt   (shortcuts you deferred)
              ponytail-toolkit audit  (what's still cuttable)
```

**Honesty boundary:** 这是基准中位数，不是当前仓库。绝不打印"你在这个仓库省了 X 行/token"这类逐仓数字——未写的版本从不存在，活仓里没有真实基线可减。唯一真实的逐仓数字来自 debt（可计数的台账），此卡指向它，而非编造。

---

## § 5 · help — 速查卡

被调用时展示以下参考卡。一次性，不改模式、不持久化。

**强度等级：**

| Level | Trigger | What change |
|-------|---------|-------------|
| **Lite** | `ponytail lite` | 照做，但一行点出更懒的替代方案。 |
| **Full** | `ponytail`（默认） | 梯子强制执行：YAGNI → stdlib → native → 一行 → 最小可行。 |
| **Ultra** | `ponytail ultra` | YAGNI 极端派。删除优于新增。构建前先质疑需求。 |

等级维持到被更改或会话结束。

**技能组成：**

| 技能 | 触发 | 作用 |
|-------|---------|--------------|
| **ponytail** | `ponytail` | 懒人模式本身，写代码时的默认行为。 |
| **ponytail-toolkit** | 见上表触发词 | 本工具箱：review / audit / debt / gain / help 五个一次性子命令。 |

**关闭：** 说 "stop ponytail" 或 "normal mode"，随时用 `ponytail` 恢复。`ponytail off` 同样有效。

**配置默认强度：** 默认 `full`，每会话自动激活（本项目通过用户级 MEMORY.md 常驻）。改：环境变量 `PONYTAIL_DEFAULT_MODE=ultra`（最高优先级），或配置文件 `~/.config/ponytail/config.json`（Windows：`%APPDATA%\ponytail\config.json`）里 `{ "defaultMode": "lite" }`。设 `"off"` 关闭自动激活。解析顺序：环境变量 > 配置文件 > `full`。

**更新：** WorkBuddy 没有 `/plugin` 自动更新流；同步上游 https://github.com/DietrichGebert/ponytail 的方式是 shallow clone 后对比 `skills/`、`hooks/`、`AGENTS.md`，把差异并入本地 `ponytail` / `ponytail-toolkit`（保留本地的 WorkBuddy 适配层：中文触发词与集成说明）。

**更多：** 完整文档与示例 https://github.com/DietrichGebert/ponytail

---

## 全局边界

- 五个子命令全部**只列出/展示，绝不擅自改代码**（"删不删、怎么删"的裁量权留给用户）。
- 不改变 ponytail 模式、不写标志文件（唯一例外：debt 在用户明确要求时可另存台账文件）。
- 仅用于编码/代码库相关请求，不用于通用知识、散文、翻译、摘要。
- "stop ponytail" / "normal mode" 时恢复常规风格。
