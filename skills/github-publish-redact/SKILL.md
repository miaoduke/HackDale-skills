---
name: "github-publish-redact"
description: "Redacts personal identifiers before any public GitHub publish. Invoke when preparing a repo/docs for public release and you must strip usernames, hostnames, UUIDs, passwords, IPs before committing."
---

# GitHub 发布 · 脱敏与保密 / Publish Redaction & Secrecy

> **Purpose:** Before anything goes public on GitHub, strip every value that could identify a specific device, person, or network. This is the **GATE 1** of the release playbook.
> **用途：** 任何内容公开到 GitHub 前，先清除所有能识别具体设备/个人/网络的真实值。这是发布流程的 **GATE 1**。

## When to use / 何时使用
Invoke this skill **before the first git add** of any public-facing file, and again right before pushing public repos. Trigger when preparing docs, code, or configs for public release.
在首次 `git add` 公开文件前、以及推送公共仓库前调用本技能；当准备把文档/代码/配置公开时触发。

## What to redact / 需要脱敏的值
Replace every real value with an obvious placeholder (keep the placeholder identical across both languages):

| Real value 真实值 | Placeholder 占位符 |
|---|---|
| Windows username (`C:\Users\d6150`) | `<USER>` |
| Linux/macOS username | `<USER>` |
| hostname (`hackdale-Aspire-A615-51G`) | `<HOSTNAME>` |
| Windows C-drive partition UUID (`DE063C...`) | `<WIN_C_UUID>` |
| data-disk partition UUID | `<DATA_PART_UUID>` |
| plaintext passwords (even pure-numeric like `334475`) | `<REDACTED_PASSWORD>` |
| password/salt/AES-key sentinels in code | `<REDACTED_PWD_SALT>` |
| IP addresses, MAC addresses | `<IP>` / `<MAC>` |
| email addresses | `<EMAIL>` |
| cloud keys (AKIA/personal tokens) | `<KEY>` / `<TOKEN>` |

## Execution steps / 执行步骤
1. **Full-tree scan**: grep the whole tree for real identifiers before writing anything:
   ```bash
   git grep -nE "<USER>|<HOSTNAME>|<WIN_C_UUID>|<REDACTED_PASSWORD>|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|BEGIN (RSA|EC|OPENSSH) PRIVATE KEY|192\.168\.|10\.\d+\.\d+\.\d+"
   ```
2. **Manual review of pure-numeric passwords**: GitHub's auto Secret Scanning **misses pure-numeric passwords**, so you must hunt them by hand or with a targeted grep over history.
3. **Redact in source, then re-commit** — never just edit the tip; if the secret is already in git history, history rewrite is required (see `github-publish-git-safe`).
4. **Register the redaction policy**: record what was replaced (and why) in the README "About Redaction / 关于脱敏" section.
5. **Note reverse-engineering contexts**: a register flagged as a writable flag-bit (e.g. `0x7A6`), NOT a live sensor, must be documented so it isn't misread.

## Checks / 检查点（GATE 1 必须全过）
- [ ] `git grep` for the real identifiers above returns **0 real hits** (only placeholders, no `AAAATT` real values).
- [ ] Every `C:\Users\<real>` replaced with `C:\Users\<USER>`.
- [ ] Redaction policy documented in README.
- [ ] No device-identifying hostname/UUID/MAC/email left in any tracked file.

## Source / 深挖参考
Full playbook: `github-publish-playbook` repo → `SOP/01_脱敏与保密.md` + `lessons/经验教训与反模式.md` (gremlins G1 pure-numeric password, G4).