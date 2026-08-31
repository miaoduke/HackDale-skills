#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gzh_format.py — Markdown 笔记 -> 公众号可直接粘贴的内联 HTML。

排版风格借鉴自开源 Skill: gzh-design-skill
  作者: 甲木 × 摸鱼小李  仓库: https://github.com/isjiamu/gzh-design-skill
  协议: AGPL-3.0（本文件仅“借鉴排版理念”，为独立最小实现，非其代码搬运）

借鉴的核心排版理念（在此以零依赖 stdlib 落地）：
  · 克制用色：主色仅锚点出现（章节编号/引言竖条/关键词标记），白底 + 灰阶承重
  · 灰阶承重：约 90% 文字用中性灰阶 #111827 -> #9CA3AF，色彩不承担正文阅读
  · 小标签：左竖条 / 药丸标签，不使用四周虚线框
  · 章节自动编号：H2 依次编号，末章标记 ∞
  · 引言卡 + 目录：首段自动转引言卡；>=2 个 H2 自动生成目录
  · 关键词标记：**加粗** -> 主色浅底下划线式高亮（每段克制使用）
  · 全内联样式：禁用 <style>/<script>/<div>/class/id/position/float/grid/外部字体
  · <span leaf=""> 包裹文字，规避公众号编辑器过滤；中文自动全角标点（代码原样）

用法：
  python gzh_format.py note.md --out note.gzh.html [--title "标题"] [--theme moyu-green]
  # 打开生成的 .gzh.html，点“复制到公众号”，粘贴进公众号编辑器即可。
"""
import argparse
import html as _html
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 主题色板（借鉴 gzh-design 的“变量角色”，此处内置 6 套主色，默认摸鱼绿）
# 每套：primary 主色 / dark 深主色 / light 浅底 / border 浅边框 / mark 关键词底
# 灰阶为全主题共用（灰阶承重）。
# ---------------------------------------------------------------------------
THEMES = {
    "moyu-green": {"name": "摸鱼绿", "primary": "#059669", "dark": "#047857",
                   "light": "#ECFDF5", "border": "#A7F3D0", "mark": "#D1FAE5"},
    "red-white":  {"name": "红白色系", "primary": "#DC2626", "dark": "#B91C1C",
                   "light": "#FEF2F2", "border": "#FECACA", "mark": "#FEE2E2"},
    "graphite":   {"name": "石墨极简", "primary": "#52525B", "dark": "#3F3F46",
                   "light": "#FAFAFA", "border": "#E4E4E7", "mark": "#F4F4F5"},
    "zen":        {"name": "留白禅意", "primary": "#4A5D52", "dark": "#3A4A41",
                   "light": "#F3F6F4", "border": "#CBD8D0", "mark": "#E4EDE8"},
    "ink-blue":   {"name": "墨蓝刊读", "primary": "#1D4ED8", "dark": "#1E40AF",
                   "light": "#EFF6FF", "border": "#BFDBFE", "mark": "#DBEAFE"},
    "olive":      {"name": "橄榄手记", "primary": "#4D7C0F", "dark": "#3F6212",
                   "light": "#F7FEE7", "border": "#D9F99D", "mark": "#ECFCCB"},
}
DEFAULT_THEME = "moyu-green"

# 灰阶（承重 90% 文字）
G_TITLE = "#111827"   # 标题
G_BODY = "#374151"    # 正文
G_MUTED = "#6B7280"   # 辅助
G_FAINT = "#9CA3AF"   # 最浅 / 目录序号
G_LINE = "#E5E7EB"    # 分割线
FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC',"
        "'Hiragino Sans GB','Microsoft YaHei',sans-serif")
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

_CN = "零一二三四五六七八九"


def cn_num(n: int) -> str:
    """1->一, 10->十, 11->十一, 21->二十一 ... 超过 99 退回数字。"""
    if n <= 0:
        return str(n)
    if n < 10:
        return _CN[n]
    if n == 10:
        return "十"
    if n < 20:
        return "十" + _CN[n % 10]
    if n < 100:
        t = _CN[n // 10] + "十"
        return t + (_CN[n % 10] if n % 10 else "")
    return str(n)


def _leaf(inner: str) -> str:
    """公众号防过滤：文字用 <span leaf=""> 包裹。"""
    return f'<span leaf="">{inner}</span>'


# ---------------------------------------------------------------------------
# 中文全角标点规范（代码/行内代码不处理）
# ---------------------------------------------------------------------------
_CJK = r"\u4e00-\u9fff\u3040-\u30ff\uff00-\uffef"
_PUNC_MAP = {",": "，", ";": "；", ":": "：", "!": "！", "?": "？",
             "(": "（", ")": "）"}


def _fullwidth_punct(text: str) -> str:
    """把与中文相邻的半角 , ; : ! ? ( ) 规范为全角。句点保守跳过（避免小数）。"""
    def repl(m):
        ch = m.group(0)
        return _PUNC_MAP.get(ch, ch)
    # 半角标点前或后是 CJK -> 全角
    pat = re.compile(r"(?<=[%s])\s?([,;:!?()])|([,;:!?()])\s?(?=[%s])"
                     % (_CJK, _CJK))

    def repl2(m):
        ch = m.group(1) or m.group(2)
        return _PUNC_MAP.get(ch, ch)
    return pat.sub(repl2, text)


# ---------------------------------------------------------------------------
# 行内解析：`code` **bold** *italic* [text](url) ![alt](src)
# ---------------------------------------------------------------------------
def _inline(text: str, th: dict, fullwidth: bool = True) -> str:
    # 先抽出行内代码，占位保护（不做全角/转义处理）
    codes = []

    def _stash(m):
        codes.append(m.group(1))
        return f"\x00C{len(codes) - 1}\x00"
    text = re.sub(r"`([^`]+)`", _stash, text)

    # 图片（行内）
    imgs = []

    def _stash_img(m):
        imgs.append((m.group(1), m.group(2)))
        return f"\x00I{len(imgs) - 1}\x00"
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _stash_img, text)

    if fullwidth:
        text = _fullwidth_punct(text)
    text = _html.escape(text, quote=False)

    # 链接 [text](url) -> 主色文字 + 浅色 url（公众号不保留外链，转纯文本）
    def _link(m):
        t, u = m.group(1), m.group(2)
        seg = (f'<span style="color:{th["dark"]};font-weight:600;">{t}</span>')
        if u and u not in t:
            seg += (f'<span style="color:{G_FAINT};font-size:13px;">'
                    f'（{u}）</span>')
        return seg
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)

    # **bold** -> 关键词标记（主色浅底 + 主色字，克制高亮）
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        lambda m: (f'<span style="background:{th["mark"]};color:{th["dark"]};'
                   f'font-weight:700;padding:0 3px;border-radius:3px;">'
                   f'{m.group(1)}</span>'),
        text)
    # *italic*
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",
                  lambda m: f'<em style="font-style:italic;">{m.group(1)}</em>',
                  text)

    # 还原图片占位
    def _unstash_img(m):
        alt, src = imgs[int(m.group(1))]
        return (f'</span><img src="{_html.escape(src, quote=True)}" '
                f'alt="{_html.escape(alt, quote=True)}" '
                f'style="max-width:100%;border-radius:8px;display:block;'
                f'margin:16px auto;"/><span leaf="">')
    text = re.sub(r"\x00I(\d+)\x00", _unstash_img, text)

    # 还原行内代码
    def _unstash(m):
        c = _html.escape(codes[int(m.group(1))], quote=False)
        return (f'<code style="font-family:{MONO};background:#F3F4F6;'
                f'color:#BE185D;padding:1px 5px;border-radius:4px;'
                f'font-size:14px;">{c}</code>')
    text = re.sub(r"\x00C(\d+)\x00", _unstash, text)
    return text


# ---------------------------------------------------------------------------
# 块级解析
# ---------------------------------------------------------------------------
def _split_blocks(md: str):
    """产出 (type, payload) 块序列。"""
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        ln = lines[i]
        s = ln.strip()
        # 代码块
        if s.startswith("```"):
            lang = s[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```
            blocks.append(("code", (lang, "\n".join(buf))))
            continue
        # 空行
        if not s:
            i += 1
            continue
        # 分割线
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            blocks.append(("hr", ""))
            i += 1
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            blocks.append(("h", (len(m.group(1)), m.group(2).strip())))
            i += 1
            continue
        # 引用（连续）
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            blocks.append(("quote", "\n".join(buf)))
            continue
        # 无序列表（连续）
        if re.match(r"^[-*+]\s+", s):
            buf = []
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                buf.append(re.sub(r"^\s*[-*+]\s+", "", lines[i]))
                i += 1
            blocks.append(("ul", buf))
            continue
        # 有序列表（连续）
        if re.match(r"^\d+\.\s+", s):
            buf = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                buf.append(re.sub(r"^\s*\d+\.\s+", "", lines[i]))
                i += 1
            blocks.append(("ol", buf))
            continue
        # 段落（连续非空非特殊行）
        buf = []
        while i < n and lines[i].strip() and \
                not re.match(r"^(#{1,6}\s|>|[-*+]\s|\d+\.\s|```|-{3,}$)",
                             lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        blocks.append(("p", " ".join(buf)))
    return blocks


# ---------------------------------------------------------------------------
# 渲染为公众号内联 HTML
# ---------------------------------------------------------------------------
def render(md: str, theme: str = DEFAULT_THEME, title: str = "") -> str:
    th = THEMES.get(theme, THEMES[DEFAULT_THEME])
    blocks = _split_blocks(md)

    # 提取标题：--title > 首个 H1 > 首行
    doc_title = title
    if not doc_title:
        for t, pl in blocks:
            if t == "h" and pl[0] == 1:
                doc_title = pl[1]
                break
    if not doc_title and blocks:
        doc_title = re.sub(r"[#>*`\-]", "", blocks[0][1] if
                           isinstance(blocks[0][1], str) else "").strip()[:40]
    doc_title = doc_title or "未命名笔记"

    # 统计 H2，用于章节自动编号 + 末章 ∞ + 目录
    h2_titles = [pl[1] for t, pl in blocks if t == "h" and pl[0] == 2]
    total_h2 = len(h2_titles)

    out = []
    # ---- 封面标题 ----
    out.append(
        f'<section style="margin:0 0 8px;">'
        f'<p style="font-size:24px;font-weight:800;color:{G_TITLE};'
        f'line-height:1.4;letter-spacing:.5px;margin:0;">'
        f'{_leaf(_inline(doc_title, th))}</p>'
        f'<p style="height:4px;width:44px;background:{th["primary"]};'
        f'border-radius:3px;margin:12px 0 0;">{_leaf("&nbsp;")}</p>'
        f'</section>')

    # ---- 引言卡（首个正文段自动转引言）----
    intro_used = False
    first_p_idx = next((k for k, (t, _) in enumerate(blocks)
                        if t == "p"), None)
    # 若首段在第一个 H2 之前，才做引言卡
    first_h_idx = next((k for k, (t, _) in enumerate(blocks) if t == "h"), None)
    if first_p_idx is not None and (first_h_idx is None or
                                    first_p_idx < first_h_idx or
                                    (first_h_idx is not None and
                                     blocks[first_h_idx][1][0] == 1)):
        intro_txt = blocks[first_p_idx][1]
        if len(intro_txt) >= 8:
            out.append(
                f'<section style="margin:20px 0;padding:14px 16px;'
                f'background:{th["light"]};border-left:4px solid '
                f'{th["primary"]};border-radius:0 8px 8px 0;">'
                f'<p style="margin:0;color:{G_BODY};font-size:15px;'
                f'line-height:1.8;">{_leaf(_inline(intro_txt, th))}</p>'
                f'</section>')
            intro_used = first_p_idx

    # ---- 目录（>=2 个 H2）----
    if total_h2 >= 2:
        items = []
        for k, ht in enumerate(h2_titles, 1):
            no = "∞" if k == total_h2 else f"{k:02d}"
            no_span = (f'<span style="color:{th["primary"]};font-weight:700;">'
                       f'{no}</span>&nbsp;&nbsp;{ht}')
            items.append(
                f'<p style="margin:6px 0;color:{G_BODY};font-size:15px;">'
                f'{_leaf(no_span)}</p>')
        out.append(
            f'<section style="margin:20px 0;padding:16px 18px;'
            f'background:#FAFAFA;border-radius:10px;">'
            f'<p style="margin:0 0 10px;font-size:13px;color:{G_FAINT};'
            f'letter-spacing:2px;">{_leaf("目 录")}</p>'
            + "".join(items) + '</section>')

    # ---- 正文块 ----
    h2_seen = 0
    for k, (t, pl) in enumerate(blocks):
        if intro_used is not False and k == intro_used:
            continue  # 已用作引言卡
        if t == "h":
            level, txt = pl
            if level == 1:
                continue  # 已作封面
            if level == 2:
                h2_seen += 1
                no = "∞" if h2_seen == total_h2 else cn_num(h2_seen)
                inner = (
                    f'<span style="display:inline-block;border-left:4px solid '
                    f'{th["primary"]};padding-left:10px;font-size:19px;'
                    f'font-weight:800;color:{G_TITLE};line-height:1.5;">'
                    f'<span style="color:{th["primary"]};">{no}、</span>'
                    f'{txt}</span>')
                out.append(
                    f'<section style="margin:32px 0 14px;">'
                    f'<p style="margin:0;display:block;">{_leaf(inner)}'
                    f'</p></section>')
            else:
                # H3+：药丸小标签
                pill = (
                    f'<span style="display:inline-block;background:'
                    f'{th["light"]};color:{th["dark"]};font-size:15px;'
                    f'font-weight:700;padding:3px 12px;border-radius:999px;">'
                    f'{txt}</span>')
                out.append(
                    f'<section style="margin:22px 0 10px;">'
                    f'<p style="margin:0;">{_leaf(pill)}</p></section>')
        elif t == "p":
            out.append(
                f'<p style="margin:14px 0;color:{G_BODY};font-size:16px;'
                f'line-height:1.9;letter-spacing:.3px;">'
                f'{_leaf(_inline(pl, th))}</p>')
        elif t == "ul":
            lis = []
            bullet = (f'<span style="color:{th["primary"]};font-weight:800;">'
                      f'·&nbsp;&nbsp;</span>')
            for it in pl:
                lis.append(
                    f'<p style="margin:8px 0;padding-left:20px;color:{G_BODY};'
                    f'font-size:16px;line-height:1.85;">'
                    f'{_leaf(bullet + _inline(it, th))}</p>')
            out.append('<section style="margin:12px 0;">' + "".join(lis) +
                       '</section>')
        elif t == "ol":
            lis = []
            for idx, it in enumerate(pl, 1):
                marker = (f'<span style="color:{th["primary"]};'
                          f'font-weight:800;">{idx}.&nbsp;&nbsp;</span>')
                lis.append(
                    f'<p style="margin:8px 0;padding-left:24px;color:{G_BODY};'
                    f'font-size:16px;line-height:1.85;">'
                    f'{_leaf(marker + _inline(it, th))}</p>')
            out.append('<section style="margin:12px 0;">' + "".join(lis) +
                       '</section>')
        elif t == "quote":
            out.append(
                f'<section style="margin:18px 0;padding:14px 16px;'
                f'background:{th["light"]};border-left:4px solid '
                f'{th["border"]};border-radius:0 8px 8px 0;">'
                f'<p style="margin:0;color:{G_MUTED};font-size:15px;'
                f'line-height:1.8;font-style:italic;">'
                f'{_leaf(_inline(pl, th))}</p></section>')
        elif t == "code":
            lang, code = pl
            esc = _html.escape(code, quote=False).replace("\n", "<br/>")
            esc = esc.replace(" ", "&nbsp;")
            out.append(
                f'<section style="margin:18px 0;padding:16px;'
                f'background:#0F172A;border-radius:10px;overflow-x:auto;">'
                f'<p style="margin:0;font-family:{MONO};font-size:13px;'
                f'line-height:1.7;color:#E2E8F0;white-space:nowrap;">'
                f'{_leaf(esc)}</p></section>')
        elif t == "hr":
            out.append(
                f'<section style="margin:26px 0;text-align:center;">'
                f'<p style="margin:0;color:{th["border"]};font-size:14px;'
                f'letter-spacing:6px;">{_leaf("· · ·")}</p></section>')

    # ---- 结尾署名条（借鉴：署名去重合并 + 收束）----
    out.append(
        f'<section style="margin:30px 0 6px;padding-top:16px;'
        f'border-top:1px solid {G_LINE};">'
        f'<p style="margin:0;color:{G_FAINT};font-size:13px;line-height:1.7;">'
        f'{_leaf("—— 本文由笔记自动排版生成 · 排版风格借鉴 gzh-design-skill")}'
        f'</p></section>')

    article = "".join(out)
    # 公众号正文容器（section，非 div）
    gzh_body = (
        f'<section style="font-family:{FONT};max-width:100%;'
        f'color:{G_BODY};font-size:16px;line-height:1.9;'
        f'padding:0 2px;">{article}</section>')

    return _wrap_preview(gzh_body, doc_title, th)


def _wrap_preview(gzh_body: str, title: str, th: dict) -> str:
    """外层预览页（可用 style/div/button，仅供浏览与复制，不粘贴此部分）。"""
    safe_title = _html.escape(title, quote=True)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{safe_title} · 公众号排版预览</title>
<style>
  body{{margin:0;background:#F3F4F6;font-family:{FONT};}}
  .bar{{position:sticky;top:0;z-index:10;background:#fff;
        border-bottom:1px solid #E5E7EB;padding:12px 16px;display:flex;
        align-items:center;gap:12px;justify-content:space-between;}}
  .bar b{{color:#111827;font-size:15px;}}
  .bar .theme{{color:#6B7280;font-size:13px;}}
  .btn{{background:{th['primary']};color:#fff;border:none;border-radius:8px;
        padding:9px 18px;font-size:14px;font-weight:600;cursor:pointer;}}
  .btn:active{{transform:translateY(1px);}}
  .wrap{{max-width:680px;margin:20px auto;background:#fff;border-radius:12px;
         box-shadow:0 1px 3px rgba(0,0,0,.08);padding:28px 22px;}}
  .tip{{max-width:680px;margin:8px auto 0;color:#9CA3AF;font-size:12px;
        padding:0 6px;}}
</style>
</head>
<body>
  <div class="bar">
    <b>公众号排版预览 · {th['name']}</b>
    <button class="btn" onclick="copyGzh()">复制到公众号</button>
  </div>
  <div class="tip">提示：点“复制到公众号”，直接粘贴进公众号编辑器即可；样式已全部内联。</div>
  <div class="wrap" id="gzh-content">{gzh_body}</div>
<script>
function copyGzh(){{
  var node=document.getElementById('gzh-content');
  var range=document.createRange();range.selectNodeContents(node);
  var sel=window.getSelection();sel.removeAllRanges();sel.addRange(range);
  try{{document.execCommand('copy');alert('已复制！去公众号编辑器粘贴即可。');}}
  catch(e){{alert('复制失败，请手动全选正文区域复制。');}}
  sel.removeAllRanges();
}}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# 禁用标签 / 合规自检（借鉴产物关校验思路，最小版）
# ---------------------------------------------------------------------------
_FORBIDDEN = [r"<div\b", r"<style\b(?![^>]*preview)", r"\sclass=", r"\sid=",
              r"position\s*:\s*(fixed|absolute|sticky)", r"display\s*:\s*grid",
              r"float\s*:", r"@media", r"@keyframes"]


def lint_gzh_body(gzh_body: str) -> list:
    """只检查公众号正文片段（不含预览外壳）。返回问题列表。"""
    issues = []
    for pat in _FORBIDDEN:
        if re.search(pat, gzh_body):
            issues.append(f"命中禁用模式: {pat}")
    # 文字应被 <span leaf> 包裹（抽样）
    if "<span leaf" not in gzh_body:
        issues.append("缺少 <span leaf> 文字包裹")
    return issues


def extract_body(full_html: str) -> str:
    m = re.search(r'<div class="wrap" id="gzh-content">(.*)</div>\s*<script>',
                  full_html, re.S)
    return m.group(1) if m else ""


def convert_file(src: str, out: str = "", theme: str = DEFAULT_THEME,
                 title: str = "") -> str:
    md = Path(src).read_text(encoding="utf-8")
    full = render(md, theme=theme, title=title)
    dst = out or str(Path(src).with_suffix(".gzh.html"))
    Path(dst).write_text(full, encoding="utf-8")
    return dst


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Markdown 笔记 -> 公众号内联 HTML（排版借鉴 gzh-design-skill）")
    ap.add_argument("input", help="输入 note.md 路径")
    ap.add_argument("--out", default="", help="输出 .html（默认同名 .gzh.html）")
    ap.add_argument("--title", default="", help="覆盖标题（默认取首个 H1）")
    ap.add_argument("--theme", default=DEFAULT_THEME,
                    choices=list(THEMES.keys()),
                    help="主题（默认 moyu-green 摸鱼绿）")
    ap.add_argument("--lint", action="store_true", help="仅做合规自检不输出")
    args = ap.parse_args(argv)

    md = Path(args.input).read_text(encoding="utf-8")
    full = render(md, theme=args.theme, title=args.title)
    body = extract_body(full)
    issues = lint_gzh_body(body)

    if args.lint:
        if issues:
            print("合规自检 FAIL:")
            for it in issues:
                print("  -", it)
            sys.exit(1)
        print("合规自检 OK：无禁用标签，文字已 <span leaf> 包裹。")
        return

    dst = args.out or str(Path(args.input).with_suffix(".gzh.html"))
    Path(dst).write_text(full, encoding="utf-8")
    print(f"[gzh] 公众号排版已生成 -> {dst}")
    print(f"[gzh] 主题={THEMES[args.theme]['name']}  "
          f"合规自检={'OK' if not issues else 'WARN:' + ';'.join(issues)}")


if __name__ == "__main__":
    main()
