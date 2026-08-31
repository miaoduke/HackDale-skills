# Platform notes (BiliNote-style)

The `fetch` step uses `yt-dlp` for every URL. Behavior per platform:

## Bilibili (哔哩哔哩)
- Audio downloads reliably via yt-dlp.
- **Subtitles**: manual subtitles are preferred; auto-subtitles via `--write-auto-subs`.
  yt-dlp can fetch many B站 字幕 directly. Where a video requires login to
  access subtitles, supply cookies with `--cookies cookies.txt` (exported from
  a logged-in browser). Subtitle-priority still holds: if a `.vtt` is obtained,
  audio transcription is skipped entirely.

## YouTube
- Audio + subtitles work out of the box with yt-dlp.
- `--write-auto-subs` covers most videos without manual captions.
- Some regions require a proxy; set `HTTP_PROXY` / `HTTPS_PROXY` in the env.

## 抖音 (Douyin) / 快手 (Kuaishou)
- yt-dlp supports many Douyin/Kuaishou share URLs, but availability changes
  frequently and some links need cookies or a browser-based fetch.
- If `fetch` fails on these platforms, fall back to downloading the video
  manually, then use `bilinote.py run --local FILE` (extract audio locally
  and transcribe). The upstream BiliNote reuses
  `Evil0ctal/Douyin_TikTok_Download_API` for robustness; this skill keeps the
  dependency-free yt-dlp path and the `--local` fallback.

## Local video
- Pass a path ending in `.mp4/.mkv/.webm/.mov/.avi/.flv` to `fetch` or `run
  --local`. Audio is extracted with ffmpeg; no subtitles are fetched, so the
  audio is always transcribed.

## General

- Subtitle-priority is the core cost-saving design: a video WITH subtitles
  skips the (expensive) transcription step.
- When subtitles are absent/unreadable, the audio is transcribed with the
  selected backend (bcut / kuaishou — see references/config.md).
- **If `fetch` fails for any reason** (CDN blocked / region-locked / proxy
  intercepts / link expired / login required), the fallback is always:
  **download the video yourself → pass the local file**:
  ```bash
  python scripts/bilinote.py run ./my_video.mp4 --out note.md
  ```
  Local files skip yt-dlp entirely — no CDN, no cookies, no proxy needed.
