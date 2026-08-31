#!/usr/bin/env python3
"""lint_skill.py — bilinote-skill 结构自检（Plan F 工程地基）。

借鉴 jnMetaCode/agency-agents-zh 的 lint 纪律，校验本技能的文档与代码是否一致，
防止后续改动"改漏"。检查项：
  1. 关键文件存在（SKILL.md / bilinote.py / gzh_format.py / references/*.md）
  2. SKILL.md 必备章节齐全
  3. E1–E8 扩展章节齐全
  4. STYLES 字典键与 SKILL.md 风格清单一致
  5. style_prompts.md 的 ## 段与平台风格键一致
  6. gzh 主题键与 SKILL.md 描述一致
  7. 子命令在 SKILL.md 命令速查中有登记

退出码：0 = 全通过；1 = 存在错误（ERROR）；警告（WARN）不影响退出码。
用法：python scripts/lint_skill.py [--strict]
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"
BILINOTE = SKILL_DIR / "scripts" / "bilinote.py"
GZH = SKILL_DIR / "scripts" / "gzh_format.py"
STYLE_PROMPTS = SKILL_DIR / "references" / "style_prompts.md"

ERRORS: list[str] = []
WARNS: list[str] = []


def err(msg: str) -> None:
    ERRORS.append(msg)


def warn(msg: str) -> None:
    WARNS.append(msg)


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except Exception as e:
        err(f"无法读取 {p.name}: {e}")
        return ""


def check_files() -> None:
    for p in (SKILL_MD, BILINOTE, GZH, STYLE_PROMPTS):
        if not p.exists():
            err(f"缺失关键文件：{p.relative_to(SKILL_DIR)}")


def check_sections(skill: str) -> None:
    required = ["集成扩展能力", "failure modes", "CHECKPOINT", "风格"]
    for s in required:
        if s not in skill:
            warn(f"SKILL.md 未找到疑似必备章节关键字：「{s}」")


def check_extensions(skill: str) -> None:
    for i in range(1, 9):
        if not re.search(rf"\bE{i}\b", skill):
            err(f"SKILL.md 缺少扩展 E{i} 的说明")


def parse_styles(code: str) -> list[str]:
    """从 bilinote.py 提取 STYLES 字典的键。"""
    m = re.search(r"STYLES\s*=\s*\{(.*?)\n\}", code, re.S)
    if not m:
        err("bilinote.py 未找到 STYLES 字典")
        return []
    body = m.group(1)
    return re.findall(r'"([a-z0-9_-]+)"\s*:', body)


def check_styles(skill: str, code: str) -> list[str]:
    keys = parse_styles(code)
    if not keys:
        return []
    for k in keys:
        if k not in skill:
            warn(f"风格 `{k}` 在 STYLES 中定义，但 SKILL.md 未提及")
    return keys


def check_style_prompts(sp: str, code: str = "") -> None:
    segs = set(re.findall(r"^##\s+([a-z0-9_-]+)\s*$", sp, re.M))
    # Plan D 起要求全部 STYLES 键都配有详细补丁段；无法解析 STYLES 时回退到 3 平台段。
    expected = set(parse_styles(code)) if code else {"xiaohongshu", "wechat", "bilibili"}
    missing = expected - segs
    if missing:
        err(f"style_prompts.md 缺少风格详细规范段：{sorted(missing)}")
    extra = segs - expected
    if extra:
        warn(f"style_prompts.md 存在未在 STYLES 中定义的段：{sorted(extra)}")


def parse_gzh_themes(gzh: str) -> list[str]:
    m = re.search(r"THEMES\s*(?::[^=]*)?=\s*\{(.*?)\n\}", gzh, re.S)
    if not m:
        warn("gzh_format.py 未找到 THEMES 字典")
        return []
    # 仅取顶层主题键（值为字典 `{` 者），忽略嵌套的 name/primary/... 等字段。
    return re.findall(r'"([a-z-]+)"\s*:\s*\{', m.group(1))


def check_gzh_themes(skill: str, gzh: str) -> None:
    themes = parse_gzh_themes(gzh)
    for t in themes:
        if t not in skill:
            warn(f"gzh 主题 `{t}` 未在 SKILL.md 说明")


def parse_subcommands(code: str) -> list[str]:
    return sorted(set(re.findall(r'\.add_parser\(\s*"([a-z-]+)"', code)))


def check_subcommands(skill: str, code: str) -> None:
    subs = parse_subcommands(code)
    for s in subs:
        if s not in skill:
            warn(f"子命令 `{s}` 未在 SKILL.md 中登记（命令速查/说明）")


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    strict = "--strict" in argv

    check_files()
    skill = _read(SKILL_MD)
    code = _read(BILINOTE)
    gzh = _read(GZH)
    sp = _read(STYLE_PROMPTS)

    if skill:
        check_sections(skill)
        check_extensions(skill)
    if skill and code:
        keys = check_styles(skill, code)
        check_subcommands(skill, code)
        print(f"  STYLES: {len(keys)} 种 -> {', '.join(keys)}")
        print(f"  子命令: {', '.join(parse_subcommands(code))}")
    if sp:
        check_style_prompts(sp, code)
        segs = re.findall(r"^##\s+([a-z0-9_-]+)\s*$", sp, re.M)
        print(f"  风格补丁段: {len(segs)} 个 -> {', '.join(segs)}")
    if skill and gzh:
        check_gzh_themes(skill, gzh)
        print(f"  gzh 主题: {', '.join(parse_gzh_themes(gzh))}")

    print()
    for w in WARNS:
        print(f"[WARN] {w}")
    for e in ERRORS:
        print(f"[ERROR] {e}")

    print()
    if ERRORS:
        print(f"lint 失败：{len(ERRORS)} 个错误，{len(WARNS)} 个警告。")
        return 1
    if strict and WARNS:
        print(f"lint 严格模式失败：{len(WARNS)} 个警告。")
        return 1
    print(f"lint 通过：0 错误，{len(WARNS)} 个警告。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
