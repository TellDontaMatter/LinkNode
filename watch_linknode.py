import time
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
NOTES_DIR = Path(r"C:\LinkNode\notes")
APP_SCRIPT = Path(r"C:\LinkNode\app.py")
REPO_DIR = Path(r"C:\LinkNode")
POLL_INTERVAL = 3  # Check for changes every 3 seconds

def get_folder_state(directory: Path):
    """Returns a dictionary mapping file paths to their last modified timestamps."""
    state = {}
    if not directory.exists():
        return state
    for md_file in directory.rglob("*.md"):
        try:
            state[str(md_file)] = md_file.stat().st_mtime
        except OSError:
            pass
    return state

def pull_latest():
    """Bring down anything changed on GitHub (online edits, Claude's PRs) before building.
    Returns True if the local copy is up to date and safe to push from."""
    res = subprocess.run(["git", "pull", "--rebase", "--autostash", "origin", "main"],
                         cwd=str(REPO_DIR), capture_output=True, text=True)
    if res.returncode == 0:
        if "Already up to date" not in res.stdout:
            print("[PULL] Got the latest changes from GitHub.")
        return True
    # Leave the folder clean instead of half-merged
    subprocess.run(["git", "rebase", "--abort"], cwd=str(REPO_DIR), capture_output=True, text=True)
    print(f"[ERROR] Could not pull from GitHub, so nothing was pushed:\n{res.stderr}")
    return False

def sync_and_deploy():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] Change detected in notes! Rebuilding graph...")

    # 0. Pull first so the push can't be rejected for being behind
    if not pull_latest():
        return

    # 1. Run app.py to rebuild graph.json and Index.html
    build_res = subprocess.run(["py", str(APP_SCRIPT)], cwd=str(REPO_DIR), capture_output=True, text=True)
    if build_res.returncode != 0:
        print(f"[ERROR] app.py failed:\n{build_res.stderr}")
        return
    print("[OK] graph.json rebuilt.")

    # 2. Check if Git has changes to commit
    status_res = subprocess.run(["git", "status", "--porcelain"], cwd=str(REPO_DIR), capture_output=True, text=True)
    if not status_res.stdout.strip():
        print("[INFO] No new Git changes to push.")
        return

    # 3. Stage, commit, and push to GitHub Pages
    subprocess.run(["git", "add", "."], cwd=str(REPO_DIR), check=True)
    commit_msg = f"Auto-update LinkNode graph ({timestamp})"
    subprocess.run(["git", "commit", "-m", commit_msg], cwd=str(REPO_DIR), check=True)
    
    print("[PUSH] Pushing updates to GitHub...")
    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO_DIR), capture_output=True, text=True)
    if push_res.returncode != 0 and pull_latest():
        # Something landed on GitHub mid-build: pull it and try once more
        push_res = subprocess.run(["git", "push", "origin", "main"], cwd=str(REPO_DIR), capture_output=True, text=True)
    if push_res.returncode == 0:
        print(f"[SUCCESS] Live graph updated! ({commit_msg})")
    else:
        print(f"[ERROR] Git push failed:\n{push_res.stderr}")

def main():
    print(f"Watching {NOTES_DIR} for new or modified markdown files...")
    print("Press Ctrl+C to stop.")
    pull_latest()  # catch up on anything changed online while the watcher was off
    last_state = get_folder_state(NOTES_DIR)
    
    while True:
        time.sleep(POLL_INTERVAL)
        current_state = get_folder_state(NOTES_DIR)
        if current_state != last_state:
            # Brief debounce to ensure file writes finish
            time.sleep(1)
            sync_and_deploy()
            last_state = get_folder_state(NOTES_DIR)

if __name__ == "__main__":
    main()
