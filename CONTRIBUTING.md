# 贡献指南 / Contributing

感谢你愿意为本 skills 集合迭代。请遵守以下规则：

## 规则 / Rules
- **禁止提交私有/逆向原文**：本仓库只收录**原创方法论与可复用指令**。严禁提交 OEM 二进制、反编译产物、固件衍生文件、他人私有代码、凭据或个人机器数据（见 THIRDPARTY.md）。
- **脱敏先行**：任何示例中的真实用户名、主机名、UUID、口令、IP、MAC 都必须替换为占位符（`<USER>`、`<HOSTNAME>`、`<WIN_C_UUID>`、`<REDACTED_PWD_SALT>` 等），并在提交前用 `git grep` 自检。
- **标准结构**：新增 skill 用 `skills/<kebab-case-name>/SKILL.md`，frontmatter 含 `name` + `description`（含触发场景，<200 字符），正文含 Purpose→When to use→Execution steps→Checks→Source。
- **更新索引**：新增/修改 skill 后，同步更新 `README.md` 的 skills 索引表与 `CHANGELOG.md`。
- **文件环境**：若本机做过任何测试，结束后恢复原始环境/配置。

## 提交约定 / Commit convention
- 使用清晰的中英双语提交信息（如 `docs: add skill github-publish-xxx`）。
- 不跳过 hooks，不 amend 已共享的提交；新内容走新提交。

## English / 英文本纲
Add skills as `skills/<name>/SKILL.md` (public-layer methodology only; redact all real identifiers; update `README.md` index + `CHANGELOG.md`). See `skills/github-publish-ops/SKILL.md` for the full recipe.