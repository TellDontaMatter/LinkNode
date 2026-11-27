# LinkNode Production Capsule — v2
## Face Behind The Voice

### The Host — Role Lock
The host is the FACE BEHIND THE VOICE. He is not a meme character.

- **Voice = Always him.** Every narration, every short, every explainer, every masterclass is voiced by him.
- **Face = Selective.** He appears on camera only where it adds trust and identity: hooks, closers, thumbnails, masterclass intros/outros.
- **Memes = No face.** Memes and stingers stay clean: text + graph + high-contrast design. No character in the frame.

### Host Appearance — For On-Camera / Thumbnail Use Only
- Bald, glasses, short salt-and-pepper beard
- Red-and-blue striped hoodie
- Brown cargo pants, brown boots
- Warm, confident smile, direct to camera
- Setting: dark-mode workspace, code / graph on screen behind him, not a fake studio

### Voice Profile — Locked
Calm, razor-sharp, zero hyperbole, developer-first.
No hype. No shouting. Explain like a builder talking to another builder.

Example line from the LinkNode script:
> "Your markdown notes are sitting in a folder. You can search them. You can grep them. But you can't *see* how they connect."

### Project Context
- Pipeline Architecture: Local Python + Ollama (qwen2.5:7b) + Obsidian-style [[ ]] links
- Tooling: Python `pathlib`, `re`, `json`, `urllib.request`
- Oldman (qwen2.5:7b) on port 11434, parsing raw markdown notes into structured JSON graphs (graph.json) and interactive D3.js web visualizations (index.html)
- Deployment: Version Control — Local Git Repositories on Windows, with cleaned .gitignore rules, excluding .crdownload, large binaries, .DS_Store, deployed live via GitHub Pages, rendered at github.io/LinkNode/

### Audio Production Format
Voiceover narration scripts must include inline [bracketed production notes] for ElevenLabs pacing, e.g. [1.5 seconds pause for ElevenLabs pacing], and pause cues, e.g. [pause], [beat].

### Operating Rules
1. **Evidence First:** Every claim, stat, or technical detail in the output must tie directly to audited text files or source docs in the repository. Do not hallucinate or extrapolate unverified facts.
2. **Zero Cloud Dependency:** All outputs must be structured cleanly as local markdown files, scripts, or JSON manifests ready for local execution or rendering.
3. **Strict Formatting:** Follow the exact volume, runtime quotas, and structure specifications below without truncation.

---

## Required Deliverables

### Phase 1: Visual / Graphic Assets — NO HOST FACE
**8 Still Memes:**
- Provide visual layout instructions, exact top/bottom text overlays, and high-contrast developer-focused aesthetics
- Topics: Local AI vs. Cloud Privacy, Markdown Notes / Hardening, Git Workflow Struggles
- Format: Text + graph + design only. Do NOT put the host in memes.

**8 Video Stingers (1s each):**
- Direct motion-graphic cuts derived directly from the 8 still memes above to serve as rapid intros or scene transitions
- Format: Motion graphic only. No host face. Voice sting optional, no on-camera.

### Phase 2: Short-Form Social Clips / Shorts — VOICE ONLY + SCREEN
**9 Short-Form Videos (10s each):**
- High-impact, rapid-fire vertical video scripts focusing on single troubleshooting wins or quick technical wins (e.g. clearing .crdownload files, fixing Git index limits, running local Ollama endpoints)
- Format: Screen capture (Terminal / VS Code / Graph) + host voiceover. No face on camera.

**3 Short-Form Videos (30s each):**
- Synthesized reels created by stitching together the sets of the 10s clips into cohesive mini-narratives with smooth transitions
- Format: Screen + voiceover only. No face.

### Phase 3: Mid-Form / Long-Form Explainers — VOICE + SCREEN, FACE FOR HOOK / CLOSER ONLY
**3 Mid-Form Explainers (90s each):**
- Expanded breakdowns taking the 30s reels and adding narration context, explaining why local-first workflows matter
- Format: Hook (0-5s): Host on camera, direct to camera. Body: Screen + voiceover. Closer (last 5s): Host on camera optional.
- Example: LinkNode Build — how raw markdown becomes a JSON graph.

**3 Long-Form Explainers (3-5 min each):**
- Deep technical guides walking through the code architecture, data flow, and local LLM prompt play
- Format: Hook: Host on camera. Body: Screen + voiceover. Closer: Host on camera.
- Example: Git Repository Build — Initialize local repos on Windows, configure .gitignore, clear cached staging, manage file sizes safely.

### Phase 4: Core Pillar Masterclass Videos (8-12 min each) — FULL HOST PRESENCE
Generate complete, step-by-step teleprompter-ready video scripts, complete with bracketed production notes and ElevenLabs pacing cues, for the following 4 pillar videos:

1. **LinkNode Build Video:** How to write the Python parser that transforms raw markdown notes into structured JSON graphs (graph.json) and D3.js force graphs (index.html).
2. **Git Repository Build Video:** Initializing local repos on Windows, setting up .gitignore rules, clearing cached staging errors with `git rm -r --cached .`, and managing file sizes safely on Windows.
3. **Git Hosting Video:** Bypassing GitHub Pages deployment hurdles, pushing to main, and publishing live.
4. **The Guru Video Master Integration:** A comprehensive masterclass tying local AI, knowledge graphs, Git version control, and automated multi-tier content pipelines into a single unified local-first workflow.

**Masterclass Format:**
- Cold Hook (0-30s): Host on camera
- Act 1-4: Screen + voiceover (code, terminal, graph)
- Closing Beat: Host on camera + title graphic sting

---

## Thumbnail Rule
Thumbnails MAY use host face + bold text + graph.
Memes may NOT use host face.

## What Changed in v2
- v1 left host usage ambiguous.
- v2 locks it: Memes = no face. Shorts = voice only. Explainers = face for hook/closer only. Masterclasses = full host presence.
- This keeps memes fast/shareable, builds voice recognition, and saves face appearances for moments that build trust.
