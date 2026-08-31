#!/usr/bin/env python3
"""bilinote-skill 回归测试（Plan F 工程地基）。

可两种方式运行：
  1) 零依赖直接跑：python tests/test_regression.py
  2) pytest（若已安装）：python -m pytest tests/

覆盖：
  - #4 弹幕恰饭检测 detect_sponsor_segments_from_danmaku（含 BV15b42177rL 场景）
  - #4 clean_transcript 物理去行
  - E8 gzh 渲染 + lint_gzh_body 禁用标签自检 + 全角标点 + <span leaf>
  - 平台风格补丁 load_style_prompts（xiaohongshu/wechat/bilibili）
  - 失败恢复标识 log_recovery / FAILURE_CODES
  - Plan C 质量闸 review_note / build_review_prompt（native brief + 校验）
  - Plan D 风格补全 全部 11 风格补丁覆盖 + preview_style 预览
  - Plan A 扩展闭环 order_extensions(E7) / needs_js_render(E1) /
    scan_ai_patterns+humanize(E6) / illustrate(E3-E4) / research(E2) / slides(E5)
  - Plan B 一源多产 produce_from_note / build_produce_prompt（native 简报 + 事实守恒）
  - Plan E 批处理 load_manifest/parse_manifest_* / slugify+dedup_slug /
    run_batch(失败隔离 + --then 链) / format_batch_report
  - Plan B wizard: _resolve_wizard_style / _build_wizard_argv（起飞前清单风格解析 + argv 拼装）
  - --video-quality 画质选择器 _build_video_format (720/1080/best)，run/embed-screenshots 入口支持
"""
from __future__ import annotations
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import bilinote as b       # noqa: E402
import gzh_format as g     # noqa: E402


# ---------------------------------------------------------------- #4 弹幕检测
def test_detect_sponsor_from_danmaku():
    # 模拟 BV15b42177rL 场景：在 311s 与 640s 附近有恰饭弹幕聚簇
    danmaku = (
        [{"t": 311.0 + i, "text": "恰饭了"} for i in range(0, 12, 2)]
        + [{"t": 640.0 + i, "text": "又是广告"} for i in range(0, 12, 2)]
        + [{"t": 100.0, "text": "讲得真好"}, {"t": 200.0, "text": "学到了"}]
    )
    segs = b.detect_sponsor_segments_from_danmaku(danmaku)
    assert len(segs) == 2, f"应检出 2 段赞助区间，实际 {len(segs)}"
    # 第一段应覆盖 311 附近
    assert segs[0][0] <= 311 <= segs[0][1]
    assert segs[1][0] <= 640 <= segs[1][1]


def test_detect_sponsor_empty():
    danmaku = [{"t": 10.0, "text": "哈哈哈"}, {"t": 20.0, "text": "前排"}]
    assert b.detect_sponsor_segments_from_danmaku(danmaku) == []


# ---------------------------------------------------------------- #4 clean
def test_clean_transcript_drops_sponsor_lines():
    transcript = (
        "00:10 - 正常内容一\n"
        "05:12 - 这期视频由赞助商支持\n"
        "05:20 - 快去下单领券\n"
        "10:00 - 正常内容二\n"
    )
    cleaned, dropped = b.clean_transcript(
        transcript, drop_ranges=[[311, 326]])
    assert dropped >= 1, "应至少去除 1 行赞助内容"
    assert "正常内容一" in cleaned and "正常内容二" in cleaned
    assert "赞助商" not in cleaned


# ---------------------------------------------------------------- E8 gzh
def test_gzh_render_and_lint():
    md = (
        "# 测试标题\n\n"
        "这是引言段落,用来测试全角标点(应转换)。\n\n"
        "## 第一章\n\n"
        "正文内容,包含**关键词**高亮。\n\n"
        "## 第二章\n\n"
        "更多内容:列表如下\n\n"
        "- 项目一\n- 项目二\n\n"
        "```python\nscale = weight * 2\n```\n"
    )
    html = g.render(md, theme="moyu-green", title="")
    body = g.extract_body(html)
    # 禁用标签自检
    problems = g.lint_gzh_body(body)
    assert not problems, f"lint 应通过，实际问题：{problems}"
    # <span leaf> 包裹
    assert 'leaf=""' in body
    # 全角标点（正文中的逗号应转全角）
    assert "，" in body
    # 代码块保留半角
    assert "scale" in body
    # 章节编号
    assert "01" in body or "一" in body


def test_gzh_all_themes_lint():
    md = "# T\n\n段落一。\n\n## 章节\n\n内容**词**。\n"
    for theme in g.THEMES:
        body = g.extract_body(g.render(md, theme=theme, title=""))
        assert not g.lint_gzh_body(body), f"主题 {theme} lint 未通过"


# ---------------------------------------------------------------- 平台风格
def test_style_prompts_loaded():
    prompts = b.load_style_prompts()
    for k in ("xiaohongshu", "wechat", "bilibili"):
        assert k in prompts and len(prompts[k]) > 50, f"{k} 补丁缺失/过短"
    # 关键特征词
    assert "痛点" in prompts["xiaohongshu"]
    assert "60/30/10" in prompts["wechat"]
    assert "黄金" in prompts["bilibili"]


# ---------------------------------------------------------------- Plan D 风格补全
def test_all_styles_have_patch():
    """Plan D 不变量：STYLES 中每个风格键都必须有详细补丁段。"""
    prompts = b.load_style_prompts()
    missing = [k for k in b.STYLES if k not in prompts]
    assert not missing, f"以下风格缺详细补丁：{missing}"
    for k in b.STYLES:
        assert len(prompts[k]) > 100, f"{k} 补丁过短（{len(prompts[k])} 字）"


def test_preview_style_list_and_single():
    # 列表模式：应含全部 16 风格键
    listing = b.preview_style("")
    for k in b.STYLES:
        assert k in listing, f"风格清单缺 {k}"
    # 单风格模式：含标签与详细规范
    single = b.preview_style("tutorial")
    assert "教程风格" in single and "前置条件" in single
    # 未知风格：友好报错，不抛异常
    bad = b.preview_style("nope")
    assert "未知风格" in bad


def test_extended_styles_loaded():
    """风格库扩展（2026-07-12）：5 个新底风格补丁与特征词校验。"""
    prompts = b.load_style_prompts()
    feats = {
        "zhihu": "先抛结论",
        "feynman": "短句锚定",
        "debate-digest": "评论区高能精选",
        "research-report": "BLUF",
        "cheatsheet": "表格",
    }
    for k, feat in feats.items():
        assert k in b.STYLES, f"STYLES 缺风格键 {k}"
        assert k in prompts and len(prompts[k]) > 100, f"{k} 补丁缺失/过短"
        assert feat in prompts[k], f"{k} 补丁缺特征词「{feat}」"


# ---------------------------------------------------------------- Plan G 缓存
def test_cache_set_get_roundtrip(tmp_path=None):
    """缓存写入后应命中；CACHE_ENABLED=False 时不缓存。"""
    import os, tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    os.environ["BILINOTE_CACHE_DIR"] = str(d)
    b.CACHE_ENABLED = True
    try:
        b._cache_set("transcribe", "k1", "00:01 测试文本")
        hit, val = b._cache_get("transcribe", "k1")
        assert hit and val == "00:01 测试文本", f"缓存应命中，实际 {hit}/{val}"
        # 未写入的键不命中
        hit2, _ = b._cache_get("transcribe", "missing")
        assert not hit2, "未写入的键不应命中"
        # 关闭缓存后不命中
        b.CACHE_ENABLED = False
        b._cache_set("transcribe", "k2", "不应写入")
        hit3, _ = b._cache_get("transcribe", "k2")
        assert not hit3, "CACHE_ENABLED=False 时不应缓存"
    finally:
        b.CACHE_ENABLED = True
        os.environ.pop("BILINOTE_CACHE_DIR", None)


def test_cache_key_stable():
    """相同入参应产相同键；不同入参应产不同键。"""
    k1 = b._cache_key("a", "b", 1)
    k2 = b._cache_key("a", "b", 1)
    k3 = b._cache_key("a", "b", 2)
    assert k1 == k2, "相同入参应产相同键"
    assert k1 != k3, "不同入参应产不同键"
    assert len(k1) == 16, f"键长应为16，实际 {len(k1)}"


def test_cache_list_and_clear(tmp_path=None):
    import os, tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    os.environ["BILINOTE_CACHE_DIR"] = str(d)
    b.CACHE_ENABLED = True
    try:
        b._cache_set("danmaku", "d1", [{"t": 1, "text": "x"}])
        b._cache_set("comments", "c1", [{"text": "y"}])
        items = b.cache_list()
        cats = {it["category"] for it in items}
        assert "danmaku" in cats and "comments" in cats, f"list 应含两类，实际 {cats}"
        n = b.cache_clear("danmaku")
        assert n == 1, f"清 danmaku 应删 1 条，实际 {n}"
        items2 = b.cache_list()
        cats2 = {it["category"] for it in items2}
        assert "danmaku" not in cats2 and "comments" in cats2, "清后 danmaku 应消失"
    finally:
        os.environ.pop("BILINOTE_CACHE_DIR", None)


# ---------------------------------------------------------------- Plan L 度量
def test_metrics_record_and_summary(tmp_path=None):
    """记录度量后 summary 应含事件分布与评分趋势。"""
    import os, tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    mp = Path(d) / "metrics.jsonl"
    os.environ["BILINOTE_METRICS"] = str(mp)
    try:
        b.record_metric("run", words=120, exports="pdf")
        b.record_metric("produce", targets="xiaohongshu,wechat", count=2)
        b.record_metric("review", auto_fix=True, score=4.5, rounds=2)
        b.record_metric("review", auto_fix=False, score=3.0, rounds=1)
        s = b.metrics_summary()
        assert "事件分布" in s and "run" in s and "produce" in s
        assert "质量评分趋势" in s and "3.75" in s, f"均值应为3.75，实际 {s}"
    finally:
        os.environ.pop("BILINOTE_METRICS", None)


# ---------------------------------------------------------------- Plan K 自定义风格+偏好
def test_load_user_styles(tmp_path=None):
    """用户自定义风格（## name 段）应被加载，@ 前缀可解析。"""
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    ud = Path(d) / "user_styles"
    ud.mkdir()
    (ud / "brand.md").write_text(
        "# 我的品牌风格\n\n## my-brand\n你是品牌写手。\n### 结构\n- 品牌调性\n",
        encoding="utf-8")
    saved = b.USER_STYLE_DIRS
    b.USER_STYLE_DIRS = [ud]
    saved_cache = b._USER_STYLES_CACHE
    b._USER_STYLES_CACHE = b.load_user_styles()  # 刷新缓存
    try:
        us = b.load_user_styles()
        assert "my-brand" in us and "品牌写手" in us["my-brand"]
        # @ 前缀解析
        assert b.resolve_style("@my-brand") == "my-brand"
        assert b.resolve_style("@unknown") == b.DEFAULT_STYLE
        assert b.resolve_style("concise") == "concise"
        # get_style_spec 能取到自定义补丁
        assert "品牌写手" in b.get_style_spec("@my-brand")
    finally:
        b.USER_STYLE_DIRS = saved
        b._USER_STYLES_CACHE = saved_cache


def test_prefs_save_load():
    """偏好记忆：save 后 load 应一致。"""
    import os, tempfile
    d = tempfile.mkdtemp()
    os.environ["HOME"] = d  # 重定向 Path.home()
    try:
        prefs = {"style": "academic", "danmaku": True, "video_quality": "1080"}
        b.save_prefs(prefs)
        got = b.load_prefs()
        assert got.get("style") == "academic"
        assert got.get("video_quality") == "1080"
    finally:
        os.environ.pop("HOME", None)


# ---------------------------------------------------------------- Plan H 系列聚合
def test_series_aggregate(tmp_path=None):
    """多份 note.md 聚合应产出总导图/索引/知识图谱。"""
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    for i, (t, hs) in enumerate([("第一集", ["开场", "核心概念"]),
                                  ("第二集", ["核心概念", "进阶"])]):
        (Path(d) / f"ep{i+1}.md").write_text(
            f"# {t}\n\n## {hs[0]}\n内容 {i+1}。\n\n## {hs[1]}\n更多。\n",
            encoding="utf-8")
    res = b.series_aggregate(
        [str(Path(d) / "ep1.md"), str(Path(d) / "ep2.md")],
        out_dir=str(d), title="测试系列")
    assert res["count"] == 2
    mm = Path(res["mindmap"]).read_text(encoding="utf-8")
    idx = Path(res["index"]).read_text(encoding="utf-8")
    graph = Path(res["graph"]).read_text(encoding="utf-8")
    assert "mindmap" in mm and "第一集" in mm and "第二集" in mm
    assert "专题索引" in idx and "ep1.md" in idx
    assert "知识图谱" in graph and "核心概念" in graph  # 共现概念


# ---------------------------------------------------------------- F-trace
def test_failure_codes_present():
    for i in range(1, 11):
        assert f"F{i}" in b.FAILURE_CODES, f"缺少失败码 F{i}"
    assert callable(b.log_recovery)


# ---------------------------------------------------------------- Plan C 质量闸
def test_review_prompt_has_sections():
    prompt = b.build_review_prompt("# 笔记\n- 要点", "源转录内容")
    for sec in ("覆盖度", "一致性", "源转录", "待审阅"):
        assert sec in prompt, f"review prompt 缺少「{sec}」"


def test_review_note_native_writes_brief(tmp_path=None):
    import tempfile
    import os
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n\n## 要点\n- A 是 B\n", encoding="utf-8")
    kind, payload = b.review_note(str(note), transcript="A 其实是 C，不是 B。")
    assert kind == "brief", f"应产 brief，实际 {kind}"
    assert Path(payload).exists(), "质检简报文件应存在"
    text = Path(payload).read_text(encoding="utf-8")
    assert "源转录" in text and "待审阅笔记" in text


def test_review_note_requires_transcript(tmp_path=None):
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "n.md"
    note.write_text("# x\n", encoding="utf-8")
    try:
        b.review_note(str(note))
        raised = False
    except ValueError:
        raised = True
    assert raised, "缺少源转录应抛 ValueError"


# ---------------- Plan I 质量闭环 auto-fix ----------------
def test_parse_review_score():
    """从质检报告抽取评分。"""
    rep = "## 质量评分\n- 覆盖度 4/5\n- 准确性 3/5\n- 结构 5/5\n"
    s = b.parse_review_score(rep)
    assert s is not None and 3 <= s <= 5, f"应解析出评分，实际 {s}"
    assert b.parse_review_score("无分数内容") is None


def test_autofix_native_writes_brief(tmp_path=None):
    """native 模式 auto-fix 应写 auto-fix-brief.md。"""
    import tempfile, os
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 要点 A（含错误数字 999）\n", encoding="utf-8")
    report = "## 一致性 / 疑似幻觉\n- 999 未在源转录出现\n## 质量评分\n2/5\n"
    kind, payload = b.auto_fix_note(str(note), report, "00:01 源内容")
    assert kind == "brief" and Path(payload).name == "note.auto-fix-brief.md"
    txt = Path(payload).read_text(encoding="utf-8")
    assert "自动修复" in txt and "质检报告" in txt


def test_review_autofix_native_briefs(tmp_path=None):
    """原生模式 review_with_autofix：第一轮 review 产简报即停，auto_fix 再产修复简报。"""
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 错误数字\n", encoding="utf-8")
    res = b.review_note_with_autofix(
        str(note), "00:01 源内容",
        auto_fix=True, target_score=4.5, max_rounds=2)
    assert res["rounds"] == 1, f"原生模式应只跑第 1 轮 review 简报，实际 {res['rounds']}"
    assert "native" in res["stopped_reason"].lower(), res["stopped_reason"]
    assert res["review_path"] and Path(res["review_path"]).exists(), "应生成 review 简报"
    assert res["fixed_path"] and Path(res["fixed_path"]).exists(), "auto_fix 应生成修复简报"


def test_review_autofix_native_no_autofix(tmp_path=None):
    """auto_fix=False 时只出 review 简报，不产修复简报。"""
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 要点\n", encoding="utf-8")
    res = b.review_note_with_autofix(str(note), "00:01 源内容", auto_fix=False)
    assert res["review_path"] and Path(res["review_path"]).exists()
    assert not res["fixed_path"], "未启用 auto_fix 不应产修复简报"


# ---------------- Plan B 一源多产 produce ----------------
def test_build_produce_prompt_has_guard(tmp_path=None):
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "src.md"
    note.write_text("# 源\n- 关键事实 A\n", encoding="utf-8")
    p = b.build_produce_prompt(note.read_text(encoding="utf-8"), "academic")
    assert "事实守恒" in p, "produce prompt 必须含「事实守恒」铁律"
    assert "源笔记（单一事实源）" in p, "必须嵌入源笔记作为事实源"
    assert "学术风格" in p, "应注入目标风格说明"


def test_produce_native_writes_brief(tmp_path=None):
    import tempfile, os
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 要点 A\n", encoding="utf-8")
    res = b.produce_from_note(str(note), targets="xiaohongshu")
    assert len(res) == 1 and res[0][0] == "brief", f"应产 brief，实际 {res}"
    brief = Path(res[0][1])
    assert brief.exists(), "produce 简报文件应存在"
    text = brief.read_text(encoding="utf-8")
    assert "事实守恒" in text and "小红书风格" in text
    assert brief.name == "note.xiaohongshu.produce-brief.md"


def test_produce_presets_registered():
    """成品包预设（produce --preset）注册校验。"""
    assert "knowledge-ip" in b.PRODUCE_PRESETS
    assert "courseware" in b.PRODUCE_PRESETS
    assert "social-matrix" in b.PRODUCE_PRESETS
    ki = b.PRODUCE_PRESETS["knowledge-ip"]
    assert "detailed" in ki["targets"] and "gzh" in ki["targets"]
    assert "humanize" in ki["extensions"] and "illustrate" in ki["extensions"]


def test_produce_preset_expands_targets_and_extensions(tmp_path=None):
    """preset 应展开 targets 并跑扩展（native 模式产 brief + ext 结果）。"""
    import tempfile, os
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 要点 A\n- 数据 123\n", encoding="utf-8")
    res = b.produce_from_note(str(note), preset="social-matrix")
    kinds = [r[0] for r in res]
    # social-matrix = 3 风格改写(xiaohongshu/bilibili/zhihu) + 1 扩展(illustrate)
    assert kinds.count("brief") == 3, f"应产 3 个风格 brief，实际 {kinds}"
    assert any(k == "ext" for k in kinds), f"应跑扩展，实际 {kinds}"


def test_produce_is_native_only(tmp_path=None):
    """produce 始终走原生简报：无 API key 也绝不调用外部 LLM，全部产 brief。"""
    import tempfile, os
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 要点 A\n", encoding="utf-8")
    res = b.produce_from_note(str(note), targets="xiaohongshu,wechat")
    assert res, "应至少产出一个产物"
    for kind, payload in res:
        assert kind == "brief", f"produce 必须全部产 brief，实际 {kind}"
        assert Path(payload).exists(), f"简报文件应存在：{payload}"


# ---- Plan A: E1–E7 扩展闭环固化 --------------------------------------
def test_order_extensions_canonical():
    # E7：任意输入都要归位到规范链，E8 永远最后
    assert b.order_extensions(["E8", "E3", "E6", "E1"]) == ["E1", "E3", "E6", "E8"]
    assert b.order_extensions(["E5", "E4", "E2"]) == ["E2", "E4", "E5"]
    assert b.order_extensions(["e6", "  ", "X9"]) == ["E6"]  # 大小写/空/未知


def test_needs_js_render():
    # E1：命中 SPA 标志且正文过短 -> 需渲染
    assert b.needs_js_render('<div id="root"></div>', 10) is True
    assert b.needs_js_render('<div id="app"></div>', 999) is False   # 正文够长
    assert b.needs_js_render("<article>" + "字" * 300, 300) is False  # 无 SPA 标志
    assert b.needs_js_render("", 0) is False


def test_scan_ai_patterns():
    text = ("值得注意的是，这项革命性技术标志着重要里程碑。"
            "专家表示这是前所未有的突破——广受好评。")
    findings = b.scan_ai_patterns(text)
    names = {n for n, _, _ in findings}
    for want in ("宣传性语言", "模糊归因", "肤浅分析铺垫", "过度强调知名度"):
        assert want in names, f"应检出「{want}」，实际 {names}"
    # 干净文本无命中
    assert b.scan_ai_patterns("今天写了三行代码，跑通了。") == []


def test_humanize_native_writes_brief(tmp_path=None):
    import tempfile, os
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# t\n- 值得注意的是，这是革命性突破。\n", encoding="utf-8")
    kind, payload, findings = b.humanize_note(str(note))
    assert kind == "brief" and Path(payload).name == "note.humanize-brief.md"
    assert len(findings) >= 2
    txt = Path(payload).read_text(encoding="utf-8")
    assert "修复对照表" in txt and "待改写笔记" in txt


def test_illustrate_and_research_and_slides_briefs(tmp_path=None):
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text(
        "# 缓存设计\n## 作用\n- 加缓存后吞吐提升 40 倍，比传统方案更快。\n"
        "## 策略\n- LRU 淘汰。\n## 一致性\n- 先写库再删缓存。\n",
        encoding="utf-8")
    # E4 信息图
    k, p = b.illustrate_note(str(note), mode="infographic")
    assert k == "brief" and Path(p).name == "note.infographic-brief.md"
    assert "视觉隐喻" in Path(p).read_text(encoding="utf-8")
    # E3 手绘
    k, p = b.illustrate_note(str(note), mode="illustration", points=2)
    assert Path(p).name == "note.illustration-brief.md"
    assert "小黑" in Path(p).read_text(encoding="utf-8")
    # E2 研究
    k, p = b.research_note(str(note), max_claims=5)
    assert k == "brief" and Path(p).name == "note.research-brief.md"
    assert "WebSearch" in Path(p).read_text(encoding="utf-8")
    assert len(b.extract_claims(note.read_text(encoding="utf-8"))) >= 1
    # E5 PPT 大纲
    k, p = b.slides_note(str(note), minutes=15)
    assert k == "brief" and Path(p).name == "note.slides-brief.md"
    outline = b.extract_slide_outline(note.read_text(encoding="utf-8"), 15)
    assert 6 <= len(outline) <= 30 and outline[0][0] == "封面"


# ---------------------------------------------------------------- Plan J 大纲前置+事实核查
def test_build_outline_prompt():
    p = b.build_outline_prompt("00:01 测试内容", "测试标题", "academic", media=True)
    assert "论点树" in p and "测试标题" in p
    assert "*Content-[mm:ss]*" in p, "视频大纲应含时间锚"
    assert "学术风格" in p
    # 非视频模式不含时间锚
    p2 = b.build_outline_prompt("正文段落", "文章", "concise", media=False)
    assert "*Content-" not in p2


def test_outline_first_writes_outline_brief(tmp_path=None):
    """native 模式 --outline-first 应额外写 outline-brief.md。"""
    import tempfile, os
    d = tmp_path or Path(tempfile.mkdtemp())
    out = Path(d) / "note.md"
    kind, payload = b.summarize("00:01 测试\n00:02 第二点", "标题",
                                out=str(out), style="concise",
                                outline_first=True)
    assert kind == "brief"
    ob = out.parent / "note.outline-brief.md"
    assert ob.exists(), "outline-first 应额外写 outline-brief.md"
    assert "论点树" in ob.read_text(encoding="utf-8")
    # 主 brief 应含大纲前置规则
    assert "大纲前置" in Path(payload).read_text(encoding="utf-8")


def test_research_brief_has_confidence_table(tmp_path=None):
    """Plan J：research 简报应含事实置信度表。"""
    import tempfile
    d = tmp_path or Path(tempfile.mkdtemp())
    note = Path(d) / "note.md"
    note.write_text("# 测试\n- 提速 40 倍，是最快的方案。\n", encoding="utf-8")
    k, p = b.research_note(str(note), max_claims=5)
    txt = Path(p).read_text(encoding="utf-8")
    assert "事实置信度表" in txt, "research 简报应含置信度表"
    assert "✅ 已证" in txt and "⚠️ 存疑" in txt and "❌ 冲突" in txt
    assert "| 置信度 |" in txt or "置信度" in txt


# ---------------------------------------------------------------- Plan E 批处理
def test_parse_manifest_text_and_json():
    items = b.parse_manifest_text(
        "# 注释行\n\nhttps://a.com/x\n./n.md | 我的笔记\n")
    assert len(items) == 2
    assert items[0]["source"] == "https://a.com/x"
    assert items[1]["source"] == "./n.md" and items[1]["title"] == "我的笔记"
    # JSON：数组 + 对象 + defaults 合并（项内优先）
    got = b.parse_manifest_json(
        {"defaults": {"style": "concise"},
         "items": ["u1", {"url": "u2", "style": "wechat"}]})
    assert got[0] == {"source": "u1", "style": "concise"}
    assert got[1]["source"] == "u2" and got[1]["style"] == "wechat"


def test_slugify_and_dedup():
    assert b.slugify("https://www.bilibili.com/video/BV15b42177rL") == "BV15b42177rL"
    assert b.slugify("https://a.com/foo/bar?x=1") == "bar"
    assert b.slugify("/tmp/some/note.md") == "note"
    assert b.slugify("中文 标题 A!!") == "中文-标题-A"
    used = set()
    assert b.dedup_slug("x", used) == "x"
    assert b.dedup_slug("x", used) == "x-2"
    assert b.dedup_slug("x", used) == "x-3"


def test_run_batch_note_ops_with_failure_isolation(tmp_path=None):
    """离线：对一批 note 跑 humanize，其中一个坏源应被隔离不影响其余。"""
    import tempfile
    d = Path(tmp_path or tempfile.mkdtemp())
    n1 = d / "a.md"
    n1.write_text("# 缓存\n## 背景\n加缓存后吞吐提升 40 倍，比传统方案更快。\n",
                  encoding="utf-8")
    out = d / "out"
    items = [{"source": str(n1), "title": "缓存实战"},
             {"source": str(d / "missing.md")}]
    recs = b.run_batch(items, op="humanize", out_dir=str(out), jobs=1)
    assert len(recs) == 2
    assert recs[0]["status"] == "ok" and recs[0]["slug"] == "缓存实战"
    assert Path(recs[0]["outputs"][0]).name == "a.humanize-brief.md"
    assert recs[1]["status"] == "failed" and recs[1]["error"]
    report = b.format_batch_report(recs, "humanize")
    assert "✅ 1 成功 / ❌ 1 失败" in report and "缓存实战" not in report  # 报告用 source 不用 slug
    assert "| 1 |" in report and "| 2 |" in report


def test_run_batch_run_op_and_then_chain(monkeypatch, tmp_path=None):
    """--op run 用 monkeypatch 免网络：run 写出真实笔记后触发 --then humanize。"""
    import tempfile
    d = Path(tmp_path or tempfile.mkdtemp())
    out = d / "out"

    def fake_run(source, out_md, **kw):
        p = Path(out_md)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# 假笔记\n## 点\n吞吐提升 40 倍，比传统方案更快。\n",
                     encoding="utf-8")
        return str(p)

    monkeypatch.setattr(b, "run", fake_run)
    recs = b.run_batch([{"source": "https://x/BV1000000000", "title": "第一集"}],
                       op="run", out_dir=str(out), jobs=1, then=["humanize"])
    assert recs[0]["status"] == "ok"
    assert Path(recs[0]["outputs"][0]).name == "第一集.md"
    # 链式后处理应产出 humanize brief，并记录在 then 里
    assert any("humanize:" in t for t in recs[0]["then"])


def test_build_video_format():
    """--video-quality 画质选择器：预设映射为 yt-dlp -f 选择器。"""
    assert b._build_video_format("720") == \
        "bestvideo[height<=720][ext=mp4]/bestvideo[ext=mp4]/bestvideo/best"
    assert b._build_video_format("1080") == \
        "bestvideo[height<=1080][ext=mp4]/bestvideo[ext=mp4]/bestvideo/best"
    assert b._build_video_format("best") == "bestvideo[ext=mp4]/bestvideo/best"
    assert b._build_video_format("1080p") == b._build_video_format("1080")
    # 未知 / 空 -> 默认 720
    assert b._build_video_format("xyz") == b._build_video_format("720")
    assert b._build_video_format("") == b._build_video_format("720")


def test_wizard_resolve_style_and_argv():
    """Plan B run --wizard：风格解析 + argv 拼装（纯函数，免网络）。"""
    # 编号解析
    assert b._resolve_wizard_style("1") == "concise"
    assert b._resolve_wizard_style("11") == "meeting"
    assert b._resolve_wizard_style("99") == b.DEFAULT_STYLE  # 越界回退
    assert b._resolve_wizard_style("xiaohongshu") == "xiaohongshu"
    assert b._resolve_wizard_style("nope") == b.DEFAULT_STYLE  # 非法键回退
    assert b._resolve_wizard_style("") == b.DEFAULT_STYLE

    # argv 拼装：全关 -> 最小化
    argv = b._build_wizard_argv("U", "detailed", False, False, False, None,
                                "720", "", "out.md")
    assert argv == ["run", "U", "--style", "detailed", "--video-quality",
                    "720", "--out", "out.md"]
    # argv 拼装：富化开关全开 + 导出 + 画质
    argv2 = b._build_wizard_argv("U", "xiaohongshu", True, True, True,
                                 "illustration", "1080", "pdf,docx", "n.md")
    assert "--danmaku" in argv2
    assert "--screenshots" in argv2
    assert "--translate" in argv2
    assert "--video-quality" in argv2 and argv2[argv2.index("--video-quality") + 1] == "1080"
    assert "--export" in argv2 and argv2[argv2.index("--export") + 1] == "pdf,docx"
    assert "illustration" not in argv2  # 手绘模式不进 run argv（由后续 illustrate 处理）
    # 非 720/1080/best 的画质回落不在此层校验（run_wizard 内做）；这里只验合法传递
    argv3 = b._build_wizard_argv("U", "academic", False, False, False, None,
                                "best", "", "a.md")
    assert argv3[argv3.index("--video-quality") + 1] == "best"
    # 评论精选开关：--comments + --comments-in-report 进入 argv
    argv4 = b._build_wizard_argv("U", "concise", False, False, False, None,
                                "720", "", "c.md", comments=True,
                                comments_in_report=True)
    assert "--comments" in argv4
    assert "--comments-in-report" in argv4


def test_comments_select_and_sections():
    """Plan C 评论区高能精选：噪声过滤 + 按赞排序 + 上下文/报告段格式。"""
    comments = [
        {"rpid": 1, "text": "前排", "likes": 9999, "user": "u1", "ctime": 0, "sub": []},
        {"rpid": 2, "text": "这个案例讲得太清楚了，收藏！", "likes": 1200,
         "user": "张三", "ctime": 1, "sub": ["同感，已三连"]},
        {"rpid": 3, "text": "😂😂😂", "likes": 800, "user": "u3", "ctime": 2, "sub": []},
        {"rpid": 4, "text": "求解：599 入会返 149 这账怎么算平的？", "likes": 530,
         "user": "李四", "ctime": 3, "sub": []},
        {"rpid": 5, "text": "一般般吧", "likes": 5, "user": "u5", "ctime": 4, "sub": []},
    ]
    # 噪声（前排/表情）被过滤；按赞排序；赞数 < min_likes 不入精选
    hi = b.select_highlight_comments(comments, top_n=8, min_likes=10)
    assert [c["rpid"] for c in hi] == [2, 4], hi  # 1200, 530；前排/表情/5赞 均被剔除
    # 上下文块格式
    ctx = b.comments_as_context(hi)
    assert "@张三" in ctx and "❤1200" in ctx
    assert "前排" not in ctx
    # 报告段格式
    sec = b.comments_as_report_section(hi)
    assert sec.startswith("## 评论区高能精选")
    assert "@张三 · ❤ 1200 赞" in sec
    assert "不代表笔记立场" in sec
    assert "同感，已三连" in sec  # 子回复展开
    # 空输入安全
    assert b.comments_as_context([]) == ""
    assert b.comments_as_report_section([]) == ""


def test_run_library_func_has_no_args_reference():
    """防回归：run() 是库函数，作用域内无 args；Plan E 加 --video-quality 时
    曾在 run 体内误用 args.video_quality 引发 NameError。用 AST 静态检查。"""
    import ast as _ast
    src = open(str(Path(__file__).resolve().parent.parent / "scripts"
                    / "bilinote.py"), encoding="utf-8").read()
    tree = _ast.parse(src)
    run_fn = next((n for n in tree.body
                   if isinstance(n, _ast.FunctionDef) and n.name == "run"), None)
    assert run_fn is not None, "未找到 run() 定义"
    bad = []
    for n in _ast.walk(run_fn):
        if isinstance(n, _ast.Attribute) and isinstance(n.value, _ast.Name) \
                and n.value.id == "args":
            bad.append(f"run() 内误用 args.{n.attr} @ line {n.lineno}")
    assert not bad, "run() 库函数体内不应出现 args. 引用:\n" + "\n".join(bad)

    # run() 必须接收 video_quality 形参（Plan E 画质开关），漏加会触发 NameError
    import inspect
    params = inspect.signature(b.run).parameters
    assert "video_quality" in params, "run() 缺少 video_quality 形参"
    # 评论精选开关（Plan C）也必须是 run() 的正式形参，否则 handler 透传会 NameError
    assert "comments" in params, "run() 缺少 comments 形参"
    assert "comments_in_report" in params, "run() 缺少 comments_in_report 形参"
    # Plan J 大纲前置开关也必须是 run() 的正式形参
    assert "outline_first" in params, "run() 缺少 outline_first 形参"


# 兼容零依赖 runner：无 pytest 时提供最简 monkeypatch 垫片
class _MonkeyShim:
    def __init__(self):
        self._undo = []

    def setattr(self, obj, name, val):
        self._undo.append((obj, name, getattr(obj, name)))
        setattr(obj, name, val)

    def undo(self):
        for obj, name, old in reversed(self._undo):
            setattr(obj, name, old)


# ---------------------------------------------------------------- runner
def _run_all():
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    import inspect
    passed = 0
    failed = 0
    for fn in fns:
        shim = None
        try:
            if "monkeypatch" in inspect.signature(fn).parameters:
                shim = _MonkeyShim()
                fn(shim)
            else:
                fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
            failed += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ERROR {fn.__name__}: {type(e).__name__}: {e}")
            failed += 1
        finally:
            if shim is not None:
                shim.undo()
    print(f"\n{passed} passed, {failed} failed (共 {len(fns)} 项)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_run_all())
