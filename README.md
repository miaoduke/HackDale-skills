# HackDale Skills — 可复用 AI Agent Skills 集 / Collection of Reusable AI-Agent Skills

> This repo is a **living collection of AI-agent skills**, distilled from real hands-on projects (e.g. the *Jiaolong 15K* and *Acer A615-51G* optimization public releases). Each skill is a self-contained `SKILL.md` that an AI agent can load on demand, with a link (soft-link layer) back to the full source playbook for deep detail.
>
> 本仓库是一个**可持续生长的 AI Agent skills 集合**，沉淀自真实落地项目（如 *蛟龙15K* 与 *Acer A615-51G* 优化方案的公开发布）。每个 skill 是独立的 `SKILL.md`，AI agent 可按需加载，并通过软链层链接回完整源经验库以深入参考。

---

## ⚠️ Disclaimer / 免责声明

**English:**
- This is an **unofficial, personal-study** skills collection. It is **not affiliated with, endorsed by, or the official product of** any vendor (Mechrevo/Uniwill, Acer, Microsoft, NVIDIA, Linux Mint, or GitHub).
- Skills here instruct reading/writing **real system knobs and issuing publish commands**. A wrong step can destabilize a system, leak personal data, or affect a shared/public repo. **Use at your own risk.**
- The repo ships **methodology and reusable instructions only**. It does **not** include OEM binaries, decompiled artifacts, credentials, or personal machine data. All identifiers are **desensitized** (`<USER>`, `<HOSTNAME>`, `<WIN_C_UUID>`, `<REDACTED_PWD_SALT>`) — replace placeholders with your own values before use.

**中文：**
- 本仓库为**非官方、个人学习用途**的 skills 集合，与任何厂商（机械革命/Uniwill、Acer、微软、NVIDIA、Linux Mint、GitHub）**无关联、非官方产品**。
- 本仓库的 skills 会指导**读写真实系统开关、执行发布操作**。操作不当可能导致系统不稳定、个人数据泄露或影响共享/公共仓库。**风险自负。**
- 仓库**只包含方法论与可复用指令**；**不含** OEM 二进制、反编译产物、凭据或个人机器数据。所有标识均已脱敏（`<USER>`、`<HOSTNAME>`、`<WIN_C_UUID>`、`<REDACTED_PWD_SALT>`）——使用前请把占位符替换为自己的值。

---

## 🧩 How this collection is organized / 集合组织方式

```
HackDale-skills/
├── skills/
│   ├── github-publish-redact/         发布前脱敏与保密
│   ├── github-publish-compliance/     社区文件与合规
│   ├── github-publish-readme/         README 双语工程
│   ├── github-publish-git-safe/       本地 git 安全初始化与提交
│   ├── github-publish-push-scan/      建仓推送与安全扫描
│   ├── github-publish-ops/            发布后运营与迭代升级
│   ├── agnes-multimodal/              Agnes 多模态生成客户端
│   ├── bilinote-skill/                B 站/笔记处理
│   ├── cli-skill-calibrator/          CLI 技能校准
│   ├── darwin-skill/                  达尔文研究流水线
│   ├── Exam2Knowledge/                考试→知识库
│   ├── opencode-compose-max/          智能混合工作模式（Compose-Max）
│   ├── opencode-compose-next/         交互式紧凑工作流（Compose-Next）
│   ├── opencode-max/                  完全自主执行模式（Max）
│   ├── ponytail/                      懒人极简哲学
│   ├── ponytail-toolkit/              Ponytail 按需工具箱
│   ├── retail-investors/              散户投资框架
│   ├── scientific-learning-loop/      科学学习循环
│   ├── xiaohongshu-ops-framework/     小红书运营框架
│   ├── deepseek-image-ocr/            无视觉模型的图片识读桥接
│   ├── github-mirror/                 所有镜像下载
│   ├── accounting-basics/             会计专业技能知识卡（166 卡）聚合
│   ├── cpa-financial-management/      注会《财务成本管理》知识卡（442 卡）聚合
│   └── cpa-financial-management-expert/ 注会《财务成本管理》专家团版
├── assets/                         打赏二维码（署名与收款沿用原经验库）
├── .github/                        SECURITY · FUNDING
├── LICENSE · THIRDPARTY · CONTRIBUTING · CHANGELOG
└── README.md
```

**Structure rule (soft-link layer):** each skill points to its full source via the `Source / 深挖参考` line. The source of truth is the `github-publish-playbook` repo; don't duplicatively fork whole stages here. **结构规则（软链层）：** 每个 skill 通过 `Source / 深挖参考` 行指回完整源。事实源头是 `github-publish-playbook` 仓库；本仓不重复维护整段阶段正文。

**Adding a new skill / 新增 skill：** add `skills/<kebab-case-name>/SKILL.md` with the standard frontmatter and body, then update the README index + CHANGELOG. See the `github-publish-ops` skill for the exact recipe. **新增 skill：** 添加 `skills/<kebab-case-name>/SKILL.md`（标准 frontmatter + 正文），再更新 README 索引与 CHANGELOG。具体步骤见 `github-publish-ops` skill。

---

## 📚 Available skills / 现有 skills 索引

### A. GitHub Publish engineering / 发布工程类
| Skill 技能 | What it does 作用 | When to invoke 触发场景 |
|---|---|---|
| [**github-publish-redact**](skills/github-publish-redact/SKILL.md) | Redact usernames/hostnames/UUIDs/passwords/IPs before public release 公开前脱敏与保密 | Preparing any repo/docs for public publish 准备公开任何仓库/文档时 |
| [**github-publish-compliance**](skills/github-publish-compliance/SKILL.md) | Generate LICENSE/THIRDPARTY/SECURITY/CONTRIBUTING/CHANGELOG/FUNDING 生成合规社区文件 | Creating a new public repo / adding project to OSS org 新建公共仓库时 |
| [**github-publish-readme**](skills/github-publish-readme/SKILL.md) | Write/translate bilingual EN→ZH README with disclaimer & capability table 撰写双语 README | Creating or translating a project README 新建或翻译 README 时 |
| [**github-publish-git-safe**](skills/github-publish-git-safe/SKILL.md) | Safe git init/stage/commit without leaking privates; filter-repo history rewrite 安全 git 提交 | First commit of a to-be-published repo, or history rewrite 首提交或历史重写时 |
| [**github-publish-push-scan**](skills/github-publish-push-scan/SKILL.md) | Create repo Private→push→verify→enable scanning→flip Public 建仓推送与安全扫描 | Publishing a finished repo to GitHub 发布成型仓库时 |
| [**github-publish-ops**](skills/github-publish-ops/SKILL.md) | Post-release ops + iteratively grow the skills collection 发布后运营与迭代 | Maintaining public repos or adding new skills 维护仓库/新增 skill 时 |

### B. General-purpose skills / 通用技能类
| Skill 技能 | What it does 作用 | When to invoke 触发场景 |
|---|---|---|
| [**deepseek-image-ocr**](skills/deepseek-image-ocr/SKILL.md) | Read an image's content by routing to DeepSeek web chat when the active model has no vision 无视觉模型时识读图片内容 | Model got a vision-unsupported image input / "识图" 模型无法看图 / 需识图时 |
| [**github-mirror**](skills/github-mirror/SKILL.md) | Download cached-Actix GitHub archives/raw files through probe-tested public mirrors with fallback 经镜像加速 GitHub 下载 | GitHub download slow/fails / "github加速" GitHub 下载慢或失败时 |
| [**agnes-multimodal**](skills/agnes-multimodal/SKILL.md) | Multimodal generation (image/video) via Agnes AI with env-based key rotation 多模态生成客户端 | Generating images/video via Agnes API 阿格尼斯多模态生成时 |
| [**bilinote-skill**](skills/bilinote-skill/SKILL.md) | Bilibili/notes capture & processing workflows 笔记/视频处理 | Processing B-station notes or videos 处理 B 站/笔记时 |
| [**cli-skill-calibrator**](skills/cli-skill-calibrator/SKILL.md) | Calibrate local CLI agent skills against the real runtime, docs & API 校准 CLI 技能 | A CLI-based skill fails due to version/driver drift skill_id 漂移导致调用失败时 |
| [**darwin-skill**](skills/darwin-skill/SKILL.md) | Darwin-style evidence research pipeline 达尔文式研究流水线 | Deep evidence-based research 需循证研究时 |
| [**Exam2Knowledge**](skills/Exam2Knowledge/SKILL.md) | Convert exam/tutor materials into a knowledge base 考试→知识库 | Turning study/exam content into reusable knowledge 考试资料转知识库时 |
| [**opencode-compose-max**](skills/opencode-compose-max/SKILL.md) | Route tasks to Max or Compose-Next smartly 智能混合模式 | "compose-max" 或"你来判断用哪种模式"时 |
| [**opencode-compose-next**](skills/opencode-compose-next/SKILL.md) | Interactive end-to-end workflow with user checkpoints 交互式紧凑工作流 | "compose-next"/"先问我再动手"时 |
| [**opencode-max**](skills/opencode-max/SKILL.md) | Fully autonomous end-to-end execution 完全自主执行 | "max"/"完全自主" 无人值守执行时 |
| [**ponytail**](skills/ponytail/SKILL.md) | Force the laziest solution that actually works 懒人极简哲学 | Avoiding over-engineering 需要极简方案/去过度工程时 |
| [**ponytail-toolkit**](skills/ponytail-toolkit/SKILL.md) | On-demand ponytail utilities (review/audit/debt/gain/help) 按需工具箱 | "ponytail-review"/"审计过度设计"时 |
| [**retail-investors**](skills/retail-investors/SKILL.md) | Retail-investor research framework 散户投资研究框架 | Personal stock/investment research 个人投资研究时 |
| [**scientific-learning-loop**](skills/scientific-learning-loop/SKILL.md) | Evidence-driven scientific learning cycle 科学学习循环 | Structured learning with verification 需循证学习时 |
| [**xiaohongshu-ops-framework**](skills/xiaohongshu-ops-framework/SKILL.md) | XiaoHongShu (RED) content & account operations framework 小红书运营框架 | Creating/optimizing 小红书 content & ops 小红书内容/运营时 |

### C. Knowledge-domain skills / 知识领域类（教材知识卡聚合）
| Skill 技能 | What it does 作用 | When to invoke 触发场景 |
|---|---|---|
| [**accounting-basics**](skills/accounting-basics/SKILL.md) | 166-card accounting knowledge collection (double-entry, vouchers, ledgers, statements, ratios, fraud detection) 会计专业技能知识卡（166 卡） | Practical accounting/analysis task: journal entry, account classification, bank reconciliation, ratio analysis 会计记账/凭证/账簿/报表/比率分析时 |
| [**cpa-financial-management**](skills/cpa-financial-management/SKILL.md) | 442-card financial cost management collection (time value, valuation, CVP, costing, capital structure, performance) 注会《财务成本管理》知识卡（442 卡） | CPA exam review or managerial-finance calc: WACC, CVP, DCF, budgeting, ABC 财管考试复习/具体计算任务时 |
| [**cpa-financial-management-expert**](skills/cpa-financial-management-expert/SKILL.md) | 113-SKU query-able expert team via mapping.md / skills.json / eureka.md 注会《财务成本管理》专家团版（结构化 113 SKU） | Precise knowledge lookup by concept/domain/confidence, or cross-topic knowledge graph 按知识点精确检索/看跨领域知识图谱时 |

*AgenAI note: invoke by matching the "When to invoke" trigger.* / *给 AI agent：按「触发场景」匹配调用。*

---

> **版权提示 / Copyright:** The three knowledge-domain cards are AI-generated
> study excerpts distilled from copyrighted textbooks (会计学全图解 / 2026注会
> 《财务成本管理》) via pdf2skill. They are for **personal study only**; the
> underlying copyright belongs to the respective authors/publishers. 三个知识领域
> 卡为受版权教材经 pdf2skill 的 **AI 学习摘录，仅供个人学习**，版权归原作者/出版社，
> 不保证完整性，不构成专业意见。

---

## 🔚 Footer / 页脚

### 贡献 · 安全 · 更新 / Contribute · Security · Updates
- **Contribute:** see [CONTRIBUTING.md](CONTRIBUTING.md). **贡献：** 见 [CONTRIBUTING.md](CONTRIBUTING.md)。
- **Security:** report vulnerabilities privately via `.github/SECURITY.md`. **安全：** 漏洞请经 `.github/SECURITY.md` 的私有渠道报送。
- **Updates:** see [CHANGELOG.md](CHANGELOG.md). **更新：** 见 [CHANGELOG.md](CHANGELOG.md).

### 许可 / License
MIT — see [LICENSE](LICENSE). **MIT 许可**，见 [LICENSE](LICENSE)。

### 支持 / Support
If this helps you and you feel like it, a voluntary tip is welcome — it does **not** change the free MIT license. 如果有帮助并且愿意，欢迎自愿打赏——**不改变** MIT 免费许可。

<p align="left">
  <img src="assets/donate_wechat.jpg" width="240" alt="WeChat 微信打赏"/>
  <img src="assets/donate_alipay.jpg" width="240" alt="Alipay 支付宝打赏"/>
</p>

---

*HackDale Skills · © 2026 <USER> · MIT · Bilingual (EN → ZH) · Living collection*