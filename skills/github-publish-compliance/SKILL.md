---
name: "github-publish-compliance"
description: "Generates the compliance + community file set for a public GitHub repo (LICENSE, THIRDPARTY, SECURITY, CONTRIBUTING, CHANGELOG, FUNDING, .gitignore). Invoke when creating a new public repo or adding a project to an existing open-source org."
---

# GitHub 发布 · 社区文件与合规 / Community & Compliance Files

> **Purpose:** Produce the standard file set every public repo needs, plus the reverse-engineering compliance extras. This is **GATE 2**'s companion — verify nothing non-redistributable is shipped.
> **用途：** 生成公共仓库必备的标准文件集，以及逆向工程的合规补充。这是 GATE 2 的配套——核对不随带任何不可再分发的二进制。

## When to use / 何时使用
Invoke when creating a new public repo, or when a project is first prepared for open-source release. Needed for every repo in a skills/experience collection.

## File set / 文件集
| File 文件 | Purpose 用途 |
|---|---|
| `LICENSE` | MIT recommended; neutral copyright holder (e.g. `<Name> Optimization Contributors`) or keep the original author's signature per user instruction. |
| `THIRDPARTY.md` | Declare any third-party binary/lib with its upstream, license, usage, and a dated note. **Never ship non-redistributable binaries** (state "obtain from upstream"). |
| `.github/SECURITY.md` | Vulnerabilities → private channel; `CONTRIBUTING` forbids submitting private/reverse-engineered source; keep direct-safe reporting path. |
| `CONTRIBUTING.md` | Contribution rules; **explicitly prohibit** submitting private/reverse-engineered original content; file counts / coverage notes accurate. |
| `CHANGELOG.md` | Versioned change log; keep in sync with README version headers. |
| `README.md` | See `github-publish-readme` skill. |
| `templates/` | Reusable compliance templates (LICENSE/THIRDPARTY/.../.gitignore). |
| `.github/FUNDING.yml` | Sponsor/donation link + target; keeps署名/donation (if user requests) consistent across repos. |

## Reverse-engineering compliance / 逆向合规要点
- Keep the **免责声明 (disclaimer)**: unofficial, not affiliated/endorsed by any vendor, use-at-your-own-risk.
- Distinguish **public layer** (conclusions, register maps, methodology, self-authored code) from **private layer** (raw captures, OEM binaries, credentials) — ship only the public layer.
- Third-party reverse-engineered binaries (e.g. WinRing0, ryzenadj, inpoutx64) must be declared, and **not redistributed**; point to upstream instead.
- Distinguish "retracted conclusions kept & annotated" from real errors.

## Checks / 检查点
- [ ] All files above exist and are non-empty.
- [ ] `THIRDPARTY.md` has dates + upstream links; non-redistributable binaries are NOT in the repo (only upstream pointers).
- [ ] `CONTRIBUTING.md` bans private/reverse-engineered submissions.
- [ ] LICENSE signature matches user request (original author or neutral).

## Source / 深挖参考
`github-publish-playbook` repo → `templates/` (7 ready files) + `SOP/03_社区文件与合规文档.md`.