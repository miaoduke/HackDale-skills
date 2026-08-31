---
name: "github-publish-git-safe"
description: "Safely inits a repo, stages, and commits public content without leaking private files or secrets into history. Invoke before the first commit of any repo that will be published, or when a history rewrite with git-filter-repo is needed."
---

# GitHub 发布 · 本地 git 安全初始化与提交 / Safe Git Init & Commit

> **Purpose:** Make the first commit contain ONLY the public layer — never `_private`, never credentials, never binaries. If a secret already slipped into history, rewrite it before it goes public.
> **用途：** 让首次提交只包含公开层——绝不带 `_private`、凭据、二进制。若秘密已进入历史，公开前必须重写。

## When to use / 何时使用
Invoke at the first commit of any repo to be published, or anytime you must `filter-repo` a leaked secret, or verify `git check-ignore`.

## Execution steps / 执行步骤
1. **`.gitignore` first** — exclude `_private_不上传/`, `*.key`, `*.pem`, `node_modules/`, local captures. Never `git add -A` blindly.
2. **Stage file-by-file** (or explicit paths), then review `git diff --cached` before committing:
   ```bash
   git add README.md LICENSE .github/ skills/
   git status                       # review
   git diff --cached --stat         # confirm only intended files
   ```
3. **Verify ignore** (PowerShell-safe, avoids PS5.1 UTF-8/BOM bugs in scripts):
   ```bash
   git check-ignore _private_不上传/xyz.json   # each private file must list
   ```
   (Note: a `.ps1` auto-check script may mis-parse UTF-8-no-BOM as GBK on PS5.1 → use file-by-file `check-ignore`.)
4. **Commit with a clear conventional message**; do not skip hooks (`-n` is forbidden); create NEW commits, never amend a shared one.
5. **History rewrite** when a secret already committed → **backup first**:
   ```bash
   git bundle create backup_<date>.bundle --all
   git filter-repo --replace-text <mapping.txt>   # <USER>, <DATA_PART_UUID>, <REDACTED_PASSWORD>
   git filter-repo --invert-paths --path <secret-binary>
   ```
   This rewrites all commit hashes → force-push the rewritten branch, and keep the backup bundle out of the public repo.

## Checks / 检查点
- [ ] `git status` shows only intended files staged; no `_private`.
- [ ] `git check-ignore` on every private path → all ignored.
- [ ] `git grep` for real secrets → 0 hits in staged content.
- [ ] If history rewritten: backup bundle exists; pushed with force; all hashes changed.

## Source / 深挖参考
`github-publish-playbook` repo → `SOP/05_本地git初始化与安全提交.md` + `lessons` (G2 PowerShell stderr, G5 memory / UTF-8).