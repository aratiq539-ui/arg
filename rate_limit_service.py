from datetime import date
from storage.json_store import read_json, write_json
from config import MAX_DAILY_USER_MESSAGES

def allow_message(user_id: int) -> bool:
    today = date.today().isoformat()
    users = read_json("users.json", {})
    user = users.get(str(user_id), {})
    usage = user.get("usage", {})
    count = usage.get(today, 0)
    if count >= MAX_DAILY_USER_MESSAGES:
        return False
    usage[today] = count + 1
    # keep only the current day to limit file growth
    user["usage"] = {today: usage[today]}
    user["last_seen"] = today
    users[str(user_id)] = user
    write_json("users.json", users)
    return True
