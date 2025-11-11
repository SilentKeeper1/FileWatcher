import os
import time
import hashlib
import json
from datetime import datetime

WATCH_DIR = r"folder"  # path to folder
STATE_FILE = "state.json"
LOG_FILE = "changes.log"
INTERVAL = 5

def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def scan_folder(folder):
    state = {}
    for root, _, files in os.walk(folder):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                state[full_path] = get_file_hash(full_path)
            except Exception:
                pass
    return state

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = f.read().strip()
                if not data:
                    return {} 
                return json.loads(data)
        except json.JSONDecodeError:
            print("state.json is corrupted — creating a new file.")
            return {}
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def log_change(action, file):
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}: {file}\n")

def watch():
    print(f"Watching folder: {WATCH_DIR}")
    old_state = load_state()

    while True:
        new_state = scan_folder(WATCH_DIR)


        for file in new_state.keys() - old_state.keys():
            log_change("Added", file)


        for file in old_state.keys() - new_state.keys():
            log_change("Removed", file)


        for file in new_state.keys() & old_state.keys():
            if new_state[file] != old_state[file]:
                log_change("Modified", file)

        save_state(new_state)
        old_state = new_state

        time.sleep(INTERVAL)

if __name__ == "__main__":
    watch()
