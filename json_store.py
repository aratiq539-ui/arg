import json, os, threading, tempfile
from pathlib import Path
from config import DATA_DIR

_LOCK = threading.RLock()
DEFAULTS = {
    "users.json": {},
    "conversations.json": {},
    "owner_memory.json": {},
    "tasks.json": {},
    "reminders.json": {},
    "campaigns.json": {},
    "approvals.json": {},
    "settings.json": {"next_task_id": 1, "next_campaign_id": 1},
    "audit_log.json": []
}

def data_path(name):
    return Path(DATA_DIR) / name

def initialize_storage():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    for name, default in DEFAULTS.items():
        path = data_path(name)
        if not path.exists():
            write_json(name, default)

def read_json(name, default=None):
    with _LOCK:
        path = data_path(name)
        if not path.exists():
            return default if default is not None else DEFAULTS.get(name, {})
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Fail closed; never overwrite a corrupt file automatically.
            raise RuntimeError(f"Storage file {name} is unreadable. Back it up and repair it.")

def write_json(name, value):
    with _LOCK:
        path = data_path(name)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=str(path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_name, path)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

def audit(event, actor_id, details=""):
    rows = read_json("audit_log.json", [])
    rows.append({"event": event, "actor_id": str(actor_id), "details": str(details)[:300]})
    write_json("audit_log.json", rows[-1000:])
