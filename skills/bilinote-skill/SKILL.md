---
name: bilinote-skill
version: 2.4.0
description: 将视频(B站/YouTube/抖音/快手/本地文件)或文本(文章URL/粘贴文本/txt/md/pdf/docx)整理成结构化Markdown笔记。视频走字幕优先→bcut/kuaishou转写→LLM总结；非视频输入源直接总结。触发词:做笔记,整理成笔记,summarize
  video,turn into notes,笔记,总结视频,take notes from video,会议纪要,视频摘要,视频笔记。agent
  原生模式，全程无需外部 API key。支持多模态视觉理解、思维导图、PDF/Word导出。集成 7 项扩展能力（E1 浏览器自动化抓取、E2
  研究写作辅助、E3 小黑手绘配图、E4 信息图生成、E5 网页PPT生成、E6 AI痕迹去除、E8 公众号排版美化；E7 为调用优先级与时机）+
  导出，全部内置于一个技能中。
agent_created: true
disable-model-invocation: true
---

# BiliNote Skill (AI video notes, no RAG)

Generate clear, structured Markdown notes from videos. The pipeline mirrors
BiliNote (JefferyHcool/BiliNote, MIT): prefer existing subtitles, transcribe
audio only when needed, then delegate final note generation to the agent
agent's own LLM (native mode — **no external LLM API key required anywhere**).
The RAG chat/QA capability of upstream BiliNote is intentionally excluded.

## 🚀 5 秒上手（agent 触发后速记）

触发后按此主链路走，细节见各 Checkpoint：

`CP1 智能默认采集` → `等待期被动预览` → `concise 草稿` → `CP5-A 风格预览` → `CP5-B 渐进增强` → `📋 质检摘要` → `交付 + S7`

- **有 `~/.bilinote/profile.yaml`** → CP5-A Step 0 走轻量确认（**仅 1 弹窗**：就按这个来 / 换风格看看）。选「就按这个来」即按默认风格 + 增强链出成品，**跳过四预览与 CP5-B**。
- **无 Profile** → 标准四风格并行预览（🔥小红书 / 📊商业 / ⚡精简 / 🎭费曼），用户看到真实产出再选方向。
- 说"换风格" → 立即退回标准路径（Profile 仅加速键，非绑架）。
- 交付前必过 **📋 质检摘要**（硬门禁 + 冷读外审[仅 E6] + 跨笔记索引[仅 series]），**不过不交付**。

```yaml
# ~/.bilinote/profile.yaml 示例（常用户加速键）
default_style: xiaohongshu   # 默认产出风格
enhance: [E6, E8]            # 默认增强链
avoid: [academic]            # 永不主动推荐的风格（可选）
```

> 完整用户向示例（场景 A 首次 / 场景 B 常用户）见同目录 `README.md`「快速上手示例」。

## When to use

- "为这个 B站/YouTube 视频做笔记", "把这条视频整理成 Markdown"
- "summarize this video into notes", "turn this lecture into structured notes"
- Any request to extract a readable, timestamped summary from a video URL or
  local video file.
- **非视频输入也支持**（统一入口 `run` 会自动识别）：
  - 文章 URL → 自动抓取网页正文后整理成笔记
  - 直接粘贴的文本 / `.txt` `.md` `.json` `.csv` / `.pdf` `.docx` `.doc` 文件
    → 完整读取后整理成笔记
  - 本地视频 / 音频文件（同视频流程：fetch → 转写 → 笔记）

> 输入类型在入口处**自动判定**：是文本 / 链接 / 视频 / 音频 / 文档，再进入对应流程；
> 非视频输入会跳过语音识别，直接进 `summarize`，且**不生成时间标记与截图占位**。

## Prerequisites

| 依赖 | 必须 | 安装 | 用途 |
|------|------|------|------|
| Python 3.10+ | ✅ | — | 运行 `scripts/bilinote.py` |
| `requirements.txt` 包 | ✅ | `pip install -r scripts/requirements.txt` | pypdf / python-docx / trafilatura / yt-dlp |
| `ffmpeg` | ⚠️ 仅视频/截图 | `apt/brew install ffmpeg` | 音频提取、抽帧、截图嵌入 |
| LLM API key | — 已移除 | 不需要，也不支持 | 技能**始终**走 agent-native 模式（由 agent 当前 LLM 生成笔记），无任何外部 LLM API 依赖 |

> **零基础启动**：只装 Python → `pip install -r scripts/requirements.txt` → 能对文章/文本/PDF 生成笔记。加视频支持再加 ffmpeg。

## 安装 / Install（多 runtime 兼容）

本技能遵循 [Agent Skills Standard](https://agentskills.io)，可在任意 skills-compatible runtime 安装（WorkBuddy / Claude Code / Codex / Cursor / OpenClaw / Hermes / Gemini CLI / OpenCode 等）。技能逻辑为纯 Python（标准库 + 可选第三方包），无 runtime 专属硬绑定。

**方式一 · 一行命令（auto-detect）** — 将整个 `bilinote-skill/` 目录复制到宿主的 skills 目录，目录名即技能名：

```bash
cp -r bilinote-skill ~/.workbuddy/skills/   # WorkBuddy
cp -r bilinote-skill ~/.claude/skills/      # Claude Code
cp -r bilinote-skill ~/.codex/skills/       # Codex
```

**方式二 · 手动路径表**

| Runtime | skills 目录 |
|---------|-------------|
| WorkBuddy | `~/.workbuddy/skills/` |
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| Cursor | `<project>/.cursor/skills/` |
| 其他 Agent Skills Standard 兼容运行时 | 参见其文档的 skills 路径 |

**方式三 · 作为参考资料** — 不安装，仅阅读 `SKILL.md` 与 `references/` 借鉴方法论亦可。

> **运行时能力提示**：E3 手绘配图 / E4 信息图生成依赖宿主 agent 提供的「图像生成工具」（WorkBuddy 为 `ImageGen`，Claude Code / Codex / Cursor 等 runtime 用等效工具）。该能力缺失时技能自动降级为「纯文字 + 配图锚点建议」，不报错。

## How to use

Run `scripts/bilinote.py`. Subcommands:

### Full pipeline (`run`) — 统一入口，自动识别输入类型

`run` 是**唯一入口**，会先 `classify_source()` 判定输入类型，再路由到对应流程：

| 输入 | 识别为 | 走的流程 |
|------|--------|----------|
| B站/YouTube 等视频平台 URL | `video_url` | fetch → 字幕/转写 → summarize |
| 直链 `.mp4/.mp3` 等媒体 URL | `media_url` | fetch → 字幕/转写 → summarize |
| 本地 `.mp4/.mp3/...` 视频/音频 | `media_file` | fetch_local → 转写 → summarize |
| 本地 `.vtt/.srt/.ass/.ssa/.sub` 字幕文件 | `subtitle_file` | **读字幕** → summarize（跳过 fetch + 转写） |
| 其它 http(s) 文章 URL | `article_url` | **scrape 网页正文** → summarize |
| 本地 `.txt/.md/.pdf/.docx/.doc/...` 文件 | `doc_file` | **读取文档** → summarize |
| 直接粘贴的纯文本 | `text` | 直接 summarize |

- **视频/音频类**（video_url / media_url / media_file）：走原视频管线；可加
  `--screenshots` / `--embed-screenshots` / `--no-time-markers`。
- **非视频类**（article_url / doc_file / text）：**自动跳过转写**，直接把读到的
  正文喂给 `summarize`；此时 `media=False`，提示词/简报会**关闭时间标记与截图占位**
  （笔记按"原文内容"而非"视频转录"组织）。
  - 文章 URL 输入额外支持 **`--images`**：抓取网页内的原文配图，笔记中用 `*Image-N*`
    标记引用，生成后由 `embed-article-images` 下载并嵌入（见下方「Embed article
    images」）。

```bash
# 视频 URL（默认行为）
python scripts/bilinote.py run "VIDEO_URL" --out note.md
# 本地视频文件（--local 通常无需指定，会自动识别）
python scripts/bilinote.py run ./lecture.mp4 --out note.md
# 文章 URL：自动抓取网页正文并整理成笔记
python scripts/bilinote.py run "https://example.com/article" --out note.md
# 本地 PDF / Word / 文本：完整读取后整理成笔记
python scripts/bilinote.py run ./report.pdf --out note.md
python scripts/bilinote.py run ./notes.txt --out note.md
# 直接粘贴文本（用引号包住多行内容）
python scripts/bilinote.py run "这里是直接粘贴的长文本……" --out note.md
# 文章 URL + 嵌入原文配图（商业风格）：抓取正文与配图，生成含 *Image-N* 标记的笔记
python scripts/bilinote.py run "https://example.com/article" --style business --images --out note.md
# 仅提供字幕文件 → 直接读字幕进入 summarize（跳过 fetch + 转写）
python scripts/bilinote.py run ./subtitle.vtt --out note.md
# 提供视频 URL + 字幕文件 → 跳直接读字幕，跳过 fetch 字幕下载
python scripts/bilinote.py run "VIDEO_URL" --subtitle-file ./subtitle.vtt --out note.md
# 提供本地视频 + 字幕文件 → 跳直接读字幕，跳过转写
python scripts/bilinote.py run ./video.mp4 --subtitle-file ./subtitle.vtt --out note.md
# run --wizard：交互起飞前清单（绕过 AskUserQuestion 4 选项上限），逐一确认
#   全部 16 风格 + 弹幕/抽帧/翻译/手绘开关 + 画质 + 导出，再调用 run 管线
python scripts/bilinote.py run "VIDEO_URL" --wizard
# ⚠️ 注意：--wizard 仅覆盖「起飞前」收集（风格/富化/画质/导出）。
#   笔记生成后，agent 仍须走 CHECKPOINT 5（生成后增强确认），wizard 用户同样享受 CP5 增值。
```
Options: `--no-time-markers`, `--screenshots`, `--no-ai-summary`,
`--transcriber bcut|biji|kuaishou|auto`
(default `auto` = language-aware router). `biji` is an alias of `bcut`
(必剪 = Bilibili BCut ASR); `kuaishou` (快手) and `bcut` are keyless online
ASR. In `auto` mode the skill routes by
language: **zh/en → bcut first, fallback kuaishou**;
**other langs (ja/ko/...) → kuaishou first, fallback bcut** (Kuaishou handled
ja/ko correctly in testing). If both online engines fail, it raises advice
(`--lang`) so you decide. `--lang <code>`
skips detection and forces a language.
`--lang zh`, `--export pdf,docx` (also emit PDF/Word alongside the Markdown).

**Report style (`--style`)** — 在 BiliNote 官方 9 种笔记风格基础上，bilinote 额外提供
**7 个平台/场景风格扩展**（控制 AI 笔记的**语气 / 表达 / 侧重点**，与「格式」如目录/截图相互独立）：
- 官方 9 种：`concise`(精简，默认), `detailed`(详细), `tutorial`(教程), `academic`(学术),
  `xiaohongshu`(小红书), `lifestyle`(生活向), `task`(任务导向), `business`(商业), `meeting`(会议纪要)
- bilinote 平台/场景扩展：`wechat`(公众号长文), `bilibili`(B站视频脚本),
  `zhihu`(知乎问答体), `feynman`(费曼讲解体), `debate-digest`(热议盘点体),
  `research-report`(投资研报体), `cheatsheet`(速查表)
- **全部 16 种风格现均已配有结构化详细规范补丁**（Plan D + 风格库扩展）：3 个平台风格
  （`xiaohongshu`/`wechat`/`bilibili`，含标题公式/正文结构/标签/互动钩子/合规提示）
  + 8 个通用风格（`concise`/`detailed`/`tutorial`/`academic`/`lifestyle`/`task`/
  `business`/`meeting`，含各自的结构模板/写法要求/禁忌）+ 5 个扩展风格
  （`zhihu`先抛结论分层论证/`feynman`具体开场+短句锚定+类比讲原理，借鉴 scientific-learning-loop 表达DNA/
  `debate-digest`以评论区高能精选为骨架/`research-report`BLUF+数据表+风险/`cheatsheet`表格化速查），
  统一存放于 `references/style_prompts.md`，由 `load_style_prompts()` 解析后在
  agent-native 模式下自动注入到生成简报（方法论中平台部分借鉴 jnMetaCode/agency-agents-zh，
  MIT，已改写为 bilinote 自有表达；feynman 表达 DNA 借鉴 scientific-learning-loop）。
风格会被注入原生模式简报，生成的笔记即按该
语气撰写。可通过环境变量 `BILINOTE_STYLE=detailed` 设默认值。

> 交互模式下 CP1 另提供 **12 个组合预设**（底风格 + 扩展打包，支持单选/多选/自定义），详见「CHECKPOINT 1」章节。
示例：
```bash
python scripts/bilinote.py run "VIDEO_URL" --style xiaohongshu --out note.md
python scripts/bilinote.py summarize --transcript t.txt --style meeting --out m.md
# 风格预览（Plan D）：产出前先看某风格会注入什么提示词，或列出全部 16 种风格
python scripts/bilinote.py style-preview            # 列出全部风格
python scripts/bilinote.py style-preview tutorial   # 查看单个风格完整规范
```

### 视频富化增强（借鉴 B 站官方 / PiliPlus 等客户端）

这一组是 **可选增强器（optional enrichers）**：每个都在失败时安全返回空结果，
**不影响核心「字幕优先 → 转写」主链路**。仅对**在线视频**（尤其 B 站）生效，本地文件/文章/纯文本自动跳过。

| 编号 | 能力 | 开关 | 说明 |
|------|------|------|------|
| **#0** | **B 站官方 AI 总结优先** | 默认开，`--no-bili-ai` 关 | 对 B 站视频先调官方 `conclusion/get`：拿到 **summary + 时间轴大纲 + AI 字幕**（免下载音频/ASR）。命中则用 AI 字幕作转写来源，大纲写入简报参考区并驱动截图时间点；失败自动回退字幕优先/转写。**多数视频需登录**，用 `--bili-cookie`（含 SESSDATA）或环境变量 `BILINOTE_BILI_COOKIE` 提升命中率。 |
| **#1** | **弹幕补转写（二级上下文）** | `--danmaku` | 抓取弹幕作为「第二字幕」喂给 LLM，辅助判断高能片段、梗与高赞观点。优先现代 protobuf 分段接口，回退旧版 XML；弹幕**不会照抄进正文**。 |
| **#2** | **高能智能抽帧建议** | 随 `--screenshots` 自动 | 依据「官方大纲章节起点 > 弹幕密度峰值 > 均匀采样」推荐截图时间点，自动生成 `*Screenshot-[mm:ss]*` 建议标记，替代纯均匀截图。 |
| **#3** | **时间戳可点击跳转** | `--linkify` | 把笔记里的 `*Content-[mm:ss]*` 与裸 `[mm:ss]` 转成指向视频对应时间点的链接（B 站 `?t=秒`，YouTube `?t=Ns`）；**保留 `*Screenshot-*` 标记不动**，不影响截图嵌入。 |
| **#4** | **内容净化（赞助/广告/片头片尾去除）** | 默认开，`--no-clean` 关 | **替代外网 SponsorBlock**（其众包库以 YouTube 为主、B 站无数据）。两层：① 通用规则交给 LLM 内容自判断跳过片头口播/片尾 CTA/赞助广告；② 弹幕信号（`恰饭/广告/种草`等关键词聚簇）检出疑似赞助区间，列为参考在简报中指示跳过（原生模式不做物理删行，由 agent 生成时遵循）。 |
| **#5** | **外语原声翻译** | `--translate` | 提示 LLM 把外语要点翻译成简体中文（专名保留英文），最终笔记以中文为主。 |

```bash
# B 站视频 + 官方 AI 总结（默认开）+ 弹幕上下文 + 截图 + 时间戳可跳转
python scripts/bilinote.py run "https://www.bilibili.com/video/BVxxxx" \
  --bili-cookie "SESSDATA=xxxx" --danmaku --screenshots --linkify --out note.md
# 更清晰的截图/多模态帧？指定视频画质（B站 1080p 及以上需登录态）
#   --video-quality 720(默认) | 1080 | best
#   下 1080p/best 需先提供登录态：设 BILINOTE_YTDLP_COOKIES=edge/chrome，
#   或导出 cookie 文件后设 BILINOTE_YTDLP_COOKIES=/path/cookies.txt
python scripts/bilinote.py run "VIDEO_URL" --screenshots --video-quality 1080 \
  --out note.md
# 关闭官方 AI 总结，走纯字幕/转写
python scripts/bilinote.py run "VIDEO_URL" --no-bili-ai --out note.md
# 外语视频翻译成中文
python scripts/bilinote.py run "https://youtu.be/xxxx" --translate --out note.md
# 评论区高能精选：抓高赞评论作观众态度参考（--comments-in-report 可写入正文）
python scripts/bilinote.py run "VIDEO_URL" --comments --out note.md
python scripts/bilinote.py run "VIDEO_URL" --comments --comments-in-report \
  --out note.md
```

**独立子命令**（便于单独取数/后处理）：
```bash
# #0 只拉官方 AI 总结（渲染 Markdown / 导出 AI 字幕转写 / 原始 JSON）
python scripts/bilinote.py bili-summary "BVxxxx" --cookie "SESSDATA=xxx" --out ai.md --transcript ai.txt
# #1 只抓弹幕上下文
python scripts/bilinote.py danmaku "BVxxxx" --limit 500 --out danmaku.txt
# #C 评论区高能精选：抓取高赞评论
python scripts/bilinote.py comments "BVxxxx" --limit 60 --top 8 --min-likes 10 --out comments.txt
# #C 直接输出可粘贴进报告的「## 评论区高能精选」段
python scripts/bilinote.py comments "BVxxxx" --report --out comments_section.md
# #2 只推荐截图时间点（可直接输出 *Screenshot-[mm:ss]* 标记行）
python scripts/bilinote.py suggest-frames "BVxxxx" --n 6 --markers
# #3 给已有笔记的时间戳加可点击链接
python scripts/bilinote.py linkify --note note.md --url "https://www.bilibili.com/video/BVxxxx"
# #4 去除转录/笔记里的赞助/广告/片头片尾（手动区间 + 自动抓弹幕检测 B 站赞助段）
python scripts/bilinote.py clean transcript.txt --ranges 30-45,120-140 \
  --url "https://www.bilibili.com/video/BVxxxx" --out cleaned.txt
# 关闭内容净化、保留原文
python scripts/bilinote.py run "VIDEO_URL" --no-clean --out note.md
# E8 把定稿 note.md 排成公众号内联 HTML（借鉴 gzh-design-skill 排版理念）
python scripts/bilinote.py gzh note.md --theme moyu-green --title "文章标题"
# E8 仅做公众号正文合规自检（禁用标签/全内联），不产文件
python scripts/bilinote.py gzh note.md --lint
# 质量闸（Plan C）：拿源转录核对定稿笔记，输出覆盖度/幻觉/结构质检报告
python scripts/bilinote.py review note.md --transcript transcript.txt
# Plan I 质量闭环：质检后自动回修问题段并复检（达标即停，默认上限 2 轮）
python scripts/bilinote.py review note.md --transcript transcript.txt --auto-fix
python scripts/bilinote.py review note.md --transcript transcript.txt --auto-fix --target-score 4.5 --max-rounds 2
# 或让 run 生成笔记后自动质检一遍（默认关闭）
python scripts/bilinote.py run "VIDEO_URL" --review --out note.md
# 风格预览（Plan D）：产出前查看某风格注入的完整提示词，或列出全部 16 种风格
python scripts/bilinote.py style-preview            # 列出全部风格 + 一句话说明
python scripts/bilinote.py style-preview academic   # 查看单个风格完整规范
# 一源多产（Plan B）：以 note.md 为唯一事实源，一次派生多份风格化/多平台产物
# 默认派生 xiaohongshu,wechat,bilibili 三份平台笔记；也支持 gzh/mindmap/pdf/docx
python scripts/bilinote.py produce note.md
python scripts/bilinote.py produce note.md --targets xiaohongshu,academic,gzh,mindmap
python scripts/bilinote.py produce note.md --out-dir ./dist   # 产物集中输出到目录
# 成品包预设（produce --preset）：一键产出整期物料（targets + 扩展简报自动展开）
#   knowledge-ip  = detailed+公众号+导图+PDF + 去AI味+信息图+研究（知识IP专栏）
#   courseware     = tutorial+公众号+导图+PDF + 手绘+PPT（课程课件）
#   social-matrix  = 小红书+B站+知乎 + 信息图（社媒矩阵）
python scripts/bilinote.py produce note.md --preset knowledge-ip
# 扩展闭环固化（Plan A）：把 E1–E7 后处理能力脚本化触发
# E6 去 AI 味：本地扫描 10 类 AI 痕迹 + native 改写；--scan-only 仅出检测报告
python scripts/bilinote.py humanize note.md
python scripts/bilinote.py humanize note.md --scan-only
# E3/E4 配图简报：抽取配图锚点 -> ImageGen 生图简报（illustration=小黑手绘 / infographic=一页图解）
python scripts/bilinote.py illustrate note.md --mode infographic
python scripts/bilinote.py illustrate note.md --mode illustration --points 3
# E2 研究补充：抽取待证据主张 -> WebSearch 研究简报（查询清单 + 引用规范）
python scripts/bilinote.py research note.md --max 5
# E5 网页PPT：抽取叙事弧大纲 -> PPT 简报（交 agent 生成单文件 HTML）
python scripts/bilinote.py slides note.md --minutes 30
# 批处理与系列化（Plan E）：对一批源批量跑既有能力，失败隔离 + 汇总报告
# 系列视频清单 -> 逐集出笔记（并发 3），并对每篇产出的真实笔记链式再产小红书/公众号
python scripts/bilinote.py batch --manifest urls.txt --op run --jobs 3 --then produce
# 缓存管理（Plan G）：同源换风格零重抓；查看/清空取数缓存
python scripts/bilinote.py cache ls                       # 列出各类别条目数与大小
python scripts/bilinote.py cache clear                    # 清空全部缓存
python scripts/bilinote.py cache clear --category danmaku # 只清弹幕缓存
# 产出度量（Plan L）：查看事件分布/风格产出/质量评分趋势
python scripts/bilinote.py metrics
# 系列聚合（Plan H）：多份 note.md -> 系列总导图 + 专题索引页 + 跨集知识图谱
python scripts/bilinote.py series ep1.md ep2.md ep3.md --title "我的专题"
python scripts/bilinote.py series --dir ./notes --title "系列专题"   # 扫描目录聚合
# run --no-cache 强制重新抓取/转写（忽略缓存）
python scripts/bilinote.py run "VIDEO_URL" --no-cache --out note.md
# 🟡 cache 命中提示（D3）：同源换风格时若命中缓存，run 会零重抓。
#   agent 应在回复中主动告知用户："已命中该源缓存，换风格零重抓、秒出笔记。"——
#   让用户知道缓存存在，鼓励对同一源做多风格派生（如先 detailed 再 xiaohongshu）。
# Plan J 大纲前置：先生成论点树大纲供确认，再据大纲填正文（减少遗漏）
python scripts/bilinote.py run "VIDEO_URL" --outline-first --out note.md
# Plan K 自定义风格库：在 references/user_styles/*.md 或 ~/.bilinote_styles/*.md 放
#   自定义风格（## name 段格式），用 --style @my-brand 引用；wizard 会记住上次选择
python scripts/bilinote.py run "VIDEO_URL" --style @my-brand --out note.md
# 对一个目录里已有的所有 note.md 批量去 AI 味
python scripts/bilinote.py batch --dir ./notes --op humanize --out-dir ./batch-out
# 直接多参数传源 + 指定风格
python scripts/bilinote.py batch https://b23.tv/x https://b23.tv/y --op run --style xiaohongshu
```

> **质量闸 `review`（Plan C）**：以**源转录为事实基准**审阅定稿 `note.md`，输出
> Markdown 报告含五节——覆盖度检查 / 一致性·疑似幻觉 / 结构与可读性 / 修订建议 / 质量评分。
> 写 `<名>.review-brief.md`，由 **agent 当前 LLM 充当质检员**读简报后产出报告。
> `run --review` 在笔记生成后内联触发质检（写 `<名>.review-brief.md`）；质检失败不阻断主流程。
>
> **一源多产 `produce`（Plan B）**：把定稿 `note.md` 当作**唯一事实源（SSOT）**，
> 不重新转写，直接派生多份产物——风格键 → `<名>.<风格>.md`，`gzh` → `<名>.gzh.html`，
> `mindmap` → `<名>.mindmap.md`，`pdf`/`docx` → 导出。改写类产物（风格键）写
> `<名>.<风格>.produce-brief.md`，由 **agent 当前 LLM 充当改编员**读简报后产出
> （简报含「事实守恒」铁律，禁止增删事实/编造）。
> 这样一份素材可一次铺到多个平台，且所有衍生都回溯到同一事实源，避免事实漂移。
>
> **扩展闭环固化（Plan A）**：把原本仅文档化、靠 agent 临场发挥的后处理扩展（E1–E7）
> 固化为「确定性脚手架 + native 简报」。本地能算死的部分用纯 Python 直接算，需要
> agent 工具的部分产出自足简报交当前 LLM/工具执行：
> - **`humanize`（E6 去 AI 味）**：本地正则**确定性扫描 10 类 AI 写作痕迹**（过度强调意义/
>   宣传性语言/模糊归因/三段式/破折号滥用…），报告命中数与样例；再 native 改写——写
>   `<名>.humanize-brief.md`（内嵌扫描结果 + 修复对照表
>   交当前 LLM 改写）。`--scan-only` 只出检测报告不改写。
> - **`illustrate`（E3/E4 配图）**：抽取配图锚点，产出 `<名>.illustration-brief.md`（小黑 IP 手绘
>   逐张提示词）或 `<名>.infographic-brief.md`（一页图解 + 视觉隐喻位），交 **ImageGen 工具**生图。
> - **`research`（E2 研究补充）**：抽取含数据/比较/因果/绝对断言的待证据主张，产出
>   `<名>.research-brief.md`（WebSearch 检索词清单 + 引用规范 + 禁编造铁律），交 **WebSearch** 补料。
> - **`slides`（E5 网页PPT）**：按「钩子→定调→主体→收束」抽取叙事弧大纲（页数随 `--minutes` 伸缩），
>   产出 `<名>.slides-brief.md` 交 agent 生成单文件 HTML 翻页 PPT。
> - **E1 SPA 检测 / E7 顺序编排**内建为 `needs_js_render()` 与 `order_extensions()` 两个纯函数：
>   前者判断页面是否需 browser-use 渲染，后者把一组扩展代码按 `E1→E2→E3→E6→E4/E5→E8` 规范链排序。
>
> **批处理与系列化 `batch`（Plan E）**：把上述所有能力放大到「一批源」维度，专治整季番剧 /
> 频道合集 / 一批已有笔记的规模化处理，**不重复实现流水线**，只做编排：
> - **三种取源方式**：位置参数直接传多个源；`--manifest` 清单文件（`.json` 数组或
>   `{items, defaults}`，或 `.txt` 每行一个源、支持 `源 | 标题`、`#` 注释）；`--dir` 目录扫描
>   （配 `--glob`，默认 `*.md`，用于对一批笔记批量后处理）。
> - **`--op`** 选择每项执行的操作：`run`（默认，全流程出笔记）/ `produce` / `humanize` /
>   `illustrate` / `research` / `slides`——复用同名子命令的既有实现（含其 native 简报行为）。
> - **`--then`**（仅 `--op run`）：对每篇产出的**真实笔记**（非 native 简报）链式再跑后处理，
>   如 `--then produce,humanize`，实现「拉取→出笔记→多平台分发」一条龙；native 模式（无 key
>   只出简报）会标记为 `deferred`，提示先据简报补全笔记再跑。
> - **失败隔离**：单项报错被捕获记入报告，不影响其余项（`--stop-on-error` 可改为遇错即停）；
>   `--jobs N>1` 用线程池并发（适合下载/LLM I/O 密集）；文件名按标题/源 `slugify` 去重，
>   报告按输入顺序稳定排列。
> - **产出**：统一输出目录下 `batch-report.md` + `batch-report.json`（每项：序号/源/状态/产物/备注）。
> - **🟡 强制：batch 完成后必须展示报告**。产出报告后，agent **必须**用 `Read` 读取 `batch-report.md` 摘要，在回复中展示关键统计（成功 N / 失败 M / 产物路径），并主动询问："是否对这批笔记做统一后处理（`--then produce,humanize`）或聚合为系列知识库（`series`）？"——避免报告生成后用户不知情、错失批量增值。

**工程自检与回归测试**（维护技能时用；改动文档/代码后建议先跑）：
```bash
# 结构自检：校验 SKILL.md 章节/E1–E8/风格清单/子命令/主题是否一致（改漏预警）
python scripts/lint_skill.py            # 0 错误即通过；--strict 视警告为失败
# 回归测试：#4 弹幕检测 + clean + E8 gzh lint + 平台风格 + F 码（零依赖可直接跑）
python tests/test_regression.py         # 亦兼容 python -m pytest tests/
```
> 失败恢复带 **F1–F10 运行时标识**：触发任一恢复分支会打 `[bilinote][F3] ...` 日志，
> 便于检索与自动化追踪（对应文末「failure modes」表）。

> **原生模式下 #3 linkify 的时机**：原生（无 API Key）模式笔记由 agent 生成，简报会附带
> linkify 指令；**待 agent 写出 note.md 后**再运行 `linkify` 子命令即可。

### agent-native mode (only mode, no API key)

`run` / `summarize` do **not** call any external LLM. (The `BILINOTE_LLM_API_KEY` /
`BILINOTE_LLM_BASE_URL` / `BILINOTE_LLM_MODEL` variables and the API direct-write
path have been **removed** — there is no API mode, only native.) Instead they:

1. Produce the transcript (subtitle or online-free transcription), then
2. Write a self-contained **brief** to `<out>.brief.md` (transcript + title +
   tags + the exact note rules), and
3. Return — the note itself is generated by **you (the agent)** using your own
   conversation LLM, then written to `<out>`.

**Agent action required to finish (no extra tool calls to the pipeline):**
- Read `<out>.brief.md` (it contains the transcript and rules).
- Optionally also read `references/note_prompt.md` for the full prompt.
- Generate the structured Markdown note per the rules and write it to `<out>`.
- If the user wanted PDF/Word, run
  `python scripts/bilinote.py export <out> --formats pdf,docx`.

This is what makes the skill usable with zero LLM configuration — no API key
is ever consulted, in agent or anywhere else.

### 原生模式交互决策（agent-native interactive decisions）

在原生模式下，`run` / `summarize` 生成 `<out>.brief.md` 后**不直接生成笔记**，
而是把决策权交给 agent。**以下 5 个 checkpoint 是强制流程**——即便用户说"随便""默认就行"，
也必须先走过 CP1（智能默认采集）与 CP5（最终形态中枢：CP5-A 风格预览 + CP5-B 渐进增强），CP2/CP3/CP4 按条件跳过。
**明确意图用户可走「🚀 提速通道」直接绕过 CP1/CP5 出成品。**

**执行顺序**：CP1（智能默认采集）→ [CP2] → [CP3] → [CP4] → CP5-A（风格预览）→ CP5-B（渐进增强）
- CP1 无条件执行（生成前，**智能默认采集**管线原料——B站→弹幕+截图 / YouTube→评论 / 文章→配图 等，告知可取消；风格由 CP5-A 定）
- CP2 检查简报第 7 条是否含 `*Screenshot-[mm:ss]*` 标记
- CP3 检查输入是否为 article_url + 简报第 9 条是否列出配图列表
- CP4 检查 fetch 是否返回网络错误
- CP5-A 在 note.md 生成后、交付前**无条件执行**——先展示 4 版真实风格样例让用户选方向（所见即所选）
- CP5-B 紧随 CP5-A——按选定风格渐进确认视觉/增强/输出，动态过滤无关选项

### 🎯 风格偏好 Profile（可选 · 自动路由 · v2.1 新增）

> 借鉴 sansheng-write 的 profile 系统。让常用户跳过 CP5 选择、直达成品，同时不绑架新手。

**文件位置**：`~/.bilinote/profile.yaml`（不存在则走标准 CP5，无惩罚、无提示噪声）。

**格式（极简，2-3 行即可）**：
```yaml
default_style: xiaohongshu   # 默认产出风格（concise/wechat/xiaohongshu/business/feynman…）
enhance: [E6, E8]            # 默认增强链（去AI味 + 公众号排版等；可选）
avoid: [bilibili, academic]  # 永不主动推荐的风格（可选）
```

**双路径分流（在 CP5-A 开头检测）**：
- **有 Profile** → 走「轻量确认路径」：直接展示偏好风格的完整预览 + 一句确认，确认即按 Profile 默认增强链出成品，**全程仅 1 次弹窗**，不弹 CP5-A 四预览、不弹 CP5-B。
- **无 Profile** → 走标准 CP5-A 四风格预览 + CP5-B 两问（同 v2.0.1）。
- **Profile 用户说"换风格"** → 立即退回标准四预览路径，不强制。

> Profile 是加速键不是绑架：任何时候用户说"换风格 / 不一样 / 随便来"，立刻回到完整选择，不走到一半卡住。

### 📌 铁律总纲（硬约束集中处 · v2.1 新增）

分散在全文的硬约束在此收敛一处，各阶段执行前引用，避免遗漏：
- **破折号统一 `--`**：给读者的文字里所有破折号用两个英文连字符，禁全角 `——`。
- **不编造**：案例 / 数字 / 数据照实；拿不到的据实留空，不制造假精度、不臆造 URL（外链必须真实可点）。
- **版权线**：直接引用原文 ≤150 字并明示出处；连续 30 字与原文雷同即改写。
- **强制 checkpoint**：CP1 智能默认 + CP5（CP5-A 预览 → CP5-B 增强）必走，不跳过；明确意图用户可走提速通道。
- **等待期不弹窗**：仅被动文本预览，绝不 `AskUserQuestion`。
- **确定性优先**：转写 / 排版 / 导出 / 截图等能用脚本确定性完成的，交给 `bilinote.py`，不交 LLM 自由发挥。
- **质量门禁**：交付前必过「📋 质检摘要」（硬门禁 + 冷读外审），不过不交付。

### ⏳ 等待期能力预览（预处理 · 一次性 · 被动）

**触发时机**：agent 发起 `run` / `summarize` 后，若识别为**长等待源**（视频需转写、或远程抓取/下载耗时），在等待管线产出简报期间，**被动输出一次**能力预览。
短等待源（纯文本 / 本地文档 / 命中缓存）不触发——没有那个等待窗口，硬塞反而打扰。

**为什么做**：转写 / 抓取是用户唯一真正"干等"的时段，注意力空闲、无任务压力，是展示"后面能做什么"的最佳窗口。首次用户尤其受益。

**规则（铁律）**：
- 🚫 **绝不在等待期弹 `AskUserQuestion`**——只输出纯文本预览。
- 🔁 单次运行只展示一次，不重复。
- ⏱️ 非阻塞：不拖慢 / 打断管线；管线极快完成则不补发。
- 🎯 措辞必须明确"稍后我会问你 / 现在不用选"，与 CP5 区分开。

**预览文案模板（agent 在等待期输出，两阶段角色化叙事）**：
```
⏳ 正在处理《{视频标题}》…（完成后自动继续，无需你操作）

第一阶段 · 转写中：
  🎙️ 转写师 · 正在把音频提取成文字（bcut 引擎，预计 60–90 秒）
  📸 摄影师 · 同步采集 {n} 个关键帧备用

{仅长视频/系列内容触发：}
第二阶段 · 并行精读中（长内容才启用，省时间）：
  🧠 架构师 · 正在抽取核心框架与思维模型
  📝 案例官 · 正在整理案例与数据
  📖 术语官 · 正在标引关键概念
  💎 金句官 · 正在摘录可独立引用的亮点

完成后自动进入风格预览，不用你操作。笔记出来后我会先给你看 4 种风格的真实样例，你直接选方向即可：
  🎨 视觉化 ：信息图 E4 · 网页PPT E5 · 思维导图 mindmap
  ✍️ 文本增强：去AI味 E6（24 类扫描+50分评分卡）· 质量闸审阅 review
  📱 社媒卡  ：一键生成小红书图文卡 / 公众号封面（零 key，见 E9）
  📦 分发多产：一源多产 produce（多平台 / 成品包）
  📄 导出排版：PDF · Word · 公众号排版 E8
  🔗 系列合集：同主题多期内容 → 自动归并成一个系列目录

💡 小贴士：先想清楚这份内容"最终去哪、给谁看"——发小红书→留意社媒卡(E9)；发公众号→留意 E8；汇报→留意 PPT(E5)；严谨→留意审阅(review)。
```

> 与 CP1 Step 3（轻量确认）和 CP5（主动决策）构成**三段式触达**：① 起飞前轻确认 → ② 等待期被动菜单 + 类型推荐 → ③ 生成后主动决策（CP5-A 预览 → CP5-B 增强）。

---

### 🚀 提速通道（明确意图时 · 可选绕过 CP1/CP5）

若用户在**首条消息**中已明确表达「风格 + 扩展」意图，agent 直接按意图执行，绕过 CP1 与 CP5 的逐个询问，零等待直达成品。

**Step 1 — 首条消息语义解析（agent 强项，无需代码改动）**

| 用户说法 | 解析为 |
|---------|--------|
| 小红书 / 种草 / 口播 / 爆款笔记 | `--style xiaohongshu`，默认 +E3+E6 |
| 公众号 / 推文 / 长文 | `--style wechat`，默认 +E6+E8 |
| 教程 / 课件 / PPT / 学这个 | `--style tutorial`，默认 +E5 |
| 学术 / 论文 / 引用 | `--style academic`，默认 +E2+mindmap |
| 商业 / 研报 / 分析 | `--style business`，默认 +E4+E2 |
| 会议纪要 / 访谈 | `--style meeting`，默认 +mindmap |
| 信息图 / 图解 / 一页 | 扩展 +E4 |
| 导图 / 思维导图 | 扩展 +mindmap |
| 去AI味 / 人味儿 / 别像AI | 扩展 +E6 |
| PPT / 演示 / 汇报 | 扩展 +E5 |
| 多平台 / 分发 / 矩阵 | 扩展 +produce |
| 公众号排版 | 扩展 +E8 |

**Step 2 — 安全阀（轻量确认，不走 CP1+CP5）**

识别到明确意图后，agent 仅做一次确认，不展开 CP1/CP5 全流程：

```
"你要的是【{风格} + {扩展}】，对吗？确认后我直接出成品。"
```

- 用户确认 → 直接 `run --style <style> <采集flag> --out <out>` → 产出符合意图的成品 → 交付（仍可走 S7 后续建议）。
- 用户修改 / 意图模糊 → 退回标准 CP1 → CP5 流程。

> **与标准流程关系**：提速通道是「专家/明确意图」用户的快捷路径，不改变默认用户的 CP1 → CP5 体验。两者共用同一套产物链路。

---

### 🔴 CHECKPOINT 1 — 管道前置决策（智能默认 · 生成前）

**v2.0 变更（S2）**：CP1 彻底弃用 `AskUserQuestion` 询问"采集哪些原料"。改为**智能默认**——agent 按输入类型自动套用最优采集组合，纯文本告知用户"将顺手采集 X/Y"，用户说"不用/取消"即可。
这同时解决了两个历史问题：① CP1 过于技术化（用户看不懂参数）→ 改为产出导向的告知；② 管线-视觉断裂（用户 CP5 想用截图但 CP1 没采）→ 默认全采，CP5 视觉选项不再空壳。

**Step 1 — 按输入类型应用智能默认采集（无需询问，直接告知）**

各源默认规则（`classify_source` 决定）：

| 输入类型 | 默认采集 flag | 说明 |
|---------|--------------|------|
| B站视频 | `--danmaku` + `--screenshots` | 弹幕热词 + 4 张抽帧截图 |
| YouTube | `--comments` | 高赞评论与锐评 |
| 抖音 / 快手 | `--screenshots` | 抽帧截图 |
| article_url | `--images` | 抓取原文配图 |
| 外语视频 | 追加 `--translate` | 译中文要点 |
| 本地文件 / 纯文本 | 无默认 | 直接转写/总结 |

agent 输出（纯文本，**非询问**）：
```
📺 已识别为 B站视频，将顺手抓取弹幕热词 + 4 张关键帧截图以丰富笔记。
   不需要的话说一声即可。
```

**Step 2 — 注入 run 命令**

agent 把默认 flag 连同 `--style concise` 注入 `run` 命令（如 `run URL --style concise --danmaku --screenshots --out <out>`）。用户要求取消某项 → 去掉对应 flag 即可。

**Step 3 — 一句话确认（指向 CP5 预览）**

```
⏳ 开始抓取/转写。生成后我会先给你看 4 种风格的真实样例，你选一个方向即可。
```

> **设计原则**：CP1 零摩擦——默认采集、告知、可取消，绝不弹 AskUserQuestion 询问参数。用户快速通过 → 等待转写（期间展示等待期能力预览 + 内容推荐）→ agent 写 concise 草稿 → **CP5-A 风格预览 → CP5-B 渐进增强**。

---

### 🔴 CHECKPOINT 2 — 视频截图嵌入确认（条件触发）

**触发条件**：简报（brief.md）第 7 条或第 10 条包含：
- 字符串 `*Screenshot-[mm:ss]*`（截图占位标记），**且**
- 存在有效的 `<video_path>` 或可下载的视频 URL

**Step 1 — 前置检查**

```bash
# 检查 ffmpeg 是否可用
which ffmpeg 2>/dev/null || echo "ffmpeg_not_found"
```

| 检查结果 | 处理 |
|---------|------|
| `ffmpeg` 可用 | 继续 Step 2 询问用户 |
| `ffmpeg` **不可用** | 跳过询问，直接告知用户："未检测到 ffmpeg，无法嵌入截图。笔记保留 `*Screenshot-[mm:ss]* 占位标记。如需嵌入截图，请先安装 ffmpeg（`apt install ffmpeg` / `brew install ffmpeg`）后重跑 `embed-screenshots`" → 跳至笔记生成 |

**Step 2 — 向用户询问**

```
AskUserQuestion:
  question: "简报中检测到 *Screenshot* 截图占位标记。是否从视频抽取帧嵌入笔记？"
  header: "截图"
  options:
    - label: "是，嵌入截图"
      description: "需要用 ffmpeg 从视频抽帧（约需 5-30 秒），生成后笔记会出现真实画面"
    - label: "否，保留占位"
      description: "保留 *Screenshot-[mm:ss]* 文字标记，不额外占用时间"
  multiSelect: false
```

**Step 3 — 分支执行**

| 用户回答 | 执行步骤 |
|---------|---------|
| **同意嵌入** | ① 在笔记中保留 `*Screenshot-[mm:ss]*` 标记<br>② 写入 note.md 临时版本<br>③ 运行 `python scripts/bilinote.py embed-screenshots --note note.md --video <video_path> --out note.md`<br>④ 检查 `screenshots/` 目录是否生成了对应帧文件<br>⑤ 成功 → 最终 note.md 中标记变为 `![screenshot at mm:ss](screenshots/xxx.jpg)` |
| **不同意** | 保留原始 `*Screenshot-[mm:ss]*` 占位标记，直接跳至笔记生成。不运行 embed-screenshots |
| **误选（无 video_path 但用户选了"嵌入"）** | 告知"未找到视频路径，无法嵌入截图"，保留占位标记 |

> 💡 **提示**：截图只展示视频画面。如果视频内容偏抽象（架构/流程/理论），截图帮助有限——笔记生成后可用「小黑手绘配图」补充图解。

---

### 🔴 CHECKPOINT 3 — 原文配图嵌入确认（条件触发）

**触发条件**：同时满足以下两项——
1. 输入类型为 `article_url`（非视频 / 非纯文本）
2. 简报第 9 条包含「原文包含 N 张配图」+ 有效的 URL 列表

> **不触发的情况**：
> - 输入是 video_url / media_file → 跳过
> - 输入是 doc_file / text → 跳过
> - 文章 URL 但 `--images` 未启用 → 跳过
> - 简报第 9 条未列出任何配图 URL → 跳过

**Step 1 — 向用户询问**

```
AskUserQuestion:
  question: "文章原文检测到 {N} 张配图。是否抓取并嵌入笔记？"
  header: "配图"
  options:
    - label: "是，嵌入配图"
      description: "将从原文 URL 下载图片到 images/ 目录，笔记中出现真实图片（约需 5-60 秒）"
    - label: "否，纯文字"
      description: "不插入任何图片标记，纯 Markdown 文字笔记"
  multiSelect: false
```

**Step 2 — 分支执行**

| 用户回答 | 执行步骤 |
|---------|---------|
| **同意嵌入** | ① 在笔记内容合适位置插入 `*Image-N*` 标记（第 1 张配图在第一次引用处插入 `*Image-1*`，以此类推）<br>② 写入 note.md 临时版本<br>③ 运行 `python scripts/bilinote.py embed-article-images --note note.md --images '<URL 列表 JSON>' --out note.md`<br>④ 成功 → 标记变为 `![图N](images/img_NN.jpg)`<br>⑤ 如部分图片下载失败 → 告知"第 X、Y 张图片下载失败（可能防盗链），已保留文字标记" |
| **不同意** | 不插入任何 `*Image-*` 标记，直接生成纯文字 note.md |

---

### 🔴 CHECKPOINT 4 — 浏览器 Cookie 抓取确认（被墙时触发）

**触发条件**：`fetch` / `run` 返回网络错误，具体表现为：
- 错误信息含 `Connection refused` / `403` / `404` / `timeout` / `名称解析失败`
- 目标站点为 B站 / YouTube / 抖音 / 快手等可能受区域限制的平台
- **排除**：URL 格式错误、404 页面、视频不存在（非网络问题）

> **CP4 与管线时序关系**：
> CP4 **不是在 brief.md 生成后触发**——它在管线更早的 `fetch` 阶段发生。
> 如果 CP4 最终无法解决，管线不会继续生成 brief.md，而是直接返回错误。

**Step 1 — 一线修复（自动执行，不询问）**

```bash
# 检查是否有代理环境变量
if [ -n "$BILINOTE_PROXY" ] || [ -n "$HTTPS_PROXY" ]; then
  # 代理已设置但 fetch 仍失败 → 跳到 Step 2
else
  # 尝试使用系统代理重试（仅一次）
  # 重试失败 → 跳到 Step 2
fi
```

**Step 2 — 向用户询问**

```
AskUserQuestion:
  question: "⚠️ 无法从 {平台名} 下载视频（CDN 被墙/连接超时）。是否从本地浏览器抓取 cookie 重试？"
  header: "网络"
  options:
    - label: "是，抓取 cookie"
      description: "仅在本地读取浏览器 cookie 文件，不上传任何数据。需要你先登录过该网站的浏览器"
    - label: "否，跳过"
      description: "改为传本地已下载的视频文件（需手动提供）"
  multiSelect: false
```

**Step 3 — 分支执行**

| 用户回答 | 执行步骤 |
|---------|---------|
| **同意抓取 cookie** | ① 告知隐私声明："本操作仅在本地读取浏览器 cookie 文件，不会上传/分享任何 cookie"<br>② 检测本地浏览器路径（按以下顺序检查）：<br>`%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies`<br>`%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cookies`<br>`%APPDATA%\Mozilla\Firefox\Profiles\*.default\cookies.sqlite`<br>③ 找到任一 → 设置环境变量 `BILINOTE_YTDLP_COOKIES=<浏览器名>` → 重试 fetch<br>④ 找不到任何浏览器 cookie → 告知"未检测到已登录的浏览器" → 引导传本地文件（见下方） |
| **不同意** | 告知用户："已跳过 cookie 抓取。" → 引导传本地文件 |
| **无浏览器 cookie** | 同上 |

**Step 3b — 兜底引导**（用户不同意 / 无 cookie 时通用）

```
告知用户：
  "已跳过 cookie 抓取。建议：手动下载视频后传本地文件运行：
   python scripts/bilinote.py run ./my_video.mp4 --out note.md
   （支持 mp4 / mkv / flv / mov / webm 等格式）"
```

> ⚠️ **隐私与安全硬性规则（CP4 专用）**：
> - 抓取前**必须先赢得用户明确同意**，不可默认勾选或静默抓取
> - 必须告知用户"本操作仅在本地读取文件，不会上传/分享任何 cookie"
> - 不可设 `BILINOTE_YTDLP_COOKIES` 为某个固定浏览器路径——必须用户同意后再检测
> - 反例 #12 在「What NOT to do」表中明确禁止未经同意的 cookie 读取

---

### 🔴 CHECKPOINT 5 — 最终形态中枢（所见即所选 · 生成后 · 交付前必走）

**v2.0 升级（S4 + S5）**：从 v1.3.0 的"4 组标签盲选"升级为**四风格并行预览 + 渐进式增强**——
用户不再根据标签猜产出，而是先看到 4 种风格的真实样例，再选最喜欢的方向；选定后，增强选项按风格动态过滤，只展示最相关的。

**为什么需要（核心洞察）**：v1.0→1.3 的所有迭代都在优化"怎么让用户选得更精准"，但根上的问题始终是——**用户永远在选一个标签**。"社交平台分发"对应小红书体还是 B站脚本体？用户终究在猜。v2.0 的解法是：让用户看到四种真实产出，再选他最喜欢的那个。这是从"根据标签选"到"看到产出再选"的质变。

> **设计原则**：锦上添花，不强制。CP5-A 多选 + 默认全否；CP5-B 按风格过滤后多选 + 默认全否。一轮问完绝不追问。

#### CP5-A — 风格预览与选定（生成后第一步）

**Step 0 — Profile 检测（v2.1 双路径分流）**

agent 先读 `~/.bilinote/profile.yaml`：
- **存在且合法** → 走「Profile 轻量确认路径」（仅 1 次弹窗）。
- **不存在** → 走「标准四预览路径」（Step 1-4，同 v2.0.1）。

**Profile 轻量确认路径**
直接展示用户偏好风格的**完整预览**（非 4 版），并一句确认：
```
📎 检测到你的风格偏好：{default_style}（+{enhance 列表}）
这篇也按这个来？
```
```
AskUserQuestion:
  - question: "你的偏好是「{default_style} + {enhance}」，这篇也这样出？"
    header: "风格"
    options:
      - label: "就按这个来"
        description: "直接应用你的默认风格 + 增强链，跳过风格预览与增强选择"
      - label: "换风格看看"
        description: "回到 4 种风格完整预览，重新挑方向"
```
- **就按这个来** → 按 Profile 默认应用（风格改写 `default_style` + 增强链 `enhance`）→ 跳到「📋 质检摘要」→ 交付（**全程仅此 1 次弹窗**）。
- **换风格看看** → 落入下方标准四预览路径。

**标准四预览路径（无 Profile / 换风格用户）**

**Step 1 — agent 并行生成 4 版真实风格预览**

concise 草稿产出后、询问用户前，agent 取草稿前 3-4 句关键内容，**同时生成 4 版真实改写**（非标签，是真实开头）：

```
🔥 社交平台 · 小红书种草
  🚨 48小时被掏空3759块！网恋奔现踩坑全记录
  姐妹们注意了💔 他在交友平台认识「日落等你回来」，第二天就赴金华见面……

📊 专业表达 · 商业简报
  案例速览 | 2026.07 · 婚恋诈骗单案
  损失: ¥3,759+ | 来源: 思化交友平台 | 手法: 小额高频诱导消费

⚡ 效率工具 · 精简速查
  TL;DR: 31岁船舶工两天内被以恋爱为名诱导消费¥3,759，警方定性"感情纠纷"。
  识破关键: 快速奔现 + 高频小额要钱

🎭 叙事体验 · 费曼讲解
  想象你在酒吧遇到一个朋友，他说"我前两天差点被骗了"——这个故事教你识别一种经典骗术……
```

**Step 1.5 — 可选视觉缩略图卡片（迭代3 · 长内容触发 · CP5-A 四预览 → 视觉看板）**

> **触发条件**：源为视频且时长 >20 分钟，或笔记将走 E3 配图（用户预览前已声明要手绘/信息图）。短内容默认不触发，零额外开销。
> **原则**：锦上添花、不强制、不改变 Step 3 选择逻辑。仅作预览增强，用户不选不影响交付。

为让用户在"看文字样例"之外还能"看视觉方向"，agent 在 4 版文字预览基础上，**额外生成 1 张合成缩略图卡片**（纯文本描述的"视觉看板"，不调用 ImageGen、零 API Key、零渲染器依赖）：

```
🖼️ 视觉方向速览（缩略图·非成品）
  [封面主视觉] 大字标题卡 + 1 个核心图标意象（如 ⚠️危机 / 🔄循环 / 📈曲线）
  [内页配图] 预计 2–4 张，图型：{流程 / 架构 / 对比 / 关系 / 结构 / 概念}
  [配色基调] 小红书=暖橙活力 / 商业=蓝灰克制 / 费曼=手绘暖黄
```

这张卡片只回答"视觉长啥样"三件事——**主视觉意象、配图数量与图型、配色基调**。用户据此可提前说"配图太多 / 想要更克制 / 换图标意象"，避免 E3 出图后再返工。它**不消耗**真实出图预算（不调 ImageGen），纯描述，属于 CP5-A 预览的视觉延伸。

**Step 2 — 内容推荐（S6-full）+ 展示预览**

展示预览前，agent 先给一句基于**已读内容**的推荐（比等待期的标题推测更准确）：
```
💡 内容分析：{类型}。我推荐「{风格组}」，因为 {理由}；当然你也可以选别的。下面是 4 种风格的真实样例——
```

**Step 3 — 询问（multiSelect）**

```
AskUserQuestion:
  - question: "4 种风格的真实样例如上，选你最喜欢的方向？（可多选 = 出多份）"
    header: "风格"
    multiSelect: true
    options:
      - label: "🔥 社交平台·小红书"
        description: "种草/口播/爆款体，四段式结构 + 标签"
      - label: "📊 专业表达·商业"
        description: "简报/研报体，数据突出 + 结构化"
      - label: "⚡ 效率工具·精简"
        description: "速读/速查体，TL;DR + 关键清单"
      - label: "🎭 叙事体验·费曼"
        description: "讲解/故事体，有人味儿、好懂"
```

**Step 4 — 分支**
- 单选 → agent 按该风格**完整改写** note.md（小红书/商业/精简/费曼各自的具体规范）；若选社交平台且想多平台，则走 `produce` 多平台
- 多选 → 走 `produce` 多份 / 多平台输出
- 全不选 → 保留 concise 草稿，直接进入 CP5-B（仅增强与输出，无风格改写）

#### CP5-B — 渐进式增强与交付（生成后第二步）

> **Profile 轻量确认路径短路**：CP5-A 中选「就按这个来」的用户已按 Profile 默认增强链（`enhance`）出成品并直接进「📋 质检摘要」，**不进入本步、不弹本步**。本步仅服务于标准四预览路径 / 换风格用户。

**Step 1 — 按已选风格动态过滤（S5）**

仅展示该风格最相关的增强，消除"与当前选择无关"的选项噪音：

| 已选风格 | 视觉选项 | 增强选项 | 输出选项 |
|---------|---------|---------|---------|
| 社交平台·小红书 | 手绘配图 / 信息图 / 嵌入截图(已采) | 去AI味 / 公众号排版 / 质量审阅 | 公众号 / PDF / 思维导图 |
| 专业表达·商业 | 数据引用 / 信息图 / 思维导图 | 去AI味 / 网页PPT / 质量审阅 | PDF / Word / 思维导图 |
| 效率工具·精简 | 思维导图 / 信息图 | 去AI味 / 质量审阅 | PDF / Word / 思维导图 |
| 叙事体验·费曼 | 手绘配图 / 信息图 / 嵌入截图(已采) | 去AI味 / 网页PPT / 质量审阅 | 公众号 / PDF / 思维导图 |
| 全不选(保留concase) | 全部视觉项 | 全部增强项 | 全部输出项 |

> 全部用大白话描述产出，不暴露 `E3/E4/E8` 这类内部代号（与 CP5-A 人话语感一致）。
> 多风格并集 → 取各行并集展示。具体风格规范见「集成扩展能力」与 `--style` 取值表。

**Step 2 — 询问（2 问，依风格过滤后的选项）**

```
AskUserQuestion:
  # Q1 · 视觉丰富度（按上表过滤，全部用大白话）
  - question: "要不要给笔记加点视觉元素？（可多选，也可跳过）"
    header: "视觉"
    multiSelect: true
    options:
      - label: "🖼️ 信息图"
        description: "把关键手法/数据做成一页图解，适合警示传播"
      - label: "🧠 思维导图"
        description: "时间线 + 结构梳理，适合速查/汇报"
      - label: "🎨 手绘配图"
        description: "小红书/费曼版补手绘风插图，更有感染力"
      - label: "📸 嵌入视频截图"
        description: "你前面采的关键帧，直接嵌进笔记画面"
  # Q2 · 增强与输出（合并，按上表过滤，全部用大白话）
  - question: "内容增强 + 输出形式？（可多选，也可跳过）"
    header: "增强·输出"
    multiSelect: true
    options:
      - label: "✍️ 去AI味（含换模型审稿）"
        description: "改写得更像人写的、少点机器腔；完成后会换一个独立审稿视角冷读一遍，确保不像 AI 写的"
      - label: "📝 公众号排版"
        description: "按微信推文样式美化，直接能发"
      - label: "📱 生成社媒卡片"
        description: "一键产出小红书 3:4 图文卡 + 公众号 21:9 封面，直接能发，零 key 本地运行（见 E9）"
      - label: "📄 导出 PDF / Word"
        description: "生成可下载/转发的文档"
      - label: "📚 做成系列合集"
        description: "同主题多期笔记自动归并成系列目录，方便追更和统一导出（例：「婚恋警示录」合集）"
```

> 术语对照（内部用，用户无需知道）：🖼️信息图=E4 · 🎨手绘配图=E3 · ✍️去AI味=E6 · 📝公众号排版=E8 · 📄导出=export · 📚系列合集=series。
> 如需更多增强（质量审阅 review、网页PPT E5 等），用户直接说即可，不必塞进这 4 个选项。

**Step 3 — 分支执行（顺序 = E7 规范）**

```
风格改写(CP5-A) → E2/E3 回修流水线(如需) → E4 信息图(如需) → mindmap(如需)
                → E6 去AI味(如需) → review 质量闸(如需) → E5 PPT(如需)
                → E8 公众号排版(如需，先 E6 再 E8) → PDF/Word/导图/series
```

> 先 E6 再 E8；先改风格再叠加；导出与排版在最后。

**Step 4 — 交付 + 后续建议（S7）**

返回最终产物路径 + 已应用增强清单；若无任何选中，直接交付初始 concise 笔记。
交付后按 S7 给出后续操作建议（见「Checkpoint 完成后的收尾动作」Step 7）。

#### 📋 质检摘要（交付前必过 · 无弹窗 · v2.1 新增）

> 借鉴 sansheng-distill 的**硬门禁（exit-code gating）** 与 sansheng-write 的**冷读外审 subagent**：把"交付前质量把关"从一句口头自检收敛为可复核的三层卡点。纯被动卡片，**绝不 `AskUserQuestion`**；仅在卡片里如实列出结果，通过即定稿交付。

**触发时机**：CP5-B 执行完（或 Profile「就按这个来」短路后），**交付前**无条件执行一次。

**三层卡点（agent 自检 + 必要时调用 subagent）**：

1. **硬门禁（P0 · 铁律总纲逐条过）**：agent 对照「📌 铁律总纲」逐条机检，列出每项的 通过 / 未过：
   - 破折号是否含全角 `——`（应全为 `--`）
   - 是否有编造 URL / 假精度数字（外链须真实可点）
   - 直接引用是否 ≤150 字且明示出处
   - 确定性任务（转写/排版/导出/截图）是否走了 `bilinote.py` 而非 LLM 自由发挥
   - 等待期是否误弹了 `AskUserQuestion`
   - （E6 去AI味）评分合计 ≥40（仅当应用了 E6 时检查；未达标强制回修、不交付）
2. **冷读外审（P1b · 仅当应用了 E6 去AI味时）**：另起一个**不同模型族**的 subagent（确保语义视角与正文生成解耦），仅喂成品让其冷读，输出：① 判定"像不像 AI 写"（是/否 + 置信度）；② 最多 3 条可改点。agent 据其吸收微调后定稿——这正是「去AI味（含换模型审稿）」承诺的审稿环节。
3. **跨笔记索引（P2 · 仅当本篇属于某 series 合集时）**：更新 `~/.bilinote/knowledge-index.json`，追加本篇（标题 + 一句话定位 + 路径 + 合集名），供后续 series 模式自动聚合目录、统一导出。

**卡片输出模板（被动文本，无弹窗）**：
```
📋 交付检查清单（质检摘要 · 迭代2）
  ✅ 硬门禁（铁律逐条）：
     · 破折号全为 `--` / 版权线合规 / 不编造 / 确定性任务走脚本 / 等待期未误弹窗 — 全部通过
     · 🆕（E6）去AI味评分：47/50 ≥40 ✅（未应用E6则跳过）
  🔍 冷读外审（已去AI味）：判定"不像AI写"；微调 1 处口语化
  🔎 来源追溯： [原文] 12 · [检索] 5 · [推断] 3（已降权）
       ⚠️ "2026 行业增速预测" 标 [推断] → 建议补充检索
  🔴 CHECKPOINT 6：数据可信度不足暂停（[推断]≥3 或金融类数据无 [检索]）→ 已暂停询问
  📚 系列索引：已并入「婚恋警示录」合集（共 3 期）
  → 定稿交付 ✓（可信度：高）
```
未过项须先修再交付（铁律：不过不交付）；无 series 不显示第 5 行；来源追溯/CHECKPOINT 6 行仅在 review 报告存在时显示；`quality-gate` 子命令可对该清单做确定性复核。

---

### 🔴 CHECKPOINT 6 — 数据可信度不足暂停（条件触发 · 迭代2新增）

> 借鉴 hk-ipo-pro 的「四级可信度 + CHECKPOINT 暂停」与 jd-analyzer 的「评分纪律」：当笔记关键论断的来源可信度不足时，**不默默交付，而是暂停**让用户决策。

**触发条件**（质检摘要阶段判断，或 `quality-gate --review` 自动判定）：
- review 报告中 `[推断]` 标签 ≥ 3 项；**或**
- 笔记类型为金融/研报，且存在数据主张未经 `[检索]` 交叉验证（仅 `[原文]` 口述或 `[推断]`）。

**动作（暂停交付，不自动放行）**：展示可信度不足项清单，询问用户三选一：
- 「继续交付（以当前可信度）」——用户知情同意
- 「补充检索后再交付」——agent 重新 WebSearch / 金融数据源核实
- 「降级标记为草稿」——文件名加 `-draft`，不计入 series 合集

**不触发时**：正常走定稿交付，检查清单不显示本行。

---

### 📑 按类型反例黑名单（review pre-flight · 迭代2新增）

> review 出报告前，先按笔记类型逐条核对以下黑名单；命中的即为必须修的问题（对应 REVIEW_INSTRUCTION 的「反例黑名单 pre-flight」小节）。

| 笔记类型 | 反例黑名单（命中即须修） |
|---------|------------------------|
| **金融/研报类** | ① 单一数据源未交叉验证 ② 未标注数据时间戳 ③ 基准标签未闭环验证 ④ 仅凭视频口述数据未检索核实 |
| **学术/严肃类** | ① 引用无出处 ② 连续 30 字与源文本雷同未改写 ③ 编造 URL |
| **配图类** | ① 相似卡片/盒子超过 3 个未抽象化 ② 单一模块体积超画面 20% ③ 缺原文指纹 |
| **通用** | ① 破折号含全角 `——` ② 外链不可点 ③ 直接引用超 150 字 |

借鉴来源：hk-ipo-pro（17 条反例黑名单 D1-D17）、excess-return-backtest（不凭单源下结论）、article-metaphor-illustrator（重复审美测试/眯眼平衡）。

---

### Checkpoint 完成后的收尾动作

所有适用 CP 完成后，按以下顺序收束：

1. **记录用户选择**：在日志中简要记录，如"管线(智能默认): B站→弹幕+截图；CP5-A: 社交平台·小红书；CP5-B: 视觉=配图+信息图, 增强=E6, 输出=E8+PDF"
2. **生成初始 note.md**：agent 根据简报（transcript + rule）+ `concise` 风格（通用草稿），撰写 Markdown 笔记并写入 `<out>`
3. **执行 CP5-A（风格预览）**：展示 4 版真实风格样例（见「CHECKPOINT 5 · CP5-A」），agent 依内容推荐一方向，用户选定（可多选 = 多份）
4. **执行 CP5-B（渐进增强）**：按选定风格动态过滤增强选项（见「CHECKPOINT 5 · CP5-B」），用户选定后按 E7 顺序执行；风格改写走 `produce` 或 agent 直接 rewrite
5. **进入「📋 质检摘要」门禁**（见上）：CP5-B 完成后先过 硬门禁 +（如含 E6）冷读外审 +（如 series）跨笔记索引更新，通过才定稿。
6. **返回 `<out>` 路径与已应用的增强清单**：
   ```
   ✅ 已生成笔记：D:\notes\video_note.md
       风格: 小红书(社交平台) | 增强: 配图(E3)+信息图(E4)+去AI味(E6) | 导出: E8+PDF
   ```
7. **后续操作建议（S7，主动给出）**：agent 依内容类型给一句"下一步"入口，引导持续使用：
   - 社会新闻/案例类 → "这类手法反复出现，要不要拉一个「XX警示录」系列？"
   - 教程/教学类 → "若这是系列课程第1节，可设系列目录自动聚合"
   - 测评/商业分析 → "同类产品还有 X/Y/Z，要不要批量跑对比？"
   - 其他 → 不强行建议
8. （历史路径）若在 CP5 之外用户另行要求 `--export pdf,docx`，亦可用 `export` 命令补出

The following failure modes are encoded as **three-column rules** (trigger →
primary fix → final fallback). When a failure occurs, follow this table
**top-to-bottom**; do not skip steps.

| # | 触发条件 | 一线修复 | 仍失败兜底 |
|---|---------|---------|-----------|
| F1 | `fetch` 无法下载（CDN 被墙 / 连接超时 / 区域受限 / 被代理拦截） | 一线修复：检查代理环境变量（`BILINOTE_PROXY`/`HTTPS_PROXY`）并重试；若仍失败 → **询问用户**是否从本地浏览器抓取 cookie 重试：<br>**用户同意** → 检测本地浏览器（Chrome/Edge/Firefox）→ 自动设置 `BILINOTE_YTDLP_COOKIES` 环境变量重试<br>**用户不同意 / 无浏览器 cookie** → 引导用户传已下载好的文件：`run <本地文件路径>` |
| F2 | `fetch` 下载了字幕但内容全空或乱码 | 丢弃坏字幕 → 降级走 `transcribe` | 同 F1 兜底 |
| F3 | `transcribe` 主引擎 (如 bcut) 返回非中文但目标语种是中文 | 自动切到另一引擎重试（**agent 须主动告知用户"主引擎返回异常，已自动切换另一引擎重试"**，让用户知道系统在努力、避免"为何这么慢"的疑问） | 两引擎交叉结果仍对不上 → **向使用者报告**两版差异，让使用者选择 |
| F4 | `transcribe` 返回空转写（0 段 / 全空白） | 换引擎重试（**agent 须主动告知"上一引擎返回空，已换引擎重试"**） | 所有引擎返回空 → **告知使用者**"音频可能损坏或完全静音" |
| F5 | `embed-screenshots` 找不到 `ffmpeg` | 检查 PATH；若缺失 → 未安装 | 保留 `*Screenshot-[mm:ss]*` 占位标记，告知使用者"未安装 ffmpeg，需手动安装后重跑 embed-screenshots" |
| F6 | `embed-article-images` 某个图片 URL 下载失败 | 跳过该 URL，继续下载其他图片 | 所有图片均失败 → 保留 `*Image-N*` 文字标记，告知使用者"图片下载失败，可能防盗链" |
| F7 | 输入 URL 含追踪参数或重定向到 404 | `fetch` / `scrape_article` 跟随重定向一次 | 最终返回非 200 → **告知使用者**"URL 无效或已失效" |
| F8 | `classify_source` 返回 `unknown`（路径存在但不是任何已知类型） | 尝试作为纯文本读取 | 读取返回空 → **告知使用者**"无法识别输入类型，请确认是 URL / 文件路径 / 纯文本" |
| F9 | `summarize` 在 agent-native 模式下生成 <out> 但未生成 `.brief.md` | 重跑 `summarize` 一次 | 仍失败 → **告知使用者**"生成失败，可能 transcript 为空" |
| F10 | agent 误以为脚本会直接产出最终 `note.md`（已移除 API 直出模式） | 脚本在 agent-native 模式只写 `<名>.brief.md` 简报，不写最终笔记 | 告知使用者"已切换为原生模式，请读 `.brief.md` 由当前 LLM 补全 note.md" |

> **HL-2 杠杆**：以上 10 条覆盖了管线所有已知失败场景。若遇到未列出的
> 异常，**必须先告知使用者，再采取任何行动**——静默跳过是反模式。

### Step-by-step (when more control is needed)
1. `fetch` — download audio + subtitles, print a JSON with paths/metadata:
   ```bash
   python scripts/bilinote.py fetch "URL" --workdir ./work
   ```
2. `transcribe` — only if no subtitle was obtained:
   ```bash
   python scripts/bilinote.py transcribe ./work/audio.mp3 --backend kuaishou --out transcript.txt
   ```
3. `summarize` — transcript → Markdown note:
   ```bash
   python scripts/bilinote.py summarize --transcript transcript.txt \
       --title "视频标题" --tags "tag1, tag2" --out note.md
   ```

### Export an existing note (`export`)
Convert a finished `.md` note into PDF and/or Word without re-running the
pipeline. Markdown headings, bullet/numbered lists, bold/italic/code and code
blocks are preserved.
```bash
python scripts/bilinote.py export note.md --formats pdf,docx
# --out BASE to control output path (default: note name without .md)
```
The same `--export pdf,docx` flag works on `run` and `summarize` to emit the
extra files in one step.

### Embed screenshots into an existing note (`embed-screenshots`)
Turns `*Screenshot-[mm:ss]*` markers in a finished note into real frames pulled
from the video. Needs `ffmpeg`.
```bash
# local video:
python scripts/bilinote.py embed-screenshots --note note.md --video ./video.mp4 --out note.md
# or let it download the video first:
python scripts/bilinote.py embed-screenshots --note note.md --url "VIDEO_URL" --out note.md
```
Images are written to `screenshots/` next to the note; markers become
`![screenshot at mm:ss](screenshots/...jpg)`. In `run`, `--embed-screenshots`
does this automatically right after the note is produced (it also enables
`--screenshots` and downloads the video). On the agent-native path the
agent asks the user first, then runs this command (video path is recorded in
the brief).

### Embed article images into an existing note (`embed-article-images`)
Turns `*Image-N*` markers in a finished note into the N-th image downloaded
from the supplied URL list (for article / web-page input). No `ffmpeg` needed.
The image list is the one printed in the brief (rule 9) when `run` is given
`--images`.
```bash
# images as a JSON array, or comma-separated URL string:
python scripts/bilinote.py embed-article-images --note note.md \
    --images '["https://.../a.png","https://.../b.png"]' --out note.md
```
Images are written to `images/` next to the note; markers become
`![图N](images/img_NN.jpg)`. Only indices actually referenced by `*Image-N*`
in the note are downloaded (others are ignored, so you can pass the full list
and reference only the relevant pictures). On the agent-native path the
agent asks the user about image embedding first (per the decision checklist
above), then runs this command.

## Key behaviors to preserve

- **Subtitle priority**: if a `.vtt` subtitle exists, skip transcription. This
  is the core cost/time saving — never transcribe when subtitles are available.
- **Faithful note format**: the note prompt lives in `references/note_prompt.md`
  and is loaded verbatim by the script. Keep its `{video_title}`, `{tags}`,
  `{segment_text}` placeholders and the "no code-block wrapping / avoid ordered-
  list misrender" rules intact. Conditional blocks (time markers, screenshots,
  AI summary) are appended by the script based on flags.
- **Transcript format**: every line is `mm:ss - text`. Parsed VTT and online
  ASR results both conform to this so the LLM sees consistent "开始时间 - 内容".

## What NOT to do (anti-patterns / blacklist)

This section lists actions the agent **must not** take. Violating any of these
reduces output quality, wastes tokens, or breaks the skill's core contract.

| # | Anti-pattern | Why not | What to do instead |
|---|---|---|---|
| 1 | **Run `summarize` when a subtitle is available** | Wastes time & tokens; subtitle is ground-truth | Subtitle goes straight to `summarize` — only `transcribe` when no `.vtt` exists |
| 2 | **Transcribe audio without trying subtitles first** | Breaks the core cost-saving guarantee | Always `fetch` (which prefers `.vtt`) before any `transcribe` call |
| 3 | **Use `--screenshots` for non-video inputs** | Screenshot markers depend on media duration — meaningless for text/PDF | `--screenshots` only works on video/media file input; skip entirely for `article_url` / `doc_file` / `text` |
| 4 | **Call `embed-screenshots` when the user said no** | Wastes ffmpeg cycles and disk; disrespects user choice | Only run `embed-screenshots` after the user explicitly opts in to screenshot extraction |
| 5 | **Generate PDF/DOCX when the user asked for Markdown only** | Unnecessary export overhead | Default to `.md` only; export to pdf/docx/mindmap only when user requests it (or when `--export` is passed) |
| 6 | **Assume `--transcriber auto` works for all languages** | bcut/kuaishou handle ja/ko well but may struggle with rare languages | For languages outside zh/en/ja/ko, ask the user or force `--lang` explicitly |
| 7 | **Ignore the brief and write the note from scratch** | The brief contains the exact rules + transcript — ignoring it produces inconsistent output | Read `<out>.brief.md` first and follow the rules listed inside |
| 8 | **Use local Whisper / MLX / Groq transcribers** | These engines have been **removed** from the skill | Only `bcut` and `kuaishou` remain; if both fail, surface the error to the user |
| 9 | **Wrap the note in a code block (`` ```markdown ``)** | The note prompt explicitly forbids this — it breaks Markdown render | Output raw Markdown; never wrap it in fenced code blocks |
| 10 | **Proceed when `fetch` returns empty transcript** | Empty input always produces empty/garbage output | Stop and tell the user the video is paywalled, region-blocked, or has no extractable content |
| 11 | **反复重试被墙的 CDN** | 被墙就是被墙，重试浪费 30 秒 + 用户耐心 | 第 1 次 fetch 失败 → 直接询问用户"是否抓取本地浏览器 cookie 重试" → 不同意/无 cookie → 引导用户传本地文件 |
| 12 | **未经用户同意抓取浏览器 cookie** | cookie 是敏感凭证，必须用户明确授权才读取 | fetch 被墙时先问"是否抓取 cookie" → 用户同意后才检测浏览器（Chrome/Edge/Firefox） |
| 13 | **把官方 AI 总结当唯一真相照抄** | 官方 AI 总结可能漏点/含幻觉，且长视频只覆盖部分 | #0 仅作**参考区**：以转录为准、AI 总结为辅，交叉印证后再落笔 |
| 14 | **把弹幕原文抄进正文** | 弹幕多为梗/情绪，噪声大 | #1 弹幕仅用于判断高能片段与观点热度，不作为正文事实来源 |
| 15 | **在没有 Cookie 时反复调官方 AI 总结** | 未登录必返回 `code=-101`，重试无意义 | #0 一次失败即回退字幕优先/转写；提示用户配 `--bili-cookie`/`BILINOTE_BILI_COOKIE` |
| 16 | **对 B 站视频依赖外网 SponsorBlock 数据** | 其众包库以 YouTube 为主、B 站几乎无数据，硬等必空 | #4 已改用 B 站原生方案：弹幕关键词聚簇检赞助段 + LLM 内容自判断跳过片头/片尾/广告，不依赖外网库 |
| 17 | **linkify 后再嵌截图顺序反了** | linkify 只处理 `*Content-*`/裸 `[mm:ss]`，保留 `*Screenshot-*`；但若先改坏结构会影响 | 先 `embed-screenshots` 再 `linkify`，或反之皆可（两者互不干扰），但不要手改标记格式 |

> This blacklist is **exhaustive, not suggestive**. If you are unsure whether an
> action is allowed, check this table first. If it's not listed above AND not in
> the "How to use" section, ask the user before proceeding.

## References

- `references/note_prompt.md` — the exact note-generation prompt (source of
  truth used at runtime).
- `references/platforms.md` — per-platform fetch notes (Bilibili cookie needs,
  Douyin/Kuaishou fallbacks, local video).
- `references/config.md` — environment variables (style/cookies/proxy), proxy, and
  the explicit note that RAG is excluded.

## Notes / limitations

- This skill does NOT include BiliNote's RAG chat-QA, vector store, or
  Function-Calling retrieval — by design.
- PDF and Word export are implemented with pure-Python libraries
  (`markdown-pdf` / `python-docx`), so no LaTeX or Microsoft Office install is
  required. Notion export remains out of scope (still an upstream TODO).
- BCut transcription follows a reverse-engineered API and may need an updated
  cookie/User-Agent.
- For region-restricted platforms, export a browser cookies file and pass it,
  or set `HTTP_PROXY` / `HTTPS_PROXY`.
- All yt-dlp download calls (audio, subtitles, and video-for-screenshots in
  `run` when `--screenshots`/`--multimodal`, and `embed-screenshots --url`)
  pick up two optional env vars via `_ytdlp_extra_opts()`, mirroring upstream
  BiliNote's browser-cookie sync + global proxy. The screenshot-stream quality
  is set by `--video-quality` {720,1080,best} (default 720); 1080p/best only
  resolve when login cookies are supplied (see `BILINOTE_YTDLP_COOKIES` below):
  - `BILINOTE_YTDLP_COOKIES` — browser name (`chrome`/`edge`/`firefox`) to read
    cookies from. Login-state cookies select reachable Bilibili CDN mirrors
    that are often blocked for anonymous requests (fixes "connection refused"
    / "requested format not available" on restricted networks).
  - `BILINOTE_PROXY` (or `HTTPS_PROXY` / `HTTP_PROXY`) — outgoing proxy for
    downloads. When unset, no `--proxy` flag is added (default behaviour).
  - The video format selector was loosened from `best[ext=mp4]/best` to
    `b[ext=mp4]/b` so a download succeeds even when a single combined mp4
    stream is unavailable.

### 视频富化增强（#0–#5）的限制与要点

- **#0 官方 AI 总结**：调用 `x/web-interface/view/conclusion/get`，需 **WBI 签名**
  （脚本内置 `_wbi_sign`，已用官方参考向量校验通过）。**未登录返回 `code=-101`**，
  绝大多数视频需要含 **SESSDATA** 的 Cookie（`--bili-cookie` 或 `BILINOTE_BILI_COOKIE`）。
  返回 `data.code=1` 表示"未识别到语音/无总结"，`=-1` 表示"敏感不支持" → 均自动回退。
  命中后 **AI 字幕直接作转写来源（免下载音频/ASR）**，大纲用于截图时间点与简报参考区。
- **#1 弹幕**：优先现代 protobuf 分段接口 `x/v2/dm/web/seg.so`（按 6 分钟/段迭代，用
  duration 定段数），失败回退旧版 `comment.bilibili.com/{cid}.xml`。protobuf 解析为
  **零依赖手写 wire-format 解析器**（progress=field2、content=field7）。部分视频弹幕稀少甚至为 0。
- **#2 抽帧建议**：优先级 **官方大纲章节起点 > 弹幕密度峰值(15s 分桶) > 均匀采样**；
  无 duration 且无大纲/弹幕时返回空（不阻塞）。
- **#3 linkify**：B 站/多数站点用 `?t=秒`，YouTube 用 `?t=Ns`；**保留 `*Screenshot-*` 标记**。
  原生模式下待 agent 写出 note.md 后再运行 `linkify` 子命令。
- **#4 内容净化（替代 SponsorBlock）**：不调用外网 `sponsor.ajay.app`（B 站无数据）。两层实现：① **弹幕信号**——抓弹幕后用 `恰饭/广告/种草/赞助/带货` 等关键词按 25s 聚簇成疑似赞助区间（`detect_sponsor_segments_from_danmaku`）；② **LLM 内容自判断**——简报/提示词注入「内容净化」规则，要求跳过片头口播、片尾 CTA、赞助广告口播。弹幕检出的疑似赞助区间仅列为参考，由 agent 在生成笔记时跳过（保留 agent 判断空间，不做转录行物理删除）。`--no-clean` 可整体关闭。
  - **回归测试参考（实网验证）**：视频 `BV15b42177rL`（何同学，2213 条弹幕）用 `clean --url` 自动抓弹幕→检测→去行，正确命中两段赞助区间 `[[311.115,326.115],[639.882,654.882]]`（05:11–05:26 / 10:39–10:54），触发弹幕典型为「本视频由阿范赞助播出」。物理去除 4 行恰饭口播（05:13/05:20/10:42/10:50），正常内容（00:30/02:15/08:40/15:00/18:20）完整保留。验证脚本与样例见 `bilinote_clean_verify.md` / `clean_demo_transcript.txt` + `.cleaned.txt`，可作为改动弹幕检测逻辑后的回归基准。
- **#5 翻译**：由 LLM 在生成阶段完成（提示词/简报注入规则），非独立 API。
- 所有增强器均为**可选、失败安全**：任一不可用都不影响「字幕优先 → 转写」核心链路。

### Multimodal / Mindmap / Export

| 功能 | 触发 | 成本 | 不做什么 |
|------|------|------|---------|
| **多模态视觉理解** | `--multimodal` | +N帧 base64 token | 不嵌入截图（用 `--embed-screenshots`） |
| **思维导图** | `--export mindmap` | 零 | 从 H1-H6 提取 Mermaid，不开 LLM |
| **格式多选** | 原生简报交互 | 零 | 默认只生成 .md |

**`--multimodal` 抽取 N 帧（默认 6）→ 送 LLM 看图 → 但笔记里不会自动插入截图**。要截图改用 `--embed-screenshots` 或 `embed-screenshots`。

> **Removed:** fast-whisper / mlx-whisper / groq 已移除。仅 bcut / kuaishou 可用。

## 长视频并行提取（cangjie 模式 · 迭代3·生产力加速）

> 借鉴 cangjie-skill 的「5 个 sub-agent 并行提取 + 三重验证」：长视频/系列内容不再串行空等，改为并行抽取后汇合。

**触发条件**（由 `classify_source()` 判断视频时长自动路由）：
- 长视频（>20 分钟）/ 系列内容 / 学术讲座 → 触发并行
- 短视频（<10 分钟）→ 不触发（开销不划算）

**流程**：转写完成后，agent 并行派出 5 个提取角色（可由主 agent 一次性生成 5 段提示，或 spawn 5 个 subagent）：
- 🧠 架构师：核心观点框架与思维模型
- 📝 案例官：案例与数据
- 📖 术语官：关键词与概念定义
- 🛡️ 反例官：被反驳/警告的观点
- 💎 金句官：可独立引用的金句

汇合后生成 concise 草稿（含框架/案例/术语预结构化）。

**三重验证（V1+V2+V3 全过才进正文，仅 V1 进「补充参考」，其他丢弃）**：
- V1 跨域复现：内容在视频中 ≥2 个独立段落出现？
- V2 预测力：能用它回答视频未明说的相关问题？
- V3 独特性：不是任何同类视频都说的泛泛之谈？

**铁律**：并行仅影响 summarize 阶段的草稿生成；CP1–CP5 决策体系不受影响，不并行弹窗。

---

## 中断恢复与 session（迭代3·生产力加速）

> 借鉴 jd-analyzer 的失败模式表与「状态可恢复」思想：交付后记录本次会话，用户后续改风格/配图/去味时零重抓。

**记录**：交付完成后，agent 把本次选择写入 `<note_dir>/.bilinote_session.json`：
```json
{
  "source": "<输入 URL 或路径>",
  "style": "xiaohongshu",
  "enhance": ["E3", "E6", "E8", "E9"],
  "timestamp": "2026-07-12T13:00:00",
  "files": {
    "note": "<note.md>",
    "illustrations": "<assets/...>",
    "humanized": "<note-humanized.md>",
    "social_cards": "<social-cards/>"
  }
}
```

**恢复**：用户说"把这篇换个风格 / 换个配图 / 换一种去AI味"时，agent 读取 session，从缓存恢复上下文，直接改目标、零重抓（结合现有 cache 机制）。

**注意**：session 仅作本地恢复提示，不含敏感凭证；用户可随时删除该文件。

---

## 集成扩展能力（内置，直接执行）

以下 7 项扩展能力（E1–E8，其中 E7 为调用优先级说明）+ 导出已**物理合并**到 bilinote-skill 中。触发后 agent 直接按本文档规则执行，
**不再调用外部 Skill**。CP1 智能默认采集 + CP5（笔记生成后，见 CHECKPOINT 5：CP5-A 风格预览 + CP5-B 渐进增强）集中决策这些能力。

**执行优先级**：配图（嵌入阶段）→ note.md 定稿 → 去AI味/信息图/PPT（后处理）→ 公众号排版 E8（最终排版，最后一步）

---

### E1. 浏览器自动化（输入增强 · 自动触发）

**触发**：`scrape_article()` 返回空正文 + 页面需要 JS 渲染（SPA / 动态加载）

**操作步骤**：
1. 确认目标 URL 的页面类型（检查 HTML 是否含 `<div id="root">` / `<div id="app">` 等 SPA 标志）
2. 使用 `browser-use` 工具打开页面：
   ```bash
   browser-use open <URL>
   ```
3. 等待页面渲染完成（检查关键内容是否出现）：
   ```bash
   browser-use state
   ```
4. 提取页面正文：
   ```bash
   browser-use text
   # 或获取完整 HTML 后用 trafilatura 提取正文
   browser-use html
   ```
5. 将提取的正文传递给 `summarize` 流程

**规则**：
- 默认 headless 模式，不弹出浏览器窗口
- 如需登录态，询问用户是否使用 `--headed` 模式手动登录
- 提取后关闭浏览器会话：`browser-use close`

---

### E2. 研究写作辅助（输入增强 · 用户主动触发）

**触发**：用户说"补充资料"/"加引用"/"找相关研究"/"加来源"

**操作步骤**：
1. **理解补充需求**：向用户确认——补充哪个方面？需要什么类型的来源（学术论文/新闻/数据）？
2. **检索来源**：使用 `WebSearch` 搜索相关可信来源，提取事实/数据/引文
3. **组织补充内容**：按"引用格式"组织——`> 来源标题 (作者, 年份)。URL`
4. **注入笔记**：将补充内容作为"延伸阅读"或"参考来源"章节追加到 note.md 末尾
5. **告知用户**：列出补充了哪些来源，用户可选择保留或删除

**规则**：
- 优先选择权威来源（学术期刊、官方报告、知名媒体）
- 每条引用必须包含可访问的 URL
- 补充内容与笔记主体用 `---` 分隔，标注「延伸阅读」
- 不可编造来源——检索不到就告知用户

---

### E3. 手绘配图生成（笔记撰写阶段 · 统一配图子流程）

**触发**：用户说"配图"/"加配图"/"画个图"，或 agent 在笔记撰写中发现适合配图的段落

**路由判断**：根据内容类型自动选择配图风格

| 内容类型 | 配图风格 | 视觉特征 |
|---------|---------|---------|
| 抽象概念/技术架构/认知转折 | **小黑 IP 手绘**（ian-xiaohei 风格） | 纯白背景、黑线稿、少量红橙蓝批注、大量留白 |
| 流程/对比/关系/结构 | **结构化极简配图**（article-metaphor 风格） | 极简强线条、橙白圆猫 IP、图型优先于风格 |

**🆕 构思卡关卡（迭代3·配图科学化 · 强制前置）**：
> 借鉴 article-metaphor-illustrator 的「构思卡 + 八项测试」与 ian-xiaohei 的「shot-list 单认知锚点」：配图不再凭运气，先过脚本化构思卡，全过才进 ImageGen。

1. **跑脚本建构思卡**：`python scripts/bilinote.py illustration-plan <note.md> [--max-cards 4]`，产出 `<note>.illustration-plan.md`——脚本自动：建段落地图、6 图型关键词识别、选 2–4 候选配图位、每张出关键字段（插入位置 / 图型 / 单一命题 / 原文指纹 / 信息单位 / 重复预算）。
2. **八项测试（脚本跑可判部分）**：一秒（主语可识别）/ 三秒（可独立判断）/ 换文（不泛化）/ 删减（信息单位≤5）/ 图型（图型匹配）/ 无文（脱离长标签可懂）/ 重复审美（无机械阵列）/ 眯眼平衡（重量均衡）。视觉重量、阅读顺序两项主观测试由 agent 在简报中补。
3. **回退规则**：任一 `❌` 项 → 重选锚点 / 换图型 / 精简信息单位后重测；连续 2 次未过则降级为纯文字 + 标注「建议配图：<命题>」而非强行出图。
4. **进 ImageGen**：全部 ✅ 才调 ImageGen；路由沿用上方两条 IP 风格（小黑手绘 / 极简强线条），**两条风格都要先过构思卡**，区别只在提示词模板。

**通用操作步骤**：
1. **识别配图点**：扫描笔记内容，找出"认知锚点"——核心判断/断点/闭环/分流/对比
2. **向用户确认**：展示候选配图点，例："检测到以下段落适合配图：①TCP三次握手流程 ②负载均衡架构。是否生成？"
3. **用户同意** → 逐张生成
4. **生成图片**：使用 `ImageGen` 工具，按选定的配图风格构建提示词

**小黑 IP 手绘提示词规则**：
- 必须包含：16:9、纯白背景、黑色线稿、少量红/橙/蓝批注、大量留白
- 必须包含：小黑（简笔小人）参与核心动作
- 禁止：PPT风格、商业插画、可爱风、复杂架构图、左上角标题、水印
- QA检查：小黑是否装饰化？是否太满？是否像PPT/流程图？中文是否过多？背景是否干净白底？

**结构化极简配图提示词规则**：
- 先判断图型：流程图 / 架构图 / 对比图 / 关系图 / 结构图 / 概念插图
- 图型优先于风格——先确定"这张图要表达什么结构关系"，再定视觉
- 必须包含：极简强线条、橙白圆猫 IP 角色
- 每张图只承担一个任务：解释 / 区分 / 转折 / 记忆 / 收束
- 通过眯眼平衡测试（闭眼半秒再睁眼，第一眼焦点是否正确）

**配图数量**：短文 1-2 张，长文 3-4 张，最多 8 张

**嵌入方式**：生成后保存到 `assets/<note-slug>-illustrations/`，按 `01-topic.png` 命名，在笔记对应位置插入 `![配图说明](assets/01-topic.png)`

---

### E4. 信息图生成（输出增强 · note.md 完成后）

**触发**：用户说"信息图"/"生成信息图"/"一页图解"/"知识卡片"

**操作步骤**：
1. **内容分析**：从 note.md 中识别核心主题，提取 3-7 个关键点（优先奇数个）
2. **构建视觉隐喻**：为每个关键点匹配具体的视觉隐喻（例：缓存→快递柜、负载均衡→交警分流）
3. **检测语言**：匹配 note.md 的语言（中文笔记→中文信息图）
4. **构建提示词**：
   ```
   主题：{核心主题}
   标题：{笔记标题}
   分点：
   1. {关键点1} — 视觉隐喻：{隐喻1}
   2. {关键点2} — 视觉隐喻：{隐喻2}
   ...
   风格约束：手绘卡通风格，16:9横向，{色调}，{布局类型}
   ```
5. **生成图片**：使用 `ImageGen` 工具，尺寸 `1536x1024`，高质量模式
6. **审查迭代**：检查——主题是否突出？关键点是否可辨？文字语言是否正确？手绘风格是否一致？
7. **保存**：输出到 `note-infographic.png`，与 note.md 同目录

**规则**：
- 关键点数量 3-7 个，优先奇数（视觉平衡更好）
- 每个关键点必须有独立的视觉隐喻，不可纯文字罗列
- 如有著名人物，需标注名字
- 迭代最多 2 次，仍不满意则告知用户可手动调整

---

### E5. 网页PPT生成（输出增强 · note.md 完成后）

**触发**：用户说"PPT"/"生成PPT"/"做演示文稿"/"做幻灯片"

**操作步骤**：
1. **需求澄清**（首次使用时询问）：
   - 风格：A. 电子杂志 × 电子墨水（衬线+流体背景+暖色） / B. 瑞士国际主义（无衬线+网格点阵+高亮色）
   - 受众/场景：内部分享 / 外部演示 / 发布会
   - 时长：15分钟≈10页，30分钟≈20页，45分钟≈25-30页
2. **大纲规划**：按"钩子→定调→主体→转折→收束"叙事弧搭建骨架
3. **内容适配**：从 note.md 提取核心内容，按页分配
4. **生成 HTML**：生成单文件 HTML 横向翻页 PPT
5. **保存**：输出到 `note-presentation.html`，与 note.md 同目录

**规则**：
- 单文件 HTML，不依赖外部资源（CSS/JS/图片全部内联）
- 横向翻页交互（左右箭头 / 触摸滑动）
- 图片/截图约定：保存到 `ppt/images/`，命名 `{页号}-{语义}.{ext}`，≥1600px，总量 <10MB
- 如用户无图片素材，用纯文字+排版+色彩传达信息
- 生成前必须对齐叙事弧+页数规划+主题节奏，不可直接动手生成

---

### E6. AI痕迹去除（输出增强 · note.md 完成后）

**触发**：用户说"去AI味"/"太AI了"/"改自然一点"/"humanize"

**操作步骤**：
1. **扫描 24 类 AI 模式**（本地 `humanize --scan-only` 覆盖正则可检子集，语义类由 LLM 自查）：

| # | AI 模式 | 表现 | 修复方法 |
|---|--------|------|---------|
| 1 | 过度强调意义 | "这标志着…的重要里程碑" | 删除或替换为具体事实 |
| 2 | 过度强调知名度 | "广受好评的""备受瞩目的" | 删除修饰语，让事实说话 |
| 3 | 肤浅分析铺垫 | "值得注意的是…""值得一提的是…" | 直接说结论，不加铺垫 |
| 4 | 宣传性语言 | "革命性的""颠覆性的""前所未有的" | 用具体数据替代 |
| 5 | 模糊归因 | "专家表示""业内人士认为" | 补充具体来源或删除 |
| 6 | 破折号滥用 | 每段都有 `—` / 全角 `——` | 减少 70%，正文统一用 `--` |
| 7 | 三段式法则 | "第一…第二…第三…" | 打破为自然段落，混合句长 |
| 8 | AI 英文词汇 | " delve / leverage / navigate / robust" | 用日常表达替代 |
| 9 | 否定式排比 | "不是…而是…不是…而是…" | 改为肯定句 |
| 10 | 连接短语堆砌 | "此外""然而""因此""与此同时" | 减少 50%，用标点代替 |
| 11 | 系动词回避 | "这意味着""这表明""体现出" | 删连接词，直接给结论 |
| 12 | 刻意换词同义循环 | "换言之""换句话说" | 保留一处即可，其余删 |
| 13 | 虚假范围 | "从 X 到 Y 的跨越" | 用具体区间替代空泛表述 |
| 14 | 协作交流痕迹 | "希望这对您有帮助" | 删客套尾句 |
| 15 | 知识截止免责 | "作为 AI""我的知识截止" | 删除免责声明 |
| 16 | 谄媚语气 | "您真聪明""很高兴为您" | 保持平视，去奉承 |
| 17 | 标记符号滥用 | 无意义加粗 / emoji / 弯引号 | 去掉装饰性标记 |
| 18 | 模板化开场 | "在当今""随着…的发展" | 删空泛起手 |
| 19 | 绝对化论断 | "一定""必然""毫无疑问" | 改为有依据的限定表述 |
| 20 | 冗余程度副词 | "非常""极其""十分" | 用事实强度本身 |
| 21 | 伪深刻反问 | "难道…？" | 反问改陈述判断 |
| 22 | 总结词套话 | "综上所述""总而言之" | 一句话收束 |
| 23 | 空洞量词 | "众多""大量""一系列" | 改为可数或具体比例 |
| 24 | 数据夸张 | "数倍""井喷""飙升" | 改为精确数字 |

2. **出 50 分评分卡（改写后自评，五维各 10 分）**：

| 维度 | 权重 | 评分要点 |
|---|---|---|
| 节奏 | 10 | 长短句交替，无机械 15 字句 |
| 真实性 | 10 | 有观点不骑墙，敢下判断 |
| 信任度 | 10 | 无谄媚、无知识截止免责声明 |
| 直接性 | 10 | 无铺垫词、无模板化开场 |
| 精炼度 | 10 | 无冗余副词、无空洞量词 |

> 分档：45–50 优秀 / 35–44 良好 / <35 需重写。**迭代 2 起，<40 分将接入「📋 质检摘要」硬门禁（不交付）**；迭代 1 仅展示评分，不拦截。

3. **报告检测结果**：告知用户"检测到以下 AI 模式：宣传性语言 ×2、三段式结构 ×1、否定式排比 ×1；改写后评分卡 47/50（优秀）。是否修复？"
4. **用户同意** → 逐条修复
5. **注入灵魂**：
   - 有观点——不要骑墙，该下判断就下
   - 变化节奏——长短句交替，不要每句都是 15 字
   - 承认复杂性——"这个问题没有标准答案"比"综上所述"真诚
   - 适当用"我"——"我认为""我觉得"在合适场合出现
   - 允许不完美——口语化的"其实""说白了"可以保留
6. **对比展示**：修复完成后告知具体修改（例："将'综上所述'改为'一句话总结'"），并附改写前后评分卡：
   ```
   改写前评分：32/50（节奏 4/10 · 真实性 6/10 · 信任度 7/10 · 直接性 8/10 · 精炼度 7/10）
   改写后评分：47/50 ✅（优秀）
   主要降分项：系动词回避 ×3、虚假范围 ×1
   ```
7. **输出**：覆盖 note.md 或另存为 `note-humanized.md`（询问用户偏好）

**规则**：
- 保持核心信息完整——去 AI 味不是删内容
- 匹配原文预期语调——学术风格不该改成口语
- 不可引入新的 AI 模式——修复本身不能产生 AI 痕迹
- **评分卡可审计**：每个降分项须能回溯到具体原文段落，不能"凭感觉打低分"
- **评分卡须落盘**：改写后把评分卡（合计行必须保留）附在笔记末尾一并写入目标文件，供 `quality-gate` 确定性门禁解析；未落盘视为评分缺失、门禁不通过

---

### E7. 扩展能力调用优先级与时机

> **入口**：E4/E5/E6/E8 在交互流程中由 **CHECKPOINT 5（最终形态中枢）** 的 Q2-Q4 集中呈现，用户可一次性多选后按本表顺序执行。风格选择（Q1）走 `produce` 改写链路；E2/E3 为输入/撰写阶段触发，CP5 不主动干预但支持用户随时手动要求（回修流水线）。

| 管线阶段 | 可用扩展 | 触发方式 |
|---------|---------|---------|
| fetch / scrape | E1 浏览器自动化 | 自动（scrape 为空时） |
| scrape 后 / summarize 前 | E2 研究写作辅助 | 用户主动 |
| 笔记撰写中 | E3 手绘配图生成 | 用户主动 / agent 建议 |
| note.md 定稿后 | E4 信息图生成 | 用户主动（CP5 集中呈现） |
| note.md 定稿后 | E5 网页PPT生成 | 用户主动（CP5 集中呈现） |
| note.md 定稿后 | E6 AI痕迹去除 | 用户主动（CP5 集中呈现） |
| note.md 定稿后 | E8 公众号排版美化 | 用户主动（CP5 集中呈现） |
| note.md 定稿后 | E9 零 key 社媒卡发布 | 用户主动（CP5 集中呈现） |

**多扩展同时触发时的顺序**：
```
E2（补充资料）→ E3（配图嵌入）→ note.md 定稿 → E6（去 AI 味）→ E4/E5（图/PPT）→ E9（社媒卡，可并行）→ E8（公众号排版，最后一步）
```
> E8 产出的是可直接粘贴进公众号的内联 HTML，属于"定稿后的最终排版"，因此永远放在后处理链末尾；若同时需要去 AI 味（E6），务必先 E6 再 E8。E9 社媒卡与 E8 互补（短卡 vs 长文），可并行生成，不互相依赖。

---

### E8. 公众号排版美化（输出增强 · note.md 完成后）

把定稿的 `note.md` 一键转成**可直接粘贴进微信公众号编辑器**的内联 HTML，排版理念借鉴开源项目 **[gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)**（作者：甲木 × 摸鱼小李，协议 AGPL-3.0）。本技能仅重实现其排版"理念"，不复制其代码。

**触发**：用户说"排成公众号"/"公众号排版"/"排版美化"/"生成公众号 HTML"/"能贴到公众号吗"

**借鉴的核心排版理念**：
- **克制用色**：主色只在锚点出现（≤5 处），白底 + 灰阶（#111827→#9CA3AF）承载约 90% 文字
- **灰阶承重**：正文 #374151、次要 #6B7280、辅助 #9CA3AF，层次靠深浅不靠颜色
- **章节自动编号**：H2 自动编号 `01 / 02 …`，最后一章标 `∞`；≥2 个 H2 自动生成"目 录"卡
- **引言卡**：首段自动转为浅灰引言卡片
- **关键词标记**：`**加粗**` 渲染为浅色底关键词高亮（每段 1–3 处为宜）
- **小标签而非虚线框**：H3+ 用左竖条 / 药丸标签，不用 dashed border 方框
- **全内联 + `<span leaf="">`**：禁用 `<style>/<script>/<div>/class/id/position:fixed|absolute|sticky/float/grid/@media/@keyframes`，所有样式内联，文字包 `<span leaf="">` 以规避公众号编辑器过滤
- **中文全角标点**：正文半角 `,;:!?()` 自动转全角（代码块内保持原样）
- **署名条**：文末自动附"排版风格借鉴 gzh-design-skill"署名，尊重原作者

**操作步骤**：
1. 确认 note.md 已定稿（若需去 AI 味，先执行 E6）
2. 运行转换：
   ```bash
   python scripts/bilinote.py gzh <note.md 路径> [--theme <主题>] [--title "封面标题"] [--out <输出.html>]
   ```
   - `--theme` 可选：`moyu-green`（默认·摸鱼绿）/ `red-white`（红白）/ `graphite`（石墨灰）/ `zen`（禅意）/ `ink-blue`（墨蓝）/ `olive`（橄榄）
   - `--title` 不填则取首个 H1 或文件名
   - `--out` 不填则输出到同目录 `<名>.gzh.html`
3. 用浏览器打开生成的 HTML，点页面顶部『复制到公众号』按钮
4. 直接粘贴进微信公众号编辑器 —— 样式全部内联，粘贴后即所见即所得
5. **合规自检**（可选）：`python scripts/bilinote.py gzh <note.md> --lint` 只校验可粘贴正文是否含禁用标签、是否全内联，不产文件

**规则**：
- 只对"可粘贴正文片段"做禁用标签校验；预览页外壳（含复制按钮）允许 div/style，但**不会被粘贴**
- 代码块内保持半角标点与原始缩进，不做全角转换
- 主色锚点数量克制，避免全篇高亮失去重点
- 输出务必保留文末署名条，遵守 AGPL-3.0 对来源的尊重

---

### E9. 零 key 社媒卡发布（输出增强 · note.md 完成后 · v3.0 迭代 1 新增）

把定稿的 `note.md` 变成**可直接发小红书 / 公众号的图文卡**，补齐"笔记→发布"的最后一公里。零 API Key、零外部依赖——不绑定任何第三方服务，不要求 html-anything 安装即可用。

**触发**：用户在 CP5-B 选「📱 生成社媒卡片」/ 说"生成社媒卡"/"出小红书图"/"公众号封面"

**产物形态**：
| 平台 | 产物 | 形态 |
|------|------|------|
| 小红书 | 3:4 竖版图文卡组（封面 + 每节一张，5–9 张） | 自包含 HTML（浏览器打开截图即发） |
| 公众号 | 21:9 主封面 + 1:1 方封面 成对 | 自包含 HTML |
| 知乎 / X | 当前复用小红书卡内容，专属模板迭代 3 补 | 同左 |

**操作步骤**：
1. 确认 note.md 已定稿（若需去 AI 味，先 E6）
2. 运行生成：
   ```bash
   # 独立入口
   python scripts/social_card.py --note <note.md> [--platforms xiaohongshu,wechat] [--png]
   # 或经统一入口
   python scripts/bilinote.py social-card --note <note.md> --png
   ```
   - 产物落 `<note_dir>/social-cards/`（`xiaohongshu/` + `wechat/` + `index.html` 索引）
   - `--png`：探测到 `playwright` / `wkhtmltoimage` 时自动栅格化为 PNG；无渲染器则仅出 HTML（零依赖兜底）
3. 用浏览器打开 `social-cards/index.html`，逐张截图即可发平台；或打开对应 HTML 直接截图

**与 E8 的关系**：E9 负责"社媒图文卡 + 封面"（短平快、一图一观点），E8 负责"公众号长篇推文排版"（长文、目录卡、引言卡）。两者互补不替代。

**与 html-anything 的关系（可选后处理）**：html-anything 是本地优先、零 key 的 agentic HTML 编辑器（Next.js 应用，75 模板，一键导出微信/X/知乎）。E9 的卡片若要更精致的版式，可在 html-anything 内打开 `social-cards/*.html` 继续微调——但 E9 本身**不依赖**它，核心路径纯零依赖。

**规则**：
- 卡片文字须来自 note.md 的真实标题/要点，**不得编造**观点或数据（遵守铁律·不编造）
- 每张卡片只讲一个点，避免信息过载
- 中文排版须清晰（字号 ≥32px、行高 ≥1.5），截图后手机端可读
- 若 `--png` 栅格化失败，退回 HTML 路径并告知用户，不阻断交付

---

## 版本记录（Changelog）

> 本技能此前无版本标识（非 git 仓库、frontmatter 无 `version` 字段、代码无 `__version__`），无法自报版本，也不发布于技能市场（BuiltinMarket）。自 **1.0.0** 起引入版本管理，使"是否最新版"可被追溯。

### 2.4.0 — 2026-07-12（迭代 3 · 生产力加速 · 渐进版方案落地）

- **E3 配图科学化（方案 D · 构思卡 + 八项测试）**：配图从"凭感觉抽锚点"升级为**脚本化构思卡**——
  - 新增 `illustration-plan` 子命令（`scripts/bilinote.py`）：扫描 note.md 建段落地图 → 识别 6 类图型（流程/架构/对比/关系/结构/概念）→ 选 2–4 候选配图位 → 每张出构思卡（插入位置/图型/配图任务/单一命题/原文指纹/信息单位/重复预算）→ 跑八项测试（一秒/三秒/换文/删减/图型/无文/重复审美/眯眼平衡）→ 写 `<note>.illustration-plan.md` 简报交 agent。
  - 八项测试脚本可判部分确定性输出 pass/warn/fail；**全过才建议进 ImageGen**，未过项标注回退建议（重选锚点/换图型/精简信息单位），消除"同文跑三次配图偏差大"。
  - §E3 升级：新增「🆕 构思卡关卡（强制前置）」四步（跑脚本 → 八项测试 → 失败回退 → 进 ImageGen）。
- **长视频并行提取（cangjie 五路并行 · 迭代3）**：视频 >20 分钟触发，5 角色（架构师/案例官/术语官/金句官/反例官）并行精读，V1/V2/V3 三重校验收敛；铁律：不改 CP（笔记主体结构）只补分角色视角，并行是加速非改写。
- **中断恢复与 session（迭代3 · 交互升级 4.3）**：运行时写 `.bilinote_session.json`（源/风格/增强/已产文件），中断后零重抓恢复；隐私说明：仅记本地路径与选用项，不含抓取内容。
- **CP5-A 视觉看板（迭代3 · 交互升级 4.2）**：长内容触发"可选视觉缩略图卡片"——纯文本描述的视觉方向速览（主视觉意象/配图数量与图型/配色基调），不调 ImageGen、零开销，提前对齐视觉避免 E3 返工。
- **自测试体制（test-prompts）**：新增 `references/test-prompts.json`，20 条回归用例（应成功/应拒绝/边界），覆盖 run/social-card/quality-gate/illustration-plan/review 等子命令的预期行为与拒绝边界，供 `lint_skill.py` 之外的功能回归。
- 配套：`scripts/lint_skill.py` 校验（目标 0 错误 0 警告）；端到端样例回归（含 `illustration-plan` 多段笔记）。

### 2.3.0 — 2026-07-12（迭代 2 · 质量收口 · 渐进版方案落地）

- **质量收口（方案 C + 方案 B 剩余）**：review 从"软判断"升级为"可审计"——
  - `REVIEW_INSTRUCTION` 升级：新增「笔记类型判定 + 反例黑名单 pre-flight + 来源追溯小结」三节；每项判定须标 `[原文]`/`[检索]`/`[推断]`，`[推断]` 权重自动 ×0.5。
  - 新增《📑 按类型反例黑名单》章节（金融/学术/配图/通用 四套 pre-flight 清单）。
  - 新增 **CHECKPOINT 6 — 数据可信度不足暂停**：`[推断]`≥3 或金融类数据无 `[检索]` 时暂停交付，三选一决策（继续/补充检索/降草稿）。
  - 质检摘要卡片升级为「交付检查清单」：硬门禁第 6 条 = E6 去AI味评分 ≥40（应用 E6 时）。
- **E6 评分接入硬门禁**：`<40` 分不交付，先回修；评分卡须随改写后笔记落盘（末尾合计行），供脚本解析。
- **新增 `quality-gate` 子命令**（`scripts/bilinote.py`）：确定性门禁——解析 E6 评分卡合计 + 重扫残留 AI 痕迹（≥6 类或 ≥12 处判偏机器腔）+ 解析 review 来源标签，输出 PASS/FAIL 或 `--json`。无外部依赖，复用 `scan_ai_patterns`。
- 配套：E6 简报规则要求 LLM 把评分卡写进 humanized 笔记末尾。

### 2.2.0 — 2026-07-12（迭代 1 · 产出收口 · 渐进版方案落地）

- **新增 §E9 零 key 社媒卡发布（产出收口核心）**：把定稿 note.md 变成可直接发小红书/公众号的图文卡，补齐"笔记→发布"最后一公里。新增 `scripts/social_card.py`（纯标准库、零 API Key、零外部依赖），产出 `<note_dir>/social-cards/`（小红书 3:4 卡组 + 公众号 21:9 封面 + 1:1 方封面 + index.html 索引）；`--png` 可选栅格化（探测 playwright/wkhtmltoimage），无渲染器则留 HTML（零依赖兜底）。不绑定 html-anything，但可借其做精致后处理。
- **E6 升级为 24 类扫描 + 50 分评分卡**：`AI_PATTERNS` 从 10 类正则扩展至 24 类（新增系动词回避/虚假范围/协作痕迹/知识截止/谄媚/标记滥用/模板开场/绝对化/冗余副词/伪反问/总结套话/空洞量词/数据夸张等 14 类）；`humanize` 改写简报新增五维（节奏/真实性/信任度/直接性/精炼度各 10 分）评分卡，改写前后对比可审计。
- **等待期能力预览升级为两阶段角色化叙事**：转写师/摄影师（第一阶段）→ 架构师/案例官/术语官/金句官（长视频并行精读，第二阶段），与"笔记专家团"叙事一脉相承，仍严守"等待期不弹窗"铁律。
- **CP5-B Q2 新增「📱 生成社媒卡片」选项**：与 E9 联动，用户一键勾选即出可发物料。
- **E7 调用表 + 多扩展顺序补 E9 行**；E9 与 E8 互补（短卡 vs 长文），可并行生成。
- **迭代 1 范围说明**：仅做产出收口 + 评分卡（不含硬门禁）；E6 <40 分接入「📋 质检摘要」硬门禁、review 可追溯、E3 构思卡、并行提取等留待迭代 2/3（见 `bilinote-优化方案.md` §5.2）。

---

### 2.1.0 — 2026-07-12（方案三 · Profile 双路径 + 质检摘要门禁）

- **方案三落地（用户「动工方案三」批准）**：融合 sansheng-distill 与 sansheng-write 的四项借鉴（P0 硬门禁 / P1a 风格 Profile / P1b 冷读外审 / P2 跨笔记索引），在 v2.0.1 基础上实现「Profile 驱动的 CP5 双路径」——常用户 1 次弹窗直达成品，新手仍走完整四预览。
- **新增「🎯 风格偏好 Profile」（P1a）**：`~/.bilinote/profile.yaml` 存默认风格 + 增强链 + 避开项。CP5-A 开头检测：有 Profile → 轻量确认路径（仅 1 弹窗，展示偏好风格完整预览 + 一句确认，确认即按默认增强链出成品）；无 Profile → 标准四预览；说"换风格"→ 立即退回标准路径。Profile 是加速键不是绑架。
- **新增「📋 质检摘要」门禁（P0 + P1b + P2 收敛）**：交付前无条件执行的三层被动卡片（无弹窗）——① 硬门禁：逐条机检「铁律总纲」（破折号/不编造/版权线/确定性/等待期不弹窗）；② 冷读外审：仅当应用 E6 去AI味时，换不同模型族 subagent 冷读成品判定"像不像 AI 写"并给 ≤3 改点（即「去AI味（含换模型审稿）」承诺的审稿环节）；③ 跨笔记索引：series 合集模式更新 `knowledge-index.json`。不过不交付。
- **「铁律总纲」集中收敛（v2.1 新增）**：把分散全文的硬约束（破折号统一、不编造、版权线 ≤150 字、强制 checkpoint、等待期不弹窗、确定性优先、质量门禁）收敛到一处，各阶段执行前引用，避免遗漏。
- **CP5-B 微调**：「去AI味」选项补「（含换模型审稿）」标注，描述写明冷读审稿环节；并在 CP5-B 顶部注明 Profile 短路用户不进入本步。
- 收尾动作 Step 5 改为先过「📋 质检摘要」再定稿（原 Step 6/7 顺延为 7/8）。
- `scripts/lint_skill.py` 校验通过（0 错误 0 警告）。

### 2.0.1 — 2026-07-12（CP5-B 去术语化）

- **修复 CP5-B 术语泄漏（v2.0 端到端复验发现）**：v2.0 的 CP5-A 已改用产出导向人话标签（🔥小红书种草…），但 CP5-B 的两问选项仍退回 `信息图E4 / 配图E3 / E8排版 / series系列聚合` 这类内部代号，与 v2.0「去技术化·所见即所选」哲学自相矛盾。复验中首用用户反馈"series系列聚合什么意思？第一次用的用户也看不懂啊"坐实该问题。
- **CP5-B Step1 过滤表 + Step2 两问选项**全部改写为大白话（🖼️信息图 / 🧠思维导图 / 🎨手绘配图 / 📸嵌入截图 / ✍️去AI味 / 📝公众号排版 / 📄导出PDF·Word / 📚做成系列合集），并在 Q2 给"系列合集"补一句 plain 解释（同主题多期自动归并成系列目录）。
- 同步修复等待期能力预览里的"series 合成系列"泄漏为"系列合集：同主题多期内容 → 自动归并成一个系列目录"。
- 保留术语对照注释（内部用，用户无需知道：🖼️=E4 · 🎨=E3 · ✍️=E6 · 📝=E8 · 📄=export · 📚=series），并注明更多增强（review / E5）用户直接说即可。
- `scripts/lint_skill.py` 校验通过（0 错误 0 警告）。

### 2.0.0 — 2026-07-12（所见即所选 · 决策流程科学重构）

- **CP5 升级为「所见即所选」（S4 升级 · 核心）**：从 v1.3.0 的"4 组标签盲选"升级为**四风格并行预览**——agent 写完 concise 草稿后，并行生成 4 版真实风格样例（🔥小红书种草 / 📊商业简报 / ⚡精简速查 / 🎭费曼讲解），用户看到真实产出再选方向（可多选=多份）。彻底消灭"选标签猜产出"的半盲决策。
- **CP5 拆为 CP5-A（风格预览）+ CP5-B（渐进增强）**：两步各 2 问，认知负荷减半；CP5-B 按已选风格**动态过滤**增强选项（S5），只展示最相关的，消除选项噪音。
- **CP1 改为智能默认（S2）**：彻底弃用 AskUserQuestion 询问"采集哪些原料"，改为按输入类型自动套用最优采集组合（B站→弹幕+截图 / YouTube→评论 / 文章→配图 等），纯文本告知、可取消。解决 CP1 技术化 + 管线-视觉断裂两问题。
- **新增提速通道（S3）**：首条消息含明确风格+扩展意图时，语义解析后仅一次轻量确认即直达成品，绕过 CP1/CP5 逐个询问。专家/明确意图用户零等待。
- **内容智能推荐（S6）**：等待期预览按标题/来源推测类型给推荐（lite），CP5-A 前按已读内容给精准推荐（full），把"选择"变成"确认"。
- **后续操作建议（S7）**：交付后依内容类型主动给出"下一步"入口（系列/对比/聚合），把一次性做笔记变成持续使用入口，提升留存。
- **设计哲学跃迁**：v1.0→1.3 优化"让用户选得更精准"，v2.0 直接移除盲选——从"根据标签选"到"看到产出再选"。总增量 token 约 1.5K-2.5K/次（4 预览+推荐+建议），对正常视频笔记占比 <15%，用户明确"不考虑成本"下全面落地。
- `scripts/lint_skill.py` 校验通过。

### 1.0.0 — 2026-07-12（首个版本化基线 · agent 维护）

- **交互重构（P0–P3，本会话累计完成）**
  - 新增 **CHECKPOINT 5**：笔记生成后、交付前的结构化增强确认（一次性 AskUserQuestion，覆盖 E4 信息图 / E5 网页PPT / E6 去AI味 / E8 公众号排版 / 导出 PDF·Word / mindmap 思维导图 / produce 一源多产 / review 质量闸），默认全否、一轮不问
  - CP1 Step 3 由冗长能力罗列改为轻量确认 + 指向 CP5
  - Wizard 注释补"生成后仍须走 CP5"；Batch 完成后强制展示报告并询问后处理 / 系列聚合
  - F3/F4 转写引擎切换时 agent 主动告知；cache 命中主动提示"零重抓秒出"
  - CP1 末尾加自定义风格提示（`--style @你的风格名`）；E7 表补 CP5 入口引用
  - B1/B2 条件种草提示（未开 `--screenshots` / `--images` 时交付附一句）、A5 系列聚合入口（CP5 交付 + batch 询问）
- **元数据修正**：frontmatter `description` 由"6 大扩展能力（E1–E6）"更正为"7 项扩展能力（E1–E8，E7 为调用优先级与时机）"，消除与正文脱节
- **验证状态**：`scripts/lint_skill.py` 0 错误 0 警告通过；CP5 实际触发的**端到端运行验证待安排**（需真实 B站/YouTube 链接或本地视频文件，见下条待办）

### 1.1.0 — 2026-07-12（等待期能力预览）

- **新增「等待期能力预览」（预处理 · 一次性 · 被动）**：agent 在 `run`/`summarize` 遇到**长等待源**（视频转写 / 远程抓取下载）期间，被动输出一次下游能力菜单（E4 信息图 / E5 网页PPT / E6 去AI味 / E8 公众号 / mindmap / produce / review / series / 导出），帮助**首次用户提前规划**。铁律：绝不弹 `AskUserQuestion`、单次仅一次、非阻塞、措辞明确"稍后我会问你"。与 CP1 Step 3 + CP5 构成**三段式触达**（起飞前轻确认 → 等待期被动菜单 → 生成后主动决策）。
- 源于 C 端到端验证期间用户提议：等待空窗是展示下游能力的黄金窗口，填补了此前全链路诊断未覆盖的"dead time"盲区（原诊断只抓了 CP5 生成后窗口，漏了生成前等待窗口）。

### 1.3.0 — 2026-07-12（CP1 瘦身 + CP5 升级为最终形态中枢）

- **CP1 角色变更**：从"12 组合预设风格选择"彻底瘦身为"管道前置决策"——仅负责输入管线原料采集（弹幕/评论/截图/配图/cookie），默认 `--style concise` 出通用草稿。移除全部 12 预设表格、4 问 AskUserQuestion 风格选择、base_style+exts 解析逻辑。设计原则：不在用户没看见内容时让做盲决策。
- **CP5 升级为最终形态中枢**：从"4 问增强确认"升级为"4 维最终形态决策"——Q1 交付风格（4 组覆盖 16 风格，多选=produce 多平台）、Q2 视觉丰富度（截图/弹幕/评论/配图/信息图/导图，首次将弹幕与高能评论暴露为一级选项）、Q3 内容增强（E6/review/E5/produce）、Q4 输出形式（E8/PDF/Word/导图/series）。全部 multiSelect + 默认全否。
- **核心 UX 改善**：风格选择从"生成前盲猜"变为"生成后依内容决策"，决策质量显著提升。`produce` 改写链路（concise → 任一风格）经端到端验证可靠。
- **保留项**：`--style` CLI 参数仍可用于直接指定风格（绕过交互）；自定义风格 Plan K（`--style @你的风格名`）不受影响；E1/E2 仍为预管线触发不进入 CP5。
- `scripts/lint_skill.py` 校验通过。

### 1.2.0 — 2026-07-12（C 端到端验证完成）

- **C · 端到端验证已通过**：真实 B站链接 `BV1tr7p6sEMc`（1818黄金眼婚恋骗局案）跑通全链路
  - 管线：`run` → 富化器#0(B站官方AI总结)失败安全回退 → 无字幕 → bcut 中文转写成功 → 原生模式产出 `note.brief.md`（330 行含完整转录）
  - **CP5 真实触发**：笔记(concise)生成后弹出 4 问 AskUserQuestion，用户一次性勾选 6 项扩展，证明此前盲区已消除
  - **扩展链路实测全绿**：`humanize`(E6, 检出破折号滥用×3) / `export --formats mindmap` / `produce --preset social-matrix`(小红书+B站+知乎+信息图) / `series --title` / `review --transcript --auto-fix` 均成功产出 native-mode brief；E4 信息图 + E5 网页PPT 由 agent 直接生成 HTML 产物
  - 验证工作区：`<你的工作目录>/bili-verify/`（含 note.md 及全部衍生产物，路径仅为示例，按实际环境替换）
  - `scripts/lint_skill.py` 校验 0 错误 0 警告通过

### 待办（规划中）
- [x] ~~**C · 端到端验证**~~（已于 1.2.0 完成，见上）
- [ ] **上游比对（可选）**：该技能 mirroring 自 `JefferyHcool/BiliNote`，可人工核对能力清单差异；当前为静态派生，无自动同步机制
- [ ] **batch 默认 `--then series`（可选·激进）**：诊断标注为后续可选，D2 询问式提示已覆盖该场景，暂不改动默认行为
