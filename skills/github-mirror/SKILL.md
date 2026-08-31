---
name: github-mirror
description: >
  Faster, reliable access to GitHub from DSH when direct downloads are slow or
  fail. DSH fetches GitHub archives via codeload.github.com and raw files via
  raw.githubusercontent.com; on this machine codeload returns HTTP 502. This skill
  rewrites GitHub URLs through a healthy public mirror (probe-tested, load-balanced,
  with direct fallback) and caches probe results locally (60s TTL, auto-refresh).
  Use whenever you must download a GitHub archive zip, fetch a raw file, or hit
  github.com/raw.githubusercontent.com/codeload.github.com and the direct call
  times out, returns 502/4xx/5xx, or is slow. Also use when the user says
  "github mirror", "github proxy", "github加速", "ghproxy", "download from github".
whenToUse: >
  Auto-trigger: BEFORE any GitHub archive/raw/API download, run the probe helper
  (tools.pwsh/powershell -File github-mirror.ps1). It checks codeload health and
  picks a healthy mirror automatically. Manual trigger: "github加速", "ghproxy",
  "download from github", or any GitHub URL that fails or is slow.
argument-hint: "<github url> [--zip|--raw]"
license: MIT
---

# GitHub Mirror (github-mirror)

DSH's direct GitHub access breaks on codeload.github.com (HTTP 502). This skill
gives the agent a reliable mirror-based download path. It is ALWAYS ON via the
global AGENTS.md rule: before downloading any GitHub artifact, the agent runs the
probe helper automatically - you never need to type the skill name.

## When to use (auto)
Run the helper before downloading any GitHub archive zip, raw file, or API call
that is slow or failing. The helper auto-detects codeload health.

## How it works
1. Helper reads the local cache (60s TTL) for the last healthy mirror set.
2. Fresh TTL -> reuse cached mirror; on failure, re-probe fresh (stale caches are untrustworthy).
3. No cache / stale -> full probe of curated mirrors, keep top 3 by latency, persist to cache.
4. All mirrors fail -> fall back to direct URL (raw.githubusercontent.com usually works directly).

## Rewrite forms (the helper applies these automatically)
- Archive zip:  github.com/{o}/{r}/archive/refs/heads/{b}.zip  via {MIRROR} prefix
- Raw file:     raw.githubusercontent.com/{o}/{r}/{b}/{p}      via {MIRROR} prefix
- GitHub API:   api.github.com/...                            via {MIRROR} prefix

## Mirror status (probe-tested 2026-08, real GET downloads of the ponytail zip)
ACTIVE (fastest first, all returned HTTP 200 with identical bytes):
  gh.ddlc.top (2544ms) | gh.jasonzeng.dev (2679ms) | ghfast.top (2992ms) |
  wget.la (3101ms) | gh.zwy.one (3377ms) | gh.chjina.com (3471ms) |
  github.geekery.cn (5837ms) | gh.idayer.com (7503ms) | ghproxy.net (14897ms)
RAW file mirrors (fast, ~400ms):
  hk.gh-proxy.org (386ms) | wget.la (396ms) | ghfast.top (462ms) | fastly.jsdelivr.net/gh (765ms)
DOWN / slow as of this probe: gh.h233.eu.org (404) | gh-proxy.org (timeout) |
  gh.monlor.com (404) | github.ednovas.xyz (403) | gh.xxooo.cf | ghpxy.hwinzniej.top |
  git.yylx.win | cdn.crashmc.com | ghproxy.cxkpro.top | ghfile.geekertao.top |
  ghp.keleyaa.com | cors.isteed.cc | github.boki.moe | down.npee.cn | raw.ihtw.moe

## Files
- SKILL.md                      this file
- github-mirror.ps1             the helper (probe + rewrite + download + cache + fallback)
- ~/.dsh/vendor/github-mirror/cache.json   probe cache (60s TTL)

## Rules
- Verify HTTP 200 and non-zero bytes before accepting a download.
- Never send GitHub credentials to mirrors; API tokens stay on direct api.github.com.
- Mirrors are public/probono and flaky; the fallback chain handles that.
- If mirror content size mismatches direct, prefer the direct source of truth.

## Update the mirror list
Re-benchmark with: powershell -File github-mirror.ps1 -Url <any github zip> -OutFile t.zip
