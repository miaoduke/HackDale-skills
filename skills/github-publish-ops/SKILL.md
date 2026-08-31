---
name: "github-publish-ops"
description: "Post-publication operations and iterative skill evolution: sponsor/FUNDING, releases, keeping repos separate, absorbing new lessons back into skills. Invoke when maintaining public repos or when a new skill/repo should be added to the skills collection."
---

# GitHub 发布 · 发布后运营与迭代 / Post-release Ops & Evolution

> **Purpose:** Keep public repos healthy after release, and keep this skills collection growing as you learn new lessons.
> **用途：** 发布后维持公共仓库健康，并在持续学习新经验的同时让本 skills 集不断生长。

## When to use / 何时使用
Invoke when maintaining an already-published repo, or when adding a **new skill** to this collection, or when a new lesson should be absorbed back into a skill.

## Post-release maintenance / 发布后运营
- **Keep one repo per project** — never jumble multiple projects into one repo. For a skills collection, structure is `skills/<skill-name>/SKILL.md` per skill.
- **Testing restores the env**: after any on-machine test, restore the original environment/config.
- **Donation / Sponsor**: keep署名 and收款码 consistent across repos (via `.github/FUNDING.yml` + README QR). Fundraising QR is displayed directly; donations must not alter the free MIT license.
- **Releases**: tag meaningful milestones so consumers can pin versions.
- **Registration & roll-back**: retracted conclusions kept & annotated, never silently deleted.

## Adding a new skill to this collection / 新增 skill 到本集
Each new capability becomes `skills/<kebab-case-name>/SKILL.md` with frontmatter:
- `name`: kebab-case unique id.
- `description`: `<does X>. Invoke when <scenario Y or user asks Z>.` (keep < 200 chars; bilingual-friendly).
- Body: Purpose → When to use → Execution steps → Checks → Source (deep-dive pointer to the original playbook repo).

Then **update the README index** so AI can discover it, and bump `CHANGELOG.md`.

## Evolution loop / 迭代升级闭环
When you hit a new gremlin or a new technique during any real publish:
1. Update the per-stage SOP in the `github-publish-playbook` source repo.
2. Mirror the insight into the relevant `SKILL.md` here.
3. Add the gremlin to the lessons log.
4. Update this repo's README capability table + CHANGELOG.
Keep the source playbook and the skills in sync — they are two views of the same knowledge.

## Checks / 检查点
- [ ] Each repo is standalone (no multi-project jumble).
- [ ] New skills added under `skills/<name>/SKILL.md` and indexed in README.
- [ ] Lessons learned mirrored back to `github-publish-playbook` and here.
- [ ] Testing restored the original environment.
- [ ] Signature & donation QR consistent; MIT unchanged.

## Source / 深挖参考
`github-publish-playbook` repo → `SOP/07_发布后运营与GitHub配置.md` + `lessons/经验教训与反模式.md`.