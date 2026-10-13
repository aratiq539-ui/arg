from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS
from services.approval_service import is_admin
from storage.json_store import read_json, write_json, audit

router = Router()

def denied():
    return "⛔ এই কমান্ডটি শুধু অনুমোদিত Admin ব্যবহার করতে পারবেন."

@router.message(Command("admin"))
async def admin(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(denied()); return
    await message.answer(
        "🛡️ <b>ARX Admin Panel</b>\n\n"
        "/memory_add key | value\n/memory_list\n/memory_delete key\n"
        "/task_add YYYY-MM-DD HH:MM | description\n/tasks\n/task_done TASK_ID\n"
        "/marketing brief\n/campaign YYYY-MM-DD HH:MM | @channel | message\n"
        "/approvals\n/approve CAMPAIGN_ID\n/cancel_campaign CAMPAIGN_ID\n"
        "/stats — usage stats"
    )

@router.message(Command("stats"))
async def stats(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(denied()); return
    users = read_json("users.json", {})
    tasks = read_json("tasks.json", {})
    campaigns = read_json("campaigns.json", {})
    await message.answer(f"📊 Users: {len(users)}\nTasks: {len(tasks)}\nCampaigns: {len(campaigns)}")

@router.message(Command("block"))
async def block(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(denied()); return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("ব্যবহার: /block TELEGRAM_USER_ID"); return
    target = parts[1]
    users = read_json("users.json", {})
    users.setdefault(target, {})["blocked"] = True
    write_json("users.json", users)
    audit("user_blocked", message.from_user.id, target)
    await message.answer(f"User {target} blocked.")

@router.message(Command("unblock"))
async def unblock(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(denied()); return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("ব্যবহার: /unblock TELEGRAM_USER_ID"); return
    target = parts[1]
    users = read_json("users.json", {})
    users.setdefault(target, {})["blocked"] = False
    write_json("users.json", users)
    audit("user_unblocked", message.from_user.id, target)
    await message.answer(f"User {target} unblocked.")
