---
name: deepseek-image-ocr
description: >
  Reads the CONTENT of an image (photo, screenshot, scan, handwritten note, chart,
  diagram, table) by routing it to DeepSeek's web chat when the active model has
  NO vision. Triggers only when the model actually cannot see the image: the user
  attached an image and the model got a vision-unsupported error, or saw the
  placeholder "[image omitted because this model accepts text only; attachment
  sha256:...]". Also triggers on explicit image-content requests that the model
  cannot fulfill: "识图", "图片里有什么", "read this image", "image ocr", "ocr this",
  "这图里写的什么", "descrbe/describe this screenshot". Does NOT trigger on: creating
  or generating an image, editing/designing an image, analyzing a video, or normal
  text-only work. Auto-invokes only on a vision-unsupported image-input error.
whenToUse: >
  The model is asked to interpret an image it cannot see (no vision support).
  Do NOT use for: image generation/editing, video analysis, or text/tool work.
  Do NOT use if the image failed for a non-vision reason (too large, expired
  attachment, corrupt file) - that needs a different fix, not OCR routing.
  Do NOT use if the model CAN see the image - just answer directly.
argument-hint: "<image path or URL>"
license: MIT
---

# DeepSeek Image OCR (deepseek-image-ocr)

Bridges vision gaps: sends an image to DeepSeek web chat and brings the
recognized content back into the current DSH session. The model behind the web
chat can see images server-side even when the active DSH model cannot.

## Architecture

A dedicated debug browser stays open on port 9222 with its own user-data-dir, so
it never touches the user's main browser. The user logs in to DeepSeek there
ONCE; the login persists in that profile. browser-use attaches to it via
`BU_CDP_URL=http://localhost:9222`.

- Primary browser: Chrome `<CHROME_EXE>` (e.g. `C:\Program Files\Google\Chrome\Application\chrome.exe`),
  profile `~/.dsh/vendor/chrome-debug-9222`.
- Fallback: Edge, profile `~/.dsh/vendor/edge-debug` (start it the same way).

Launch command (Chrome; the real URL is required - `about:blank` gets swallowed
by a running Chrome instance and the debug port never opens):

```
<CHROME_EXE> --remote-debugging-port=9222 --user-data-dir=~/.dsh/vendor/chrome-debug-9222 --no-first-run --no-default-browser-check https://www.example.com
```

## Flow (implemented in ocr.py)

1. Ensure the debug browser is up on 9222 and the user is logged in (composer
   present). Browser cookies persist the login across calls - no TTL file.
2. `new_tab('https://chat.deepseek.com')`, wait for load, check the composer.
   No composer => not logged in => hand off to the user, retry after.
3. Install hooks: XHR prototype override captures completion SSE streams into
   `window.__urespList`; `window.fetch` override logs request URLs into
   `window.__ulog`.
4. Attach the image with CDP `DOM.setFileInputFiles` via the input's
   `backendNodeId` (from `DOM.getDocument` -> `DOM.querySelector
   input[type=file]` -> `DOM.describeNode`). CJK paths work directly; no
   ASCII-path copy is needed.
5. Wait for upload-complete signal: a `fetch_files?file_ids=` request appears
   in `window.__ulog`. NOT the local `blob:` thumbnail (appears instantly,
   before server upload) and NOT any `.ds-loading` spinner (persistent
   telemetry). Sending before this fires gives an empty reply.
6. Set toggles via `.ds-toggle-button` + `aria-pressed`: deepthink ON,
   web-search OFF. Web search defaults ON and injects unrelated results that
   starve the reply; deepthink must be ON for real image analysis.
7. Send: focus the composer, `execCommand('insertText', prompt)`, click the
   send button `.ds-button--primary.ds-button--circle` in the footer.
8. Wait for the completion stream to stabilize (no new responses for 15s), then
   parse the SSE: the stream has a THINK fragment (discard - it is the reasoning)
   then a RESPONSE fragment (keep - it is the answer). Return ONLY the RESPONSE
   content.
9. Close the tab with `Target.closeTarget` (not the browser).

## Prompt

Open-ended, no output constraints, so nothing is missed:

```
请识别并描述这张图片中的所有内容。
```

A narrower enumerated prompt ("transcribe text / list objects / read tables /
state file-type") was rejected: it risks dropping content and biases the model.

## Extracting the answer

Do NOT scrape the DOM for the reply. DeepSeek uses hashed class names and a
virtualized list (`ds-virtual-list`), so CSS selectors and `document.body.innerText`
are unreliable. Parse the captured SSE stream instead:

- THINK fragment content is the reasoning process - discard it.
- RESPONSE fragment content is the answer - return it verbatim.
- Fragments arrive as: a full-response update carrying a fragment list, a
  `response/fragments` APPEND adding a new fragment, and content APPENDs
  (`{"v":"..."}` or `{"p":".../-1/content","v":"..."}`) accumulating text.

parse_stream() in ocr.py handles all three shapes; reuse it.

## Rules

- Web search OFF, deepthink ON, every call.
- Wait for `fetch_files?file_ids=` before sending.
- Return ONLY the RESPONSE content - never the thinking process.
- Keep the prompt open-ended and fixed.
- If not logged in, hand off to the user, then continue automatically.
- If the model can see the image, do NOT invoke this skill; answer directly.

## Files

- SKILL.md                 this file
- ocr.py                   driver: hooks + attach + toggles + send + stream parse
  `python ocr.py --test`    self-check of parse_stream (no browser needed)
  via browser-use          feed ocr.py to stdin then call `run(r"<path>")`

## Gotchas

- browser-use scripts piped through pwsh MUST be pure ASCII - CJK in a .py
  source mangles via console codepage 936. Escape CJK as `\uXXXX` in JS string
  literals. ocr.py is pure ASCII for this reason.
- Chrome with `about:blank` + a profile that another Chrome instance uses gets
  handed off to that instance and exits; the debug port never opens. Use a real
  URL and a dedicated profile dir.
- DeepSeek's class names are hashed and change between builds; do not key on them
  except the stable `.ds-toggle-button` / `.ds-button--primary` patterns.
