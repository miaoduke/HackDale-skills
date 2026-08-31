# Configuration & environment

The bilinote skill is configured through environment variables (or CLI flags
that override them). No secrets are stored in the skill files.

## Note generation — agent-native (no external LLM API)

The skill does **not** call any external LLM API. `run` / `summarize` produce a
transcript + a self-contained brief (`<out>.brief.md`); the agent's own
conversation LLM generates the final Markdown note. The following variables and
CLI flags have been **removed** (no longer read anywhere):

- `BILINOTE_LLM_API_KEY` / `BILINOTE_LLM_BASE_URL` / `BILINOTE_LLM_MODEL`
- CLI: `--model`, `--base-url`, `--api-key`, `--calibrate`

No secrets are needed or stored.

## Transcriber (audio → text) — only used when no subtitle
| Variable | Default | Meaning |
|----------|---------|---------|
| `BILINOTE_TRANSCRIBER` | `auto` | 在线转写引擎：`auto` (按语种路由), `bcut`/`biji` (必剪, 免费无密钥), `kuaishou` (快手, 免费无密钥)。 |

CLI equivalents: `--transcriber`.

> `biji`（必剪）和 `bcut` 是**同一个引擎**——必剪是 B 站在线编辑器，其 ASR 即 BiliNote 所称 `bcut`。两者皆可用。

## 视频富化增强（#0–#5，可选，仅在线视频）
| Variable | Default | Meaning |
|----------|---------|---------|
| `BILINOTE_BILI_COOKIE` | — | B 站 Cookie（**含 SESSDATA**），用于官方 AI 总结（#0）等需登录接口；也用于弹幕/cid 解析的鉴权。CLI 等价：`--bili-cookie`。未设置时 #0 对多数视频返回 `code=-101 账号未登录` 并自动回退字幕优先/转写。 |

CLI 开关：`--no-bili-ai`(关#0) · `--danmaku`(#1) · `--linkify`(#3) · `--no-clean`(关#4 内容净化) · `--translate`(#5)；#2 随 `--screenshots` 自动。
独立子命令：`bili-summary`(#0) / `danmaku`(#1) / `suggest-frames`(#2) / `linkify`(#3) / `clean`(#4)。详见 SKILL.md「视频富化增强」章节。

### Language-aware router (`auto`, 默认)
- 路由策略（需在 `run` 时通过 `--lang <code>` 指定语种；未指定则按中文 bcut 优先）：
  - **zh / en** → `bcut`（必剪）优先，fallback `kuaishou`（快手）。
  - **其他语种 (ja/ko/fr/...)** → `kuaishou`（快手）优先，fallback `bcut`。
    （实测 Kuaishou 对 ja/ko 转写准确。）
- `bcut` 与 `kuaishou` 均**在线、免费、无密钥**。
- 若主引擎失败会自动尝试 fallback。两者均失败则抛出 RuntimeError。
- 手动指定引擎时池顺序：`bcut` → `kuaishou`。
- ⚠️ 本地 `fast-whisper`/`mlx-whisper` 与在线 `groq` 已移除；如遇 bcut/快手均失败，建议手动指定 `--lang` 重试。

## Report style (summarize output) — user-selectable
| Variable | Default | Meaning |
|----------|---------|---------|
| `BILINOTE_STYLE` | `concise` | 报告风格（控制笔记的语气/表达/侧重点）。可选 11 种：BiliNote 官方 9 种 `concise`(精简), `detailed`(详细), `tutorial`(教程), `academic`(学术), `xiaohongshu`(小红书), `lifestyle`(生活向), `task`(任务导向), `business`(商业), `meeting`(会议纪要)；bilinote 平台扩展 `wechat`(公众号长文), `bilibili`(B站视频脚本)。三个平台风格(`xiaohongshu`/`wechat`/`bilibili`)会注入结构化平台写法规范（详见 `references/style_prompts.md`）。 |

CLI equivalents: `--style` (on `run` and `summarize`).

- 风格对齐 BiliNote 官方「笔记风格」预设（详见 https://docs.bilinote.app/guide/basic ），
  与「笔记格式」（目录/截图等）相互独立。风格会被**注入 LLM 提示词**（或原生模式简报规则），
  生成的笔记按该语气撰写；不改变抓取/转写步骤。
- `concise`(精简) 为上游默认值，对应"提炼要点、简洁明了"。
- 分块总结合并时，合并步骤会要求**保持所选风格**，保证最终笔记一致。

## Screenshot embedding (optional, user-decided)
The `--screenshots` flag only inserts `*Screenshot-[mm:ss]*` **placeholders**
into the note. To actually put real video frames in, the user must opt in:

- **Explicit / standalone:** pass `--embed-screenshots` to `run`. This
  auto-enables `--screenshots`, downloads the best video stream, and after the
  note is produced calls `embed-screenshots` to extract one frame per marker
  with `ffmpeg` (requires `ffmpeg` on PATH). Images land in `screenshots/`
  beside the note.
- **Agent-native (default):** the brief records the downloaded video path
  and the available markers. The agent **asks the user** whether to embed; if
  yes, it runs:
  ```bash
  python scripts/bilinote.py embed-screenshots --note <out> --video <video_path> --out <out>
  ```
  (`--url` may be used instead of `--video` to download first. The download
  honors `BILINOTE_YTDLP_COOKIES` / `BILINOTE_PROXY` — see **Video download:
  cookies & proxy** — which is how blocked Bilibili CDNs get worked around.)
- The standalone helper `embed-screenshots --note N --video V [--out O]` works
  on any note that already contains `*Screenshot-[mm:ss]*` markers.

## External binaries (must be installed separately)
- `ffmpeg` — required for audio extraction/local video. Not a pip package.
- `yt-dlp` — installed via `requirements.txt`, but also needs `ffmpeg`.

## Input sources — `run` auto-classifies (2026-07-09 新增)

The `run` subcommand accepts **any** of the following and decides the flow
itself via `classify_source()` (no need to pick a subcommand):

| Input | Detected kind | Flow |
|-------|---------------|------|
| Video-platform URL (Bilibili/YouTube/…) | `video_url` | fetch → subtitle/transcribe → summarize |
| Direct media URL (`.mp4`/`.mp3`…) | `media_url` | fetch → subtitle/transcribe → summarize |
| Local video/audio file | `media_file` | fetch_local → transcribe → summarize |
| Local subtitle file (`.vtt`/`.srt`/`.ass`/`.ssa`/`.sub`) | `subtitle_file` | **read subtitle directly** → summarize |
| Any other `http(s)` URL | `article_url` | **`scrape_article`** → summarize |
| Local doc file (`.txt`/`.md`/`.pdf`/`.docx`/`.doc`…) | `doc_file` | **`read_document`** → summarize |
| Raw pasted text | `text` | summarize directly |

- **Video/audio kinds** go through the normal transcription pipeline and support
  time markers / screenshot embedding.
- **Subtitle file** (`.vtt`/`.srt`/`.ass`/`.ssa`/`.sub`) is read directly via
  `parse_vtt()` and fed to `summarize` with `media=True` — this **skips fetch
  and transcription entirely**. Use this when you already have a subtitle file
  (downloaded manually, extracted from MKV, or exported from a subtitle editor).
- **`--subtitle-file PATH`** explicitly provides a subtitle file **alongside a
  video source** (URL or local). The skill reads the given subtitle instead of
  fetching/downloading one, but still extracts video metadata (title, tags) and
  optionally supports multimodal frame sampling. This is useful when:
  - The video platform doesn't expose subtitles via yt-dlp but you have one.
  - You want to use a corrected / human-edited subtitle instead of the auto-generated one.
  - You have a local video file with a matching subtitle file.
- **Article URL** is fetched with `requests`; main text is extracted by
  `trafilatura` when present, otherwise by `beautifulsoup4`, with a last-resort
  regex tag-strip. Raises if nothing usable is extracted (likely paywalled/anti-bot).
  Raw **bytes** are fed to the parser so the real UTF-8 charset is auto-detected
  from `<meta>` (avoids mojibake when the server omits a charset).
- **Article images** (optional, `--images`): when enabled, `scrape_article`
  also returns up to 8 content-image URLs (`_extract_article_images`), filtered
  to drop site chrome (login/avatar/banner/app icons, placeholder tokens like
  `@@pic1@@`, tracking pixels). The note prompt/brief lists them (rule 9) and
  the LLM inserts `*Image-1*`…`*Image-N*` markers; `embed-article-images`
  downloads each referenced URL (with a same-origin `Referer` to bypass simple
  hotlink protection) into `images/` and replaces the markers.
- **Local documents**: text types (`.txt`/`.md`/`.json`/`.csv`/`.html`) are read
  directly; `.pdf` via `pypdf`/`PyPDF2`; `.docx` via `python-docx`; `.doc` is
  attempted only if `textract` is installed (else clear error → convert to `.docx`).
- **Non-video inputs** skip transcription and are passed with `media=False`:
  the note prompt/brief disables time markers and `*Screenshot-[mm:ss]*`
  placeholders, and labels the content "原文内容" instead of "视频转录".
- **Native-mode interaction**: the brief instructs the agent to confirm with the
  user (via AskUserQuestion) **(1) report style** and **(2) image embedding**
  before finalizing the note, unless those were already supplied as CLI flags.

### New dependencies (added to `scripts/requirements.txt`)
- `trafilatura` — preferred web extractor (optional; `beautifulsoup4` fallback).
- `beautifulsoup4` — mandatory article/doc HTML fallback parser.
- `pypdf` — PDF text extraction (`PyPDF2` used automatically if `pypdf` absent).
- `python-docx` — already required; used for `.docx` reading.
- `textract` — **optional**, only for legacy `.doc`; install manually if needed.

## Video download: cookies & proxy (yt-dlp)
All yt-dlp download calls — audio, subtitles, and the video-for-screenshots
stream in both `fetch` and `embed-screenshots --url` — pick up the two
optional variables below via `_ytdlp_extra_opts()`. When neither is set,
**no extra flag is added** (default behaviour unchanged). This mirrors upstream
BiliNote's browser-cookie sync + global proxy.

| Variable | Default | Meaning |
|----------|---------|---------|
| `BILINOTE_YTDLP_COOKIES` | — | Browser name to read cookies from (`chrome` / `edge` / `firefox`). Adds `--cookies-from-browser <name>`. **Login-state Bilibili cookies select a reachable CDN mirror** that is often blocked for anonymous requests — this is the fix for `WinError 10061 connection refused` / `requested format is not available` on restricted networks. Requires the named browser to be installed and a Bilibili login session present. |
| `BILINOTE_PROXY` | — | Outgoing proxy for downloads (e.g. `http://127.0.0.1:7890`). Adds `--proxy <url>`. **Takes priority** over the generic proxy vars below. |
| `HTTPS_PROXY` / `HTTP_PROXY` | — | Generic proxy fallback used when `BILINOTE_PROXY` is unset (standard yt-dlp env handling). |

> **CDN blocked?** When `embed-screenshots --url` fails with a
> `mcdn.bilivideo.cn … connection refused` error, the video CDN is not
> reachable from the current network. Set `BILINOTE_YTDLP_COOKIES=chrome`
> (or `edge`) so a **logged-in** browser session supplies cookies that
> route Bilibili to a different, reachable mirror host. In an environment
> where even that is blocked, download the video manually (e.g. from a
> reachable machine) and pass it with `--video <path>` instead of `--url`.

The video format selector was also loosened from `best[ext=mp4]/best` to
`b[ext=mp4]/b` so a download succeeds even when no single combined
mp4 stream is available.

## Proxy
- Set `HTTP_PROXY` / `HTTPS_PROXY` for region-restricted platforms (e.g. YouTube in CN).
- For Bilibili video downloads specifically, prefer `BILINOTE_YTDLP_COOKIES`
  (login cookie → reachable CDN mirror) and/or `BILINOTE_PROXY` — see
  **Video download: cookies & proxy** above.

## Note
- The RAG / chat-QA feature of upstream BiliNote is intentionally NOT part of
  this skill (no `chromadb`, no vector store, no chat service).
