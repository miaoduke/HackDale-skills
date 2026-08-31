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
│   ├── github-publish-redact/       SKILL.md  发布前脱敏与保密
│   ├── github-publish-compliance/   SKILL.md  社区文件与合规
│   ├── github-publish-readme/       SKILL.md  README 双语工程
│   ├── github-publish-git-safe/     SKILL.md  本地 git 安全初始化与提交
│   ├── github-publish-push-scan/    SKILL.md  建仓推送与安全扫描
│   └── github-publish-ops/          SKILL.md  发布后运营与迭代升级
├── assets/                         打赏二维码（署名与收款沿用原经验库）
├── .github/                        SECURITY · FUNDING
├── LICENSE · THIRDPARTY · CONTRIBUTING · CHANGELOG
└── README.md
```

**Structure rule (soft-link layer):** each skill points to its full source via the `Source / 深挖参考` line. The source of truth is the `github-publish-playbook` repo; don't duplicatively fork whole stages here. **结构规则（软链层）：** 每个 skill 通过 `Source / 深挖参考` 行指回完整源。事实源头是 `github-publish-playbook` 仓库；本仓不重复维护整段阶段正文。

**Adding a new skill / 新增 skill：** add `skills/<kebab-case-name>/SKILL.md` with the standard frontmatter and body, then update the README index + CHANGELOG. See the `github-publish-ops` skill for the exact recipe. **新增 skill：** 添加 `skills/<kebab-case-name>/SKILL.md`（标准 frontmatter + 正文），再更新 README 索引与 CHANGELOG。具体步骤见 `github-publish-ops` skill。

---

## 📚 Available skills / 现有 skills 索引

| Skill 技能 | What it does 作用 | When to invoke 触发场景 |
|---|---|---|
| [**github-publish-redact**](skills/github-publish-redact/SKILL.md) | Redact usernames/hostnames/UUIDs/passwords/IPs before public release 公开前脱敏与保密 | Preparing any repo/docs for public publish 准备公开任何仓库/文档时 |
| [**github-publish-compliance**](skills/github-publish-compliance/SKILL.md) | Generate LICENSE/THIRDPARTY/SECURITY/CONTRIBUTING/CHANGELOG/FUNDING 生成合规社区文件 | Creating a new public repo / adding project to OSS org 新建公共仓库时 |
| [**github-publish-readme**](skills/github-publish-readme/SKILL.md) | Write/translate bilingual EN→ZH README with disclaimer & capability table 撰写双语 README | Creating or translating a project README 新建或翻译 README 时 |
| [**github-publish-git-safe**](skills/github-publish-git-safe/SKILL.md) | Safe git init/stage/commit without leaking privates; filter-repo history rewrite 安全 git 提交 | First commit of a to-be-published repo, or history rewrite 首提交或历史重写时 |
| [**github-publish-push-scan**](skills/github-publish-push-scan/SKILL.md) | Create repo Private→push→verify→enable scanning→flip Public 建仓推送与安全扫描 | Publishing a finished repo to GitHub 发布成型仓库时 |
| [**github-publish-ops**](skills/github-publish-ops/SKILL.md) | Post-release ops + iteratively grow the skills collection 发布后运营与迭代 | Maintaining public repos or adding new skills 维护仓库/新增 skill 时 |

*AgenAI note: invoke by matching the "When to invoke" trigger.* / *给 AI agent：按「触发场景」匹配调用。*

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