---
name: "github-publish-readme"
description: "Writes a polished bilingual (English+Chinese) README for a public repo with disclaimer, capability table, thing-to-know, known-issues, redaction note. Invoke when creating or translating the README of any public project."
---

# GitHub 发布 · README 文档工程 / README Engineering

> **Purpose:** The README is the front door of a public repo. Produce a complete **bilingual (EN then ZH)** README that states the disclaimer up front and makes known-issues explicit.
> **用途：** README 是公共仓库的门面。生成一份**先英文、后中文**的完整双语 README，把免责声明放在最前，并把已知问题讲清楚。

## When to use / 何时使用
Invoke when creating a fresh README, or when asked to **translate an existing README into Chinese-English bilingual**. Also when updating a repo after structure changes.

## Structure / 结构（每节先英文、后中文）
1. **Title** bilingual (e.g. `# 项目名 (Model) — 功能 · 说明` / `# Project (Model) — Feature · Desc`).
2. **Disclaimer / 免责声明** at the very top: unofficial, not affiliated/endorsed by any vendor, use-at-your-own-risk. (intentional duplication = safe for skimming users)
3. **Quick Navigation / 快速导航** — one-line links to the important sections.
4. **Directory Tree / 目录结构** — accurate file counts; names that lie must be flagged (e.g. a "latest" folder that is actually older).
5. **Capability Table (dual-OS comparison) / 双系统能力对比** — e.g. 12 features × Windows/Linux availability, so readers know what runs where.
6. **Known Issues / 已知问题** — GitHub-native `- [ ]` checkboxes with status icons (🟥待修/🟨观察/🟩已解决).
7. **Unpublished Content / 未公开内容** — what is intentionally excluded (OEM binaries, decompiled artifacts, credentials, personal machine data, runtime logs).
8. **About Redaction / 关于脱敏** — what was replaced and why; how to restore placeholders (`<USER>`, `<WIN_C_UUID>`, `<REDACTED_PWD_SALT>`).
9. **Footer sections**: 贡献 · 安全 · 更新 · 许可 (Contributions · Security · Changelog · License), with donation/QR if requested.

## Key rules / 关键规则
- **Bilingual discipline**: each section = English first, then Chinese. Technical terms, register addresses, file names, URLs stay in **original form in both languages**.
- **Every claim must be verifiable**: file counts match `git ls-files`; capability table is real, not aspirational.
- **目录名会骗人**: a "newer-named" folder may hold an older baseline — audit and annotate the mismatch.
- Keep placeholders `<NAME>` identical across both languages so a reader can search once.

## Checks / 检查点
- [ ] Disclaimer is present and near the top.
- [ ] Every main section appears in EN then ZH.
- [ ] File counts verified against `git ls-files`.
- [ ] Known-issues uses `- [ ]` + status icons.
- [ ] Redaction placeholders identical in both languages.

## Source / 深挖参考
`github-publish-playbook` repo → `SOP/04_README与文档工程.md`; see `github-publish-redact` for placeholder conventions.