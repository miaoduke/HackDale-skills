#!/usr/bin/env python3
"""E9 · 零依赖社媒卡生成器（bilinote v3.0 迭代 1）

把 note.md 变成可直接发小红书 / 公众号的图文卡：
  · 小红书 3:4 竖版图文卡组（封面 + 每节一张，5–9 张）
  · 公众号 21:9 主封面 + 1:1 方封面

设计原则：
  · 零 API Key、零外部依赖（纯 Python 标准库 + 自包含 HTML/CSS）
  · 不依赖 html-anything 安装即可用；若 html-anything 已就绪，可后续在其内打开微调
  · 可选 PNG：探测到 playwright / wkhtmltoimage / weasyprint 时自动栅格化，否则留 HTML

用法：
  python social-card.py --note note.md [--out <dir>] [--platforms xiaohongshu,wechat] [--png]
  python bilinote.py social-card --note note.md --png
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

CJK_FONT = (
    '-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", '
    '"Noto Sans CJK SC", "Source Han Sans SC", "Hiragino Sans GB", sans-serif'
)

# 平台调色板（克制、可读优先）
PALETTES = {
    "xiaohongshu": {"bg": "#ffffff", "accent": "#ff2e4d", "ink": "#1a1a1a", "sub": "#8a8a8a"},
    "wechat": {"bg": "#0b1f3a", "accent": "#ffd24a", "ink": "#ffffff", "sub": "#b9c6da"},
}


def parse_note(path: str) -> tuple[str, list[dict], str]:
    """返回 (标题, 小节列表[{h, bullets:[...]}], 导语)。"""
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    title = "笔记"
    for ln in lines:
        m = re.match(r"^#\s+(.+)$", ln)
        if m:
            title = m.group(1).strip()
            break
    sections: list[dict] = []
    cur: dict | None = None
    intro_parts: list[str] = []
    in_intro = True
    for ln in lines:
        h = re.match(r"^#{2,3}\s+(.+)$", ln)
        if h:
            in_intro = False
            if cur:
                sections.append(cur)
            cur = {"h": re.sub(r"^\s*[\d.、]+\s*", "", h.group(1)).strip(), "bullets": []}
        elif m := re.match(r"^\s*(?:[-*]|\d+[.、])\s+(.+)$", ln):
            b = m.group(1).strip()
            if not b:
                continue
            if in_intro and len(intro_parts) < 3 and not b.startswith("#"):
                intro_parts.append(b)
            elif cur:
                if len(cur["bullets"]) < 6:
                    cur["bullets"].append(b)
        elif in_intro and ln.strip() and len(intro_parts) < 3 and not ln.startswith("#"):
            intro_parts.append(ln.strip())
    if cur:
        sections.append(cur)
    # 若没有任何 ## 小节，用导语虚拟一节
    if not sections and intro_parts:
        sections = [{"h": title, "bullets": intro_parts[:6]}]
    intro = " · ".join(intro_parts[:2]) if intro_parts else title
    return title, sections, intro


def _card_html(platform: str, title: str, heading: str, bullets: list[str], idx: int,
               total: int, cover: bool = False) -> str:
    p = PALETTES[platform]
    bullet_html = "\n".join(
        f'<li>{html.escape(b[:60])}</li>' for b in bullets[:6]) or "<li>—</li>"
    ratio = "3 / 4" if platform == "xiaohongshu" else ("21 / 9" if platform == "wechat" and cover else "1 / 1")
    w = 1080
    h = int(w * (4 / 3)) if platform == "xiaohongshu" else (int(w * 9 / 21) if cover else w)
    label = "小红书图文卡" if platform == "xiaohongshu" else ("公众号封面" if cover else "公众号方图")
    heading_text = title if cover else heading
    sub = "" if cover else f'<p class="sub">{html.escape(bullets[0][:40]) if bullets else ""}</p>'
    return f"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(heading_text)}</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:{CJK_FONT}; background:#f0f0f0; display:flex; justify-content:center;
         padding:24px; }}
  .card {{ width:{w}px; height:{h}px; background:{p['bg']}; position:relative;
          display:flex; flex-direction:column; padding:64px 56px;
          border-radius:18px; overflow:hidden; }}
  .bar {{ width:120px; height:14px; background:{p['accent']}; border-radius:8px; margin-bottom:40px; }}
  .kicker {{ font-size:30px; letter-spacing:6px; color:{p['accent']};
            font-weight:700; margin-bottom:18px; }}
  h1 {{ font-size:{56 if cover else 46}px; line-height:1.28; color:{p['ink']};
       font-weight:800; margin-bottom:28px; }}
  .sub {{ font-size:32px; line-height:1.5; color:{p['sub']}; margin-bottom:auto; }}
  ul {{ margin-top:auto; }}
  li {{ font-size:34px; line-height:1.7; color:{p['ink']}; list-style:none;
       padding-left:34px; position:relative; margin-bottom:14px; }}
  li::before {{ content:""; position:absolute; left:0; top:18px; width:16px; height:16px;
               background:{p['accent']}; border-radius:50%; }}
  .foot {{ position:absolute; bottom:36px; right:56px; font-size:26px;
          color:{p['sub']}; }}
</style></head>
<body><div class="card">
  <div class="bar"></div>
  <div class="kicker">{label}</div>
  <h1>{html.escape(heading_text)}</h1>
  {sub if not cover else ""}
  <ul>{bullet_html}</ul>
  <div class="foot">{idx}/{total}</div>
</div></body></html>"""


def render_xiaohongshu(title: str, sections: list[dict], out_dir: Path) -> list[Path]:
    cards: list[Path] = []
    xs_dir = out_dir / "xiaohongshu"
    xs_dir.mkdir(parents=True, exist_ok=True)
    chosen = sections[:8]
    total = len(chosen) + 1
    # 封面
    cover_bullets = chosen[0]["bullets"] if chosen else []
    cover = _card_html("xiaohongshu", title, title, cover_bullets, 1, total, cover=True)
    cp = xs_dir / "01-cover.html"
    cp.write_text(cover, encoding="utf-8")
    cards.append(cp)
    for i, s in enumerate(chosen, start=2):
        h = _card_html("xiaohongshu", title, s["h"], s["bullets"], i, total)
        fp = xs_dir / f"{i:02d}-{re.sub(r'[^\\w一-鿿]+', '-', s['h'])[:20]}.html"
        fp.write_text(h, encoding="utf-8")
        cards.append(fp)
    return cards


def render_wechat(title: str, sections: list[dict], out_dir: Path) -> list[Path]:
    cards: list[Path] = []
    wc_dir = out_dir / "wechat"
    wc_dir.mkdir(parents=True, exist_ok=True)
    all_bullets = [b for s in sections for b in s["bullets"]]
    # 21:9 主封面
    cover = _card_html("wechat", title, title, all_bullets[:1], 1, 2, cover=True)
    cp = wc_dir / "cover-21x9.html"
    cp.write_text(cover, encoding="utf-8")
    cards.append(cp)
    # 1:1 方封面（标题 + 3 要点）
    square = _card_html("wechat", title, title, all_bullets[:3], 2, 2)
    sp = wc_dir / "cover-1x1.html"
    sp.write_text(square, encoding="utf-8")
    cards.append(sp)
    return cards


def maybe_render_png(html_paths: list[Path]) -> list[Path]:
    """可选：用可用渲染器把 HTML 栅格化为 PNG。无则跳过。"""
    pngs: list[Path] = []
    renderer = None
    # 1) playwright (node)
    try:
        node = subprocess.run(["node", "-e",
            "require('playwright')"], capture_output=True, text=True, timeout=8)
        if node.returncode == 0:
            renderer = "playwright"
    except Exception:
        pass
    # 2) wkhtmltoimage
    if not renderer:
        wk = subprocess.run(["wkhtmltoimage", "--version"], capture_output=True, text=True, timeout=8)
        if wk.returncode == 0:
            renderer = "wkhtmltoimage"
    if not renderer:
        return pngs
    for hp in html_paths:
        pp = hp.with_suffix(".png")
        try:
            if renderer == "playwright":
                subprocess.run(["node", "-e",
                    f"const{{chromium}}=require('playwright');"
                    f"(async()=>{{const b=await chromium.launch();"
                    f"const p=await b.newPage();"
                    f"await p.goto('file://{hp.resolve()}');"
                    f"const c=await p.$('.card');"
                    f"await c.screenshot({{path:'{pp.resolve()}'}});"
                    f"await b.close();}})()"], check=True, timeout=60)
            else:
                subprocess.run(["wkhtmltoimage", str(hp), str(pp)], check=True, timeout=60)
            if pp.exists():
                pngs.append(pp)
        except Exception:
            continue
    return pngs


def generate_social_cards(note_path: str, out_dir: str = "",
                          platforms: str = "xiaohongshu,wechat", try_png: bool = False) -> dict:
    """主入口。返回 {platform: [生成的文件路径...]}。"""
    src = Path(note_path)
    if not src.exists():
        raise FileNotFoundError(note_path)
    out = Path(out_dir) if out_dir else src.parent / "social-cards"
    out.mkdir(parents=True, exist_ok=True)
    title, sections, intro = parse_note(note_path)
    plats = [p.strip() for p in platforms.split(",") if p.strip()]
    result: dict[str, list[str]] = {}
    htmls: list[Path] = []
    if "xiaohongshu" in plats:
        cards = render_xiaohongshu(title, sections, out)
        result["xiaohongshu"] = [str(c) for c in cards]
        htmls += cards
    if "wechat" in plats:
        cards = render_wechat(title, sections, out)
        result["wechat"] = [str(c) for c in cards]
        htmls += cards
    if "zhihu" in plats or "x" in plats:
        # 占位：知乎/X 当前复用小红书卡内容，后续迭代补专属模板
        result.setdefault("zhihu", result.get("xiaohongshu", []))
        result.setdefault("x", result.get("xiaohongshu", []))
    if try_png:
        pngs = maybe_render_png(htmls)
        result["_png"] = [str(p) for p in pngs]
    # 索引页
    idx = out / "index.html"
    links = "\n".join(
        f'<li><a href="{Path(p).relative_to(out).as_posix()}">{Path(p).name}</a></li>'
        for pl in result if not pl.startswith("_")
        for p in result[pl])
    idx.write_text(
        f"<!doctype html><meta charset=utf-8><title>社媒卡 · {html.escape(title)}</title>"
        f"<h1>社媒卡产物 · {html.escape(title)}</h1><ul>{links}</ul>"
        f"<p>零依赖生成；用浏览器打开各 HTML，截图即可发平台。"
        f"运行时长视频/批量可加 --png 自动栅格化（需 playwright/wkhtmltoimage）。</p>",
        encoding="utf-8")
    result["_index"] = str(idx)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="bilinote E9 零依赖社媒卡生成器")
    ap.add_argument("--note", required=True, help="源笔记 note.md 路径")
    ap.add_argument("--out", default="", help="输出目录（默认 <note_dir>/social-cards）")
    ap.add_argument("--platforms", default="xiaohongshu,wechat",
                    help="逗号分隔：xiaohongshu,wechat,zhihu,x")
    ap.add_argument("--png", action="store_true", help="尝试栅格化为 PNG（需渲染器）")
    args = ap.parse_args(argv)
    res = generate_social_cards(args.note, args.out, args.platforms, args.png)
    print(f"✅ 社媒卡生成完成（共 {sum(len(v) for k,v in res.items() if not k.startswith('_'))} 个 HTML）")
    for k, v in res.items():
        if k.startswith("_"):
            continue
        print(f"  [{k}] {len(v)} 张")
    print(f"  索引：{res.get('_index','')}")
    if res.get("_png"):
        print(f"  PNG：{len(res['_png'])} 张")


if __name__ == "__main__":
    main()
