# LinkNode YouTube uploader

`youtube_uploader.py` turns a finished video into YouTube-ready metadata, checks it against the truth gate, and (once allowed) uploads it.

```
video + script in youtube\approved\
   -> Qwen drafts title, description, tags      (py youtube_uploader.py draft)
   -> truth gate blocks anything on the NOT BUILT list
   -> you review <video>.metadata.json and set "approved": true
   -> upload step                                (py youtube_uploader.py upload)
        studio mode (default): writes <video>.studio.txt to paste into YouTube Studio
        api mode (after audit): uploads PRIVATE or scheduled, logs the link to youtube\uploads.json
```

Nothing is ever uploaded as public. Videos, metadata, your login token and your Google client file stay on your PC (they're in `.gitignore`).

## Why "studio" mode is the default

YouTube locks every video uploaded through the API from an **unverified (unaudited) Google Cloud project** to private, and that lock can't be appealed or removed later. You'd have to re-upload. So until your project passes YouTube's API audit, the script does everything except the final upload and gives you paste-ready text for YouTube Studio.

To get the audit: fill in the "YouTube API Services - Audit and Quota Extension Form" for your project. When it's approved, put this in `youtube\config.json`:

```json
{ "upload_mode": "api" }
```

## One-time setup (only needed for "api" mode and `check-auth`)

1. **Google Cloud Console:** pick or create a project, then enable **YouTube Data API v3**.
2. **OAuth consent screen** (newer consoles: Google Auth Platform → Audience): User type **External**, add the scope `.../auth/youtube.upload`, and set the publishing status to **In production**. If you leave it in Testing, the login dies every 7 days.
3. **Credentials:** Create OAuth client ID → **Desktop app**. Download the JSON and save it as `C:\LinkNode\youtube\client_secret.json`.
4. Run `py youtube_uploader.py login`. Your browser opens. Google will warn that the app is unverified: click **Advanced → Go to (app name)**. That's expected for your own app.
5. Run `py youtube_uploader.py check-auth`. It should say "YouTube login OK."

Draft mode only needs Ollama running with `qwen2.5:7b`. No Google setup required.

## Everyday use

1. Put the finished video and its script, with the same name, in `youtube\approved\`, for example `short10_03.mp4` + `short10_03.md`.
2. `py youtube_uploader.py draft`. Qwen writes `short10_03.metadata.json`, and the gate marks it PASS or BLOCKED and says why.
3. Open the metadata file. Edit anything you like, set `"approved": true`, and optionally set `"publish_at": "2026-12-06T18:00:00-05:00"`. Run `draft` again to re-check your edits.
4. `py youtube_uploader.py upload`.

## Settings (`youtube\config.json`, all optional)

| Setting | Default | Meaning |
|---|---|---|
| `upload_mode` | `"studio"` | `"api"` only after the audit |
| `category_id` | `"28"` | Science & Technology |
| `masterclass_links_live` | `false` | set `true` once the masterclasses are published, so captions may mention them |
| `push_log_to_github` | `true` | commit `youtube\uploads.json` so Claude can pass links to Muse |
| `footer` | live graph link | added to every description |

## The truth gate

`youtube\truth_gate.json` lists the claims LinkNode can't make yet ([[ ]] links, regex, D3.js, made-up numbers, products for sale...). It matches the LinkNode Truth Sheet in the Claude + Muse Workspace. When a feature ships, Claude updates both.

## Limits worth knowing

- YouTube allows a limited number of API uploads per project per day. The script uploads one at a time and stops on the first error instead of retrying.
- Titles: max 100 characters. Descriptions: max 5000 bytes. No `<` or `>` anywhere. The gate checks these.
- Chapters aren't drafted, because Qwen doesn't know the timestamps. Add `0:00 Intro` style lines to the description yourself if you want them.
