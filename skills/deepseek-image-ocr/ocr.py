#!/usr/bin/env python3
# ocr.py - OCR an image via chat.deepseek.com over the dedicated debug browser (CDP 9222).
# Assumes browser-use is already attached to a debug browser on port 9222 where the
# user is logged in to DeepSeek. See SKILL.md for browser launch + one-time login.
import sys, time, json

# Open-ended prompt: no output constraints, so nothing is missed. (User-corrected:
# an enumerated "transcribe text / list objects / read tables" prompt was too narrow.)
PROMPT = '\u8bf7\u8bc6\u522b\u5e76\u63cf\u8ff0\u8fd9\u5f20\u56fe\u7247\u4e2d\u7684\u6240\u6709\u5185\u5bb9\u3002'

# XHR hook: completion SSE streams -> window.__urespList (one entry per completion request).
# fetch hook: request URLs -> window.__ulog (upload-complete signal: fetch_files?file_ids=).
HOOK = "(function(){if(window.__hk)return 'already';window.__hk=1;window.__urespList=[];window.__ulog=[];var xo=XMLHttpRequest.prototype.open,sf=XMLHttpRequest.prototype.send;XMLHttpRequest.prototype.open=function(m,u){this.__u=String(u).slice(0,150);return xo.apply(this,arguments);};XMLHttpRequest.prototype.send=function(b){var self=this;if((self.__u||'').indexOf('completion')>=0){self.addEventListener('load',function(){try{window.__urespList.push(String(self.responseText||''));}catch(e){}});}return sf.apply(this,arguments);};var of=window.fetch;window.fetch=function(u,o){try{window.__ulog.push(String((u&&u.url)||u||'').slice(0,150));}catch(e){}return of.apply(this,arguments);};return 'hooked';})()"

# Toggle: deepthink ON, web-search OFF. Search default-on injects web results and
# starved the reply; deepthink must be on for real image analysis.
SETTOGGLES = "(function(){[...document.querySelectorAll('.ds-toggle-button')].filter(function(b){return b.offsetParent;}).forEach(function(b){var t=(b.innerText||'').trim(),ap=b.getAttribute('aria-pressed')==='true';if(t.indexOf('\\u6df1\\u5ea6\\u601d\\u8003')>=0&&!ap)b.click();if(t.indexOf('\\u667a\\u80fd\\u641c\\u7d22')>=0&&ap)b.click();});return 'set';})()"

# Insert prompt + click the send button (.ds-button--primary.ds-button--circle in footer).
SENDJS = "(function(){for(var tr=0;tr<8;tr++){var e=document.querySelector('[contenteditable=true]')||document.querySelector('textarea');if(!e)continue;e.focus();document.execCommand('insertText',false,'__P__');if(e.textContent.trim().length>5){var root=e.closest('div[class*=footer],div[class*=input],div[class*=composer],form')||e.parentElement.parentElement.parentElement.parentElement;var s=[...root.querySelectorAll('[role=button],[class*=ds-button]')].filter(function(b){return b.offsetParent&&/ds-button--primary/.test(b.className)&&/ds-button--circle/.test(b.className);})[0];if(s&&s.className.indexOf('disabled')<0){s.click();return 'sent';}return 'send-disabled';}}return 'no-composer';})()".replace('__P__', PROMPT)

def parse_stream(s):
    # SSE stream: THINK fragment (discard) then RESPONSE fragment (keep). Fragments
    # arrive as: full-response update with a fragment list, a fragment-array APPEND,
    # and content APPENDs (with or without an explicit 'o').
    fragments = []
    for line in s.split('\n'):
        line = line.strip()
        if not line.startswith('data:'): continue
        payload = line[5:].strip()
        if not payload or payload == '[DONE]': continue
        try: obj = json.loads(payload)
        except: continue
        if not isinstance(obj, dict): continue
        v, p, o = obj.get('v'), obj.get('p'), obj.get('o')
        if isinstance(v, dict) and 'response' in v:
            frags = v['response'].get('fragments', [])
            if frags:
                fragments = [{'type': f.get('type',''), 'content': fragments[i]['content'] if i < len(fragments) else ''} for i, f in enumerate(frags)]
            continue
        if p == 'response/fragments' and o == 'APPEND' and isinstance(v, list):
            for f in v:
                fragments.append({'type': f.get('type',''), 'content': '' if f.get('content','') == '1' else f.get('content','')})
            continue
        if p and 'fragments/-1/content' in p and isinstance(v, str):
            if fragments: fragments[-1]['content'] += v
            continue
        if isinstance(v, str) and not p and not o:
            if fragments: fragments[-1]['content'] += v
            continue
    return fragments

def run(path):
    new_tab('https://chat.deepseek.com')
    wait_for_load()
    time.sleep(2)
    if not js("!!document.querySelector('[contenteditable=true],textarea')"):
        print('NEED_LOGIN=1'); print('ACTION=log in to chat.deepseek.com in the debug browser, then retry'); return
    cdp('Network.enable')
    js(HOOK)
    doc = cdp('DOM.getDocument', depth=-1)
    nid = cdp('DOM.querySelector', nodeId=doc['root']['nodeId'], selector='input[type=file]')['nodeId']
    backend = cdp('DOM.describeNode', nodeId=nid, depth=0, pierce=True)['node']['backendNodeId']
    # CJK path works directly with setFileInputFiles; no ASCII-path copy needed.
    cdp('DOM.setFileInputFiles', files=[path], backendNodeId=backend)
    # Upload-complete signal: fetch_files?file_ids= in the hooked request log.
    # NOT the local blob: thumbnail, which appears instantly before server upload.
    for _ in range(30):
        time.sleep(1)
        if 'fetch_files?file_ids=' in '|'.join(js("window.__ulog||[]")):
            break
    js(SETTOGGLES)
    time.sleep(1)
    st = js(SENDJS)
    if st != 'sent':
        print('SEND_FAIL=' + str(st)); return
    # Wait for the completion stream to stabilize (no new responses for 15s).
    prev = 0; stable = 0
    for _ in range(80):
        time.sleep(5)
        cnt = len(json.loads(js("JSON.stringify(window.__urespList.map(function(s){return s.length;}))")))
        if cnt == prev and cnt > 0: stable += 1
        else: stable = 0
        prev = cnt
        if stable >= 3: break
    streams = json.loads(js("JSON.stringify(window.__urespList)"))
    best = ''
    for s in streams:
        for f in parse_stream(s):
            if f['type'] == 'RESPONSE' and len(f['content']) > len(best):
                best = f['content']
    print('RESULT_START')
    print(best if best else 'NO_RESPONSE')
    print('RESULT_END')
    # Close the tab (not the browser).
    try:
        for t in cdp('Target.getTargets').get('targetInfos', []):
            if 'chat.deepseek.com' in str(t.get('url','')):
                cdp('Target.closeTarget', targetId=t['targetId']); break
    except Exception: pass

def _selftest():
    # Real fragment of a DeepSeek completion stream (THINK then RESPONSE).
    sample = (
        'data: {"v":{"response":{"fragments":[{"id":2,"type":"THINK","content":"1"}]}}}\n'
        'data: {"p":"response/fragments","o":"APPEND","v":[{"id":3,"type":"RESPONSE","content":"\\u6839\\u636e"}]}\n'
        'data: {"v":"\\u60a8"}\n'
        'data: {"v":"\\u63d0\\u4f9b\\u7684"}\n'
    )
    frags = parse_stream(sample)
    assert frags[0]['type'] == 'THINK', frags[0]
    assert frags[1]['type'] == 'RESPONSE', frags[1]
    assert frags[1]['content'] == chr(0x6839)+chr(0x636e)+chr(0x60a8)+chr(0x63d0)+chr(0x4f9b)+chr(0x7684), repr(frags[1]['content'])
    print('SELFTEST_OK')

if __name__ == '__main__':
    if '--test' in sys.argv:
        _selftest()
    elif len(sys.argv) > 1:
        run(sys.argv[1])
