---
name: cli-skill-calibrator
description: 校准/更新本地「CLI 型」agent
  技能时，先对照真实运行时(取最高版本)与官方文档/API，消除因版本漂移、命令被移除、参数格式错、skill_id 命名不一致导致的调用失败。
agent_created: true
disable-model-invocation: true
---

# 校准 CLI 型 agent 技能

当你要**修复或更新**一个"靠调用本机 CLI 程序干活"的 agent 技能（典型如 `node xxx.js`、`python cli.py`、某 `.exe`；本例为天天基金 `ttskill`），且它现在调用报错、或官网发了新版文档，用本技能的流程，避免把过时/错误命令写进文档。

## 何时触发
- 技能调用报：`未知命令` / `unknown subcommand` / `缺少参数` / `command not found` / 字段名对不上
- 用户要求"参考官网更新某 CLI 技能，减少出错"
- 你拿到一个 SPA 官网链接，却抓不到真实内容

## 核心心法（一句话）
文档（无论旧 SKILL.md 还是官网）都可能是过时的；**唯一不会骗你的是这台机器现在实际能执行的那个二进制**。但机器可能装了多个版本——所以「取最高版本」比「取第一个」安全。

---

## 流程

### 1. 定位真实运行时（绕过包装层）
- 找程序**本体**，别找 Windows 包装层（`.cmd` / `.bat` 在沙箱/headless 环境常被安全策略禁止）。
  - 对 Node 程序：用其自带的 `runtime/node.exe` 直调 `xxx.js`，不用 PATH 里的 node，也别碰 `.cmd`。
- **多版本共存时**（致命坑）：
  - ❌ `ls -d …/* | head -1` —— 按字母序取第一个，会取到更旧的版本
  - ✅ `ls -d …/* | sort -V | tail -1` —— 取语义最高版本

### 2. 读真实契约（别推断，实测）
- 跑 `<runtime> --help` 拿**真实的子命令列表**（不要凭记忆或旧文档）。
- 对"列出技能/路由"类命令，直接跑它（如 `skill list` / `agent-entry show`）。
- 对"调用"类，挑一个已知存在的目标**真跑一次**验证参数格式：`--action` 名、`--body` 是否顶层 JSON、缺省值等。
- **报错信息本身就是最好的 schema**：`缺少参数: XXX` → 照 XXX 改名重发；`未知命令：Y` → 该命令在此版本不存在。

### 3. 对官方信源交叉验证（官网抓不到就挖源）
WebFetch 对 SPA / hash 路由页面往往只拿到空壳（如 `skills.xxx.com/#route=skills`）。换这些手法：
- `curl` 抓**原始 HTML** → 找 JS bundle（`<script src=".../assets/index-*.js">`）或内嵌 `window.__` 数据。
- 在 bundle 里搜 `api` / `fetch(` / `skill_id`，定位真实数据 API 端点。
- 找官方**「安装说明」`.md`**（常见路径如 `…/xxx-cli-install.md`），里面通常写明规范命令与调用体格式。
- 调官方**业务包/基础包解析 API**（形如 `openapi/skill-package/list`、`openapi/base-package/resolve?platform=&arch=&env=prod`），拿权威 skill 清单 + 最新版本号。
- ⚠️ **警惕"展示组件"坑**：官网营销页/热门榜里的名字（如 `FUND_*`）常和真实 invoke id（`TTFUND_*` / `ACCOUNT_*`）不一致 —— 以 API / 本地 `list` 为准，别照搬页面字符串。

### 4. 判据：本地 vs 官网，谁为准
- 先经官方 `base-package/resolve` 确认**最新版**，再比本机实际装了哪个版本。
- 本机落后 → **提示升级**，别把旧命令写进文档；本机更新/等同 → 以本机为准，但标注版本号。
- 若本地与官网命令名冲突：**先确认本机到底跑的是哪个版本**再下结论（本技能的诞生正是因没做这一步而翻车）。

### 5. 写"自愈"式文档
- 把"拿不准就问运行时"写进技能：`--help` / `skill info <id>` / 官方路由命令，作为权威参数来源，而非硬编码一长串易过期的参数。
- 可保留已验证的"快照表"方便快速调用，但注明「实时以运行时 `agent-entry show` / `skill list` 为准」。

### 6. 打包成可移植技能
- 技能目录只放 `SKILL.md`（及其 `references/`、`scripts/`），不要塞日志/缓存。
- 路径用环境变量（`$LOCALAPPDATA`、`$HOME`）或 `/c/Users/*` 兜底，**绝不写死用户名**。
- 打包：`zip` 内结构为 `skill-name/SKILL.md`，解压后把文件夹放到目标 agent 的 `skills/` 目录即生效。

---

## 本次实证（天天基金 ttskill 案例）
- 本机**并存 0.1.1 与 0.1.2**；首次用 `head -1` 取到旧版 0.1.1（缺 `agent-entry`）→ 误判 `agent-entry` 被"移除"并删之。
- 官方 `base-package/resolve` 当前 = **0.1.2**；`skill-package/list` 业务包 = **33 个**，与本地 `skill list` 的 33 个 **1:1 吻合**。
- 官网 JS bundle 里的 `FUND_*` 仅是"热门技能"展示组件，**不是真实 invoke id**。
- 修正：探测改 `sort -V | tail -1`；恢复 `agent-entry show/refresh/bootstrap` 为官方主路由；`--action` 必填且每技能自有动作名（多为 `query`）；body 为顶层 JSON。实测 0.1.2 探测 + `agent-entry show` + 真实 `invoke` 全链路通过。

## 自检清单（交付前过一遍）
- [ ] 运行时定位是否取了**最高版本**（非 head -1）
- [ ] 是否实测过 `--help` 与至少一次真实调用
- [ ] 是否与官方 API/安装文档交叉验证过版本与 skill 清单
- [ ] 是否标注了"实时以运行时为准"的自愈入口
- [ ] 技能文件是否无硬编码用户名、可跨机器/跨 agent 移植
