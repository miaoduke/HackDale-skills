---
name: "github-publish-push-scan"
description: "Creates the GitHub repo (Private first), pushes, verifies the remote, then enables Secret Scanning / Push Protection / Dependabot and flips to Public. Invoke when publishing a completed repo to GitHub."
---

# GitHub 发布 · 建仓推送与安全扫描 / Create, Push & Secure

> **Purpose:** Publish a repo to GitHub safely: create it **Private**, push, verify the remote matches, enable secrets scanning, and only then flip **Public**.
> **用途：** 安全地把仓库发布到 GitHub：先建 **Private**、推送、核对远端一致、开启秘密扫描，最后才转 **Public**。

## When to use / 何时使用
Invoke when pushing a final repo to GitHub for the first time, or when enabling security features on an existing public repo.

## Execution steps / 执行步骤
1. **Create the repo Private** (never public-first):
   ```bash
   gh repo create miaoduke/<repo> --private --source . --push
   ```
2. **Push & verify** the remote sha equals local (PowerShell may misreport git progress on stderr as an error — confirm with `ls-remote`):
   ```bash
   git push origin main
   git ls-remote origin main      # = local HEAD sha → OK
   ```
3. **Final self-check** before public: re-run sensitive scan + `check-ignore` + confirm working tree clean.
4. **Enable security features** on the (public or private-with-advanced) repo:
   ```bash
   gh api -X PATCH repos/OWNER/REPO \
     -f "security_and_analysis[secret_scanning][status]=enabled" \
     -f "security_and_analysis[secret_scanning_push_protection][status]=enabled" \
     -f "security_and_analysis[dependabot_security_updates][status]=enabled"
   ```
   > Secret Scanning & Push Protection engage fully on **public** repos / Private with Advanced Security.
5. **Flip Public** only after final self-check passes:
   ```bash
   gh repo edit OWNER/REPO --visibility public --accept-visibility-change-consequences
   ```
6. **Verify visibility** via API (`private: false`, correct URL).

## Notes on CodeQL / CodeQL 说明
Only meaningful for repos with real analyzable code (Python/Java/JS/...). For pure-doc / template / text repos, skip CodeQL — it produces no useful alerts. (Note: GitHub may mislabel Chinese-heavy markdown as "Wolfram Language"; this is text, not code.)

## Checks / 检查点
- [ ] Repo created Private, pushed successfully.
- [ ] `ls-remote` sha == local HEAD.
- [ ] Final self-check passed before flipping public.
- [ ] Secret Scanning + Push Protection + Dependabot = enabled.
- [ ] Public confirmed via API (`private:false`).

## Source / 深挖参考
`github-publish-playbook` repo → `SOP/06_建仓推送与安全扫描.md` + `lessons` (G2 stderr).