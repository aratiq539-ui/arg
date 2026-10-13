from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import TIMEZONE
from services.approval_service import is_admin
from services.scheduler_service import schedule_task
from storage.json_store import read_json, write_json, audit

router = Router()

def parse_date_and_text(raw):
    try:
        date_part, description = raw.split("|", 1)
        run_at = datetime.strptime(date_part.strip(), "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(TIMEZONE))
        return run_at, description.strip()
    except Exception:
        return None, None

@router.message(Command("task_add"))
async def task_add(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Owner-only command."); return
    run_at, description = parse_date_and_text(message.text.partition(" ")[2])
    if not run_at or not description:
        await message.answer("ব্যবহার: /task_add YYYY-MM-DD HH:MM | কাজের বিবরণ\nসময় Asia/Dhaka timezone অনুযায়ী।"); return
    if run_at <= datetime.now(ZoneInfo(TIMEZONE)):
        await message.answer("ভবিষ্যতের তারিখ ও সময় দিন।"); return
    settings = read_json("settings.json", {})
    task_id = int(settings.get("next_task_id", 1))
    settings["next_task_id"] = task_id + 1
    write_json("settings.json", settings)
    tasks = read_json("tasks.json", {})
    tasks[str(task_id)] = {"description": description[:1000], "run_at": run_at.isoformat(), "done": False, "notified": False, "created_by": message.from_user.id}
    write_json("tasks.json", tasks)
    await schedule_task(message.bot, task_id, run_at)
    audit("task_created", message.from_user.id, str(task_id))
    await message.answer(f"✅ Reminder তৈরি হয়েছে।\nID: <code>{task_id}</code>\nসময়: {run_at:%d-%m-%Y %H:%M}\nকাজ: {description}")

@router.message(Command("tasks"))
async def tasks_list(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Owner-only command."); return
    tasks = read_json("tasks.json", {})
    if not tasks:
        await message.answer("কোনো task নেই।"); return
    lines = []
    for tid, item in tasks.items():
        state = "Done" if item.get("done") else ("Notified" if item.get("notified") else "Pending")
        lines.append(f"#{tid} [{state}] {item['run_at']}\n{item['description']}")
    await message.answer("📋 <b>Your tasks</b>\n\n" + "\n\n".join(lines)[:3800])

@router.message(Command("task_done"))
async def task_done(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Owner-only command."); return
    tid = message.text.partition(" ")[2].strip()
    tasks = read_json("tasks.json", {})
    if tid not in tasks:
        await message.answer("Task ID পাওয়া যায়নি।"); return
    tasks[tid]["done"] = True
    write_json("tasks.json", tasks)
    audit("task_done", message.from_user.id, tid)
    await message.answer(f"Task #{tid} সম্পন্ন হিসেবে চিহ্নিত হয়েছে।")
