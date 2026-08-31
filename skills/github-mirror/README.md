# github-mirror — DSH GitHub access accelerator skill

Lazy senior dev mode for GitHub downloads in DeepSeek Harness (DSH).

## What it does
DSH's direct GitHub access breaks on codeload.github.com (HTTP 502). This skill
routes GitHub archive/raw/API downloads through a fast, healthy public mirror,
with local probe caching (60s TTL) and direct fallback.

## Files
- SKILL.md           the skill definition (trigger words + procedure)
- github-mirror.ps1  the helper (probe + rewrite URL + download + cache + fallback)

## Install into another agent

### Claude Code / Codex / Copilot CLI
1. Copy this folder into your agent's skills directory, e.g.:
   - Claude Code:  ~/.claude/skills/github-mirror/
   - Codex:        ~/.codex/skills/github-mirror/
   - Copilot CLI:  ~/.copilot/skills/github-mirror/
   - DSH:          ~/.dsh/skills/github-mirror/
   - OpenCode:     ~/.config/opencode/skills/github-mirror/
2. Ensure the helper runs from a PowerShell-capable shell (Windows) or bash (macOS/Linux).
3. The agent auto-loads the skill when a GitHub download is slow/failing or the user says
   "github加速" / "ghproxy" / "download from github".

### Requirements
- The helper runs in the agent's shell tool (PowerShell on Windows, bash on macOS/Linux).
- API keys for the search providers are read from env vars
  (TAVILY_API_KEY / EXA_API_KEY / FIRECRAWL_API_KEY) or the Windows User registry.
  Set them in the target environment, or edit github-mirror.ps1 to hardcode keys.
- No browser needed for plain HTTP downloads through the mirrors.

## Verify it works
Run:  powershell -File github-mirror.ps1 -Url https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip -OutFile t.zip
Expected: CACHE=MISS (fresh probe) then MIRROR=... BYTES=... with a valid zip.

## Mirror list
Probe-tested 2026-08 (real downloads of the ponytail repo):
ACTIVE (fastest first): gh.ddlc.top (2544ms) | gh.jasonzeng.dev (2679ms) |
  ghfast.top (2992ms) | wget.la (3101ms) | gh.zwy.one (3377ms) | gh.chjina.com (3471ms) |
  github.geekery.cn (5837ms) | gh.idayer.com (7503ms) | ghproxy.net (14897ms)
RAW (fast, ~400ms): hk.gh-proxy.org | wget.la | ghfast.top | fastly.jsdelivr.net/gh
DOWN as of probe: gh.h233.eu.org | gh-proxy.org | gh.monlor.com | github.ednovas.xyz | others

## License
MIT
