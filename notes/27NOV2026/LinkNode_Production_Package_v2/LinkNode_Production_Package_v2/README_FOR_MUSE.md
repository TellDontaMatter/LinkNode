# LinkNode Production Package v2 — FOR MUSE
## How to use this folder

You are Muse. Your job is to SCHEDULE the supporting Zuckerverse content for this package.

**Zuckerverse = Meta surfaces:** Facebook (Page / Reels), Instagram (Feed / Reels / Stories), Threads

**DO NOT re-generate scripts.** The scripts in this folder are final. Your job is scheduling + captions + hashtags + cross-post mapping.

### 1. Face Behind The Voice — LOCKED RULE
- Host = face behind the voice. Voice = always him. Face = selective.
- MEMES + STINGERS: NO face. Text + graph + high-contrast design only.
- SHORTS 10s / 30s: VOICE ONLY + screen capture. No face on camera.
- MID / LONG EXPLAINERS: Face for HOOK (first 5s) + CLOSER (last 5s) only. Body = screen + voiceover.
- MASTERCLASSES: Full host. On-camera hook, screen walkthrough, on-camera closer.
- THUMBNAILS: Face ALLOWED. Bold text + graph + face.

Host look (for thumbnails / hooks / closers only): Bald, glasses, salt-and-pepper beard, red-and-blue striped hoodie, brown cargo pants, brown boots. Dark-mode workspace behind him.

Voice: Calm, razor-sharp, zero hyperbole, developer-first.

### 2. Folder Map
- `memes/` — 8 still memes, text + graph, NO face
- `stingers/` — 8 x 1s motion cuts from memes, NO face
- `shorts_10s/` — 9 x 10s, voice + screen only
- `shorts_30s/` — 3 x 30s, stitched from 10s clips, voice + screen only
- `mid_form/` — 3 x 90s explainers, face hook/closer only
- `long_form/` — 3 x 3-5 min explainers, face hook/closer only
- `masterclasses/` — 4 x 8-12 min teleprompter scripts, full host
- `scheduling/` — `schedule.json` + `schedule.csv` + `captions.md` — USE THESE TO SCHEDULE

### 3. Scheduling Instructions for Muse
1. Read `scheduling/schedule.json` — it is the source of truth for order, platform, format, and caption file.
2. Read `scheduling/captions.md` for ready-to-paste captions + hashtags per asset.
3. Schedule in this order: Memes first to seed, then Shorts daily, then Mid/Long, then Masterclasses as pillars.
4. Cross-post rule:
   - Facebook: Meme image + long caption + link to masterclass
   - Instagram: Reel / Carousel + short punchy caption
   - Threads: Text hook + 1 line takeaway + link
5. Do NOT put host face in meme posts. Do NOT crop host face into meme images.
6. For Shorts: caption must say "Voiceover + screen" — do not promise on-camera.
7. For Masterclasses: caption must say "Full episode — host on camera" — this is the only tier where face is the promise.
8. Keep Evidence First: do not invent stats. If a caption claims a number, it must come from the script file.

### 4. Project Context (for captions)
LinkNode = Local Python + Ollama (qwen2.5:7b on localhost:11434) pipeline that turns raw markdown notes with [[ ]] links into structured JSON graph (graph.json) + interactive D3.js force graph (index.html). No cloud. No subscriptions. Total ownership.
Git track = Local Git on Windows, .gitignore, `git rm -r --cached .`, fixing index limits, GitHub Pages deploy.

### 5. What to return after scheduling
- Confirmation list: asset -> platform -> scheduled date/time -> caption used
- Any asset you could NOT schedule + why
- Do not re-write scripts.
