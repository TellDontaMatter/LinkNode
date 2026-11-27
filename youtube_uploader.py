"""
LinkNode YouTube uploader.

Pipeline, one video at a time:
  1. Qwen node    - local Qwen (Ollama) drafts the title, description and tags from the video's script
  2. Truth gate   - blocks any claim on the NOT BUILT list in youtube/truth_gate.json
  3. Your review  - you read <video>.metadata.json and set "approved": true
  4. Upload node  - "studio" mode (default): writes paste-ready text for YouTube Studio.
                    "api" mode (after YouTube's API audit): uploads PRIVATE or scheduled. Never public.
  5. Log node     - records the link in youtube/uploads.json and pushes it to GitHub

Python standard library only, same as app.py. Nothing uploads until you approve it.

Commands (run from C:\\LinkNode):
  py youtube_uploader.py draft        draft + gate metadata for every new video
  py youtube_uploader.py upload       upload every video whose metadata says "approved": true
  py youtube_uploader.py check-auth   confirm the YouTube login still works (no upload)
  py youtube_uploader.py login        sign in to YouTube (first time, or after the login expires)

Setup: see youtube/README.md
"""
import json
import logging
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
YT_DIR = BASE_DIR / "youtube"
APPROVED_DIR = YT_DIR / "approved"          # put finished videos (.mp4/.mov) + their script (.md/.txt) here
CLIENT_SECRET = YT_DIR / "client_secret.json"  # from Google Cloud Console (never committed)
TOKEN_FILE = YT_DIR / "token.json"            # created by `login` (never committed)
GATE_FILE = YT_DIR / "truth_gate.json"
UPLOAD_LOG = YT_DIR / "uploads.json"
CONFIG_FILE = YT_DIR / "config.json"           # optional settings, see README

OLLAMA_URL = "http://localhost:11434/api/generate"
QWEN_MODEL = "qwen2.5:7b"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}
SCRIPT_EXTS = [".md", ".txt"]
CHUNK = 8 * 1024 * 1024  # multiple of 256 KB, as YouTube requires

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger("youtube")


# ---------------------------------------------------------------- helpers
def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def save_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def config():
    cfg = {"category_id": "28",          # 28 = Science & Technology
           "default_language": "en",
           "made_for_kids": False,
           "masterclass_links_live": False,
           "push_log_to_github": True,
           # "studio" (default): no API upload. Writes <video>.studio.txt with the approved, gated
           #   title/description/tags to paste into YouTube Studio.
           # "api": real API upload. ONLY switch to this after your Google Cloud project passes
           #   YouTube's API audit. Uploads from unaudited projects are locked private for good.
           "upload_mode": "studio",
           "footer": "Live graph: https://telldontamatter.github.io/LinkNode/"}
    cfg.update(load_json(CONFIG_FILE, {}))
    return cfg


def videos():
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(p for p in APPROVED_DIR.iterdir() if p.suffix.lower() in VIDEO_EXTS)


def script_for(video):
    for ext in SCRIPT_EXTS:
        s = video.with_suffix(ext)
        if s.exists():
            return s.read_text(encoding="utf-8", errors="ignore")
    return ""


def meta_path(video):
    return video.with_name(video.stem + ".metadata.json")


# ---------------------------------------------------------------- 1. Qwen node
def ask_qwen(title_hint, script_text):
    prompt = f"""System: You write YouTube metadata for LinkNode videos. Respond ONLY with valid JSON, no code fences, no commentary.

Facts you may use (nothing else):
- LinkNode turns a folder of markdown notes into a live knowledge graph.
- A local AI (Qwen 2.5 7B running in Ollama on the user's own PC) reads each note and finds its concepts and related topics.
- The graph is a force-directed graph you can drag and hover, published free on GitHub Pages.
- A watcher script rebuilds and publishes the graph whenever a note changes.
- No database, no server, no subscription. Notes stay on your machine.
Never mention: wikilinks or double brackets, regex, D3, headings becoming nodes, any file counts, any product for sale, masterclass numbers.
Do not use the characters < or > anywhere.

Video file name: {title_hint}
Video script:
{script_text[:6000]}

JSON schema:
{{"title": "max 90 characters, plain and specific", "description": "2-4 short paragraphs, max 1500 characters", "tags": ["5 to 12 short tags"]}}
"""
    payload = {"model": QWEN_MODEL, "prompt": prompt, "stream": False, "format": "json"}
    req = urllib.request.Request(OLLAMA_URL, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            text = json.loads(r.read().decode("utf-8")).get("response", "")
    except Exception as e:
        raise RuntimeError(f"Could not reach Qwen in Ollama ({e}). Is Ollama running?")
    text = text.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise RuntimeError(f"Qwen did not return valid JSON: {text[:300]}")
    return {"title": str(data.get("title", "")).strip(),
            "description": str(data.get("description", "")).strip(),
            "tags": [str(t).strip() for t in data.get("tags", []) if str(t).strip()]}


# ---------------------------------------------------------------- 2. Truth gate
def truth_gate(meta, cfg):
    """Returns a list of problems. Empty list = passes."""
    gate = load_json(GATE_FILE, {"banned": []})
    text = "\n".join([meta.get("title", ""), meta.get("description", ""), " ".join(meta.get("tags", []))])
    problems = []
    for rule in gate.get("banned", []):
        if rule.get("allow_if_config") and cfg.get(rule["allow_if_config"]):
            continue
        m = re.search(rule["pattern"], text, re.IGNORECASE)
        if m:
            problems.append(f'"{m.group(0)}": {rule["why"]}')
    # YouTube's own limits
    if not meta.get("title"):
        problems.append("title is empty")
    if len(meta.get("title", "")) > 100:
        problems.append("title is over YouTube's 100-character limit")
    if len(meta.get("description", "").encode("utf-8")) > 5000:
        problems.append("description is over YouTube's 5000-byte limit")
    if "<" in text or ">" in text:
        problems.append("YouTube does not allow < or > in titles or descriptions")
    if len(",".join(meta.get("tags", []))) > 500:
        problems.append("tags are over YouTube's 500-character limit")
    return problems


def cmd_draft():
    cfg = config()
    done = {u["file"] for u in load_json(UPLOAD_LOG, [])}
    vids = [v for v in videos() if v.name not in done]
    if not vids:
        log.info(f"No new videos in {APPROVED_DIR}")
        return
    for v in vids:
        mp = meta_path(v)
        if mp.exists():
            meta = load_json(mp, {})
            meta["gate_problems"] = truth_gate(meta, cfg)   # re-check after your edits
            meta["gate"] = "PASS" if not meta["gate_problems"] else "BLOCKED"
            save_json(mp, meta)
            log.info(f"{v.name}: already drafted, re-checked -> {meta['gate']}")
            continue
        script = script_for(v)
        if not script:
            log.warning(f"{v.name}: no script found ({v.stem}.md or .txt). Qwen will only see the file name.")
        try:
            meta = ask_qwen(v.stem, script)
        except RuntimeError as e:
            log.error(f"{v.name}: {e}")
            continue
        if cfg.get("footer") and cfg["footer"] not in meta["description"]:
            meta["description"] = (meta["description"] + "\n\n" + cfg["footer"]).strip()
        meta.update({"privacy": "private", "publish_at": "", "approved": False})
        meta["gate_problems"] = truth_gate(meta, cfg)
        meta["gate"] = "PASS" if not meta["gate_problems"] else "BLOCKED"
        meta["_how_to_approve"] = ('Edit title/description/tags if you want, then set "approved": true. '
                                   'For a scheduled release set publish_at like "2026-12-06T18:00:00-05:00". '
                                   'Run `py youtube_uploader.py draft` again to re-check, then `py youtube_uploader.py upload`.')
        save_json(mp, meta)
        if meta["gate"] == "PASS":
            log.info(f"{v.name}: drafted, gate PASS. Review {mp.name} and set approved to true.")
        else:
            log.warning(f"{v.name}: drafted, gate BLOCKED -> " + "; ".join(meta["gate_problems"]))


# ---------------------------------------------------------------- OAuth (installed-app loopback flow)
def _post_form(url, fields):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def _client():
    if not CLIENT_SECRET.exists():
        sys.exit(f"Missing {CLIENT_SECRET}. Download the OAuth client (Desktop app) JSON from Google Cloud Console "
                 "and save it there. See youtube/README.md.")
    c = load_json(CLIENT_SECRET, {})
    return c.get("installed") or c.get("web") or c


def cmd_login():
    c = _client()
    state = secrets.token_urlsafe(16)
    got = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>LinkNode: YouTube login received. You can close this tab.</h2>")

        def log_message(self, *a):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    redirect = f"http://127.0.0.1:{server.server_port}"
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": c["client_id"], "redirect_uri": redirect, "response_type": "code",
        "scope": SCOPE, "access_type": "offline", "prompt": "consent", "state": state})
    print("Opening your browser to sign in to YouTube. If it doesn't open, paste this link:\n" + url)
    webbrowser.open(url)
    server.timeout = 300
    while "code" not in got and "error" not in got:
        server.handle_request()
    server.server_close()
    if got.get("state") != state or "code" not in got:
        sys.exit(f"Login failed: {got.get('error', 'state mismatch')}")
    tok = _post_form(TOKEN_URL, {"code": got["code"], "client_id": c["client_id"],
                                 "client_secret": c["client_secret"], "redirect_uri": redirect,
                                 "grant_type": "authorization_code"})
    tok["obtained_at"] = datetime.now(timezone.utc).isoformat()
    save_json(TOKEN_FILE, tok)
    print("Logged in. Token saved to youtube/token.json (kept off GitHub).")


def access_token():
    tok = load_json(TOKEN_FILE, None)
    if not tok or "refresh_token" not in tok:
        sys.exit("Not logged in. Run: py youtube_uploader.py login")
    c = _client()
    try:
        new = _post_form(TOKEN_URL, {"refresh_token": tok["refresh_token"], "client_id": c["client_id"],
                                     "client_secret": c["client_secret"], "grant_type": "refresh_token"})
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        if "invalid_grant" in body:
            sys.exit("YouTube login has expired or was revoked (invalid_grant).\n"
                     "If this happens every 7 days, your Google Cloud OAuth consent screen is still in 'Testing':\n"
                     "switch it to 'In production', then run: py youtube_uploader.py login")
        raise
    return new["access_token"]


def cmd_check_auth():
    access_token()
    tok = load_json(TOKEN_FILE, {})
    print(f"YouTube login OK. Last full login: {tok.get('obtained_at', 'unknown')}")


# ---------------------------------------------------------------- 4. Upload node
def upload_video(video, meta, cfg, token, upload_url=UPLOAD_URL):
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": bool(cfg["made_for_kids"])}
    if meta.get("publish_at"):
        status["publishAt"] = meta["publish_at"]   # YouTube publishes it at this time; must stay private until then
    body = {"snippet": {"title": meta["title"], "description": meta["description"], "tags": meta.get("tags", []),
                        "categoryId": str(cfg["category_id"]), "defaultLanguage": cfg["default_language"]},
            "status": status}
    size = video.stat().st_size
    ctype = "video/mp4" if video.suffix.lower() in (".mp4", ".m4v") else "application/octet-stream"
    req = urllib.request.Request(upload_url + "?uploadType=resumable&part=snippet,status",
                                 data=json.dumps(body).encode(), method="POST",
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json; charset=UTF-8",
                                          "X-Upload-Content-Type": ctype,
                                          "X-Upload-Content-Length": str(size)})
    with urllib.request.urlopen(req, timeout=60) as r:
        session = r.headers["Location"]

    sent, tries = 0, 0
    with open(video, "rb") as f:
        while sent < size:
            f.seek(sent)
            chunk = f.read(CHUNK)
            end = sent + len(chunk) - 1
            put = urllib.request.Request(session, data=chunk, method="PUT",
                                         headers={"Authorization": f"Bearer {token}",
                                                  "Content-Length": str(len(chunk)),
                                                  "Content-Range": f"bytes {sent}-{end}/{size}"})
            try:
                with urllib.request.urlopen(put, timeout=300) as r:
                    return json.loads(r.read().decode())      # 200/201: upload finished
            except urllib.error.HTTPError as e:
                if e.code == 308:                             # chunk accepted, keep going
                    rng = e.headers.get("Range")
                    sent = int(rng.split("-")[1]) + 1 if rng else 0
                    tries = 0
                    log.info(f"{video.name}: {sent * 100 // size}% uploaded")
                    continue
                if e.code in (500, 502, 503, 504) and tries < 5:
                    tries += 1
                    time.sleep(2 ** tries)
                    continue
                raise RuntimeError(f"YouTube rejected the upload ({e.code}): {e.read().decode(errors='ignore')[:400]}")
    raise RuntimeError("Upload ended without a response from YouTube")


# ---------------------------------------------------------------- 5. Log node
def push_log():
    cmds = [["git", "pull", "--rebase", "--autostash", "origin", "main"],
            ["git", "add", str(UPLOAD_LOG.relative_to(BASE_DIR))],
            ["git", "commit", "-m", "Log YouTube upload"],
            ["git", "push", "origin", "main"]]
    for c in cmds:
        r = subprocess.run(c, cwd=str(BASE_DIR), capture_output=True, text=True)
        if r.returncode != 0 and c[1] != "commit":
            log.warning(f"Could not push the upload log ({' '.join(c[:2])}): {r.stderr.strip()[:200]}")
            return


def cmd_upload():
    cfg = config()
    uploads = load_json(UPLOAD_LOG, [])
    done = {u["file"] for u in uploads}
    queue = []
    for v in videos():
        if v.name in done:
            continue
        meta = load_json(meta_path(v), None)
        if not meta:
            log.info(f"{v.name}: not drafted yet. Run `draft` first.")
            continue
        if not meta.get("approved"):
            log.info(f"{v.name}: waiting for your approval in {meta_path(v).name}")
            continue
        problems = truth_gate(meta, cfg)          # check again: you may have edited it
        if problems:
            log.warning(f"{v.name}: BLOCKED by truth gate, not uploaded -> " + "; ".join(problems))
            continue
        queue.append((v, meta))
    if not queue:
        log.info("Nothing approved to upload.")
        return
    if cfg.get("upload_mode") != "api":
        for v, meta in queue:
            out = v.with_name(v.stem + ".studio.txt")
            out.write_text("Paste into YouTube Studio (Create > Upload videos). Truth gate: PASS.\n\n"
                           f"FILE:\n{v.name}\n\nTITLE:\n{meta['title']}\n\nDESCRIPTION:\n{meta['description']}\n\n"
                           f"TAGS:\n{', '.join(meta.get('tags', []))}\n\n"
                           f"VISIBILITY:\n{'Schedule for ' + meta['publish_at'] if meta.get('publish_at') else 'Private'}\n",
                           encoding="utf-8")
            log.info(f"{v.name}: ready for YouTube Studio -> {out.name}")
        log.info('upload_mode is "studio": nothing was sent to YouTube. See youtube/README.md for why, '
                 'and how to switch to "api" after the audit.')
        return
    token = access_token()
    for v, meta in queue:
        log.info(f"{v.name}: uploading as {'scheduled for ' + meta['publish_at'] if meta.get('publish_at') else 'PRIVATE'}...")
        try:
            res = upload_video(v, meta, cfg, token)
        except Exception as e:
            log.error(f"{v.name}: {e}. Stopping here; nothing else will upload this run.")
            break   # one at a time; never hammer YouTube's quota with retries
        entry = {"file": v.name, "video_id": res["id"], "url": f"https://youtu.be/{res['id']}",
                 "title": meta["title"], "privacy": "private",
                 "publish_at": meta.get("publish_at", ""), "uploaded_at": datetime.now(timezone.utc).isoformat()}
        uploads.append(entry)
        save_json(UPLOAD_LOG, uploads)
        meta["uploaded"] = entry
        save_json(meta_path(v), meta)
        log.info(f"{v.name}: DONE -> {entry['url']} (private until you or publish_at make it public)")
    if cfg.get("push_log_to_github"):
        push_log()


if __name__ == "__main__":
    cmds = {"draft": cmd_draft, "upload": cmd_upload, "check-auth": cmd_check_auth, "login": cmd_login}
    if len(sys.argv) != 2 or sys.argv[1] not in cmds:
        print(__doc__)
        sys.exit(1)
    cmds[sys.argv[1]]()
