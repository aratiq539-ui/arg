import os

def _csv_ints(value):
    result = set()
    for part in (value or "").split(","):
        part = part.strip()
        if part.isdigit():
            result.add(int(part))
    return result

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_IDS = _csv_ints(os.getenv("ADMIN_IDS", ""))
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
AI_MODEL = os.getenv("AI_MODEL", "gemini-2.5-flash").strip()
AI_BASE_URL = os.getenv("AI_BASE_URL", "").strip()
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
TIMEZONE = os.getenv("TIMEZONE", "Asia/Dhaka").strip()
DATA_DIR = os.getenv("DATA_DIR", "./data").strip()
BACKUP_DIR = os.getenv("BACKUP_DIR", "./backups").strip()
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_DAILY_USER_MESSAGES = int(os.getenv("MAX_DAILY_USER_MESSAGES", "50"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4000"))
OWNER_APPROVAL_REQUIRED = os.getenv("OWNER_APPROVAL_REQUIRED", "true").lower() != "false"
