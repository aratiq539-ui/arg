from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import TIMEZONE
from services.approval_service import is_admin
from services.marketing_service import create_marketing_copy
from services.scheduler_service import schedule_campaign
from storage.json_store import read_json, write_json, audit

router = Router()

@router.message(Command("marketing"))
async def marketing(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ এই ফিচারটি Admin-only।"); return
    brief = message.text.partition(" ")[2].strip()
    if not brief:
        await message.answer("ব্যবহার: /marketing আপনার অ্যাপ/সার্ভিস ও লক্ষ্য লিখুন"); return
    await message.bot.send_chat_action(message.chat.id, "typing")
    result = await create_marketing_copy(message.from_user.id, brief, is_admin=True)
    await message.answer("📣 <b>Marketing Draft</b>\n\n" + result[:3800])

@router.message(Command("campaign"))
async def campaign(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Admin-only."); return
    raw = message.text.partition(" ")[2]
    try:
        date_part, channel, content = [x.strip() for x in raw.split("|", 2)]
        run_at = datetime.strptime(date_part, "%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo(TIMEZONE))
        if not channel or not content:
            raise ValueError()
        if run_at <= datetime.now(ZoneInfo(TIMEZONE)):
            await message.answer("ভবিষ্যতের সময় দিতে হবে।"); return
    except Exception:
        await message.answer("ব্যবহার: /campaign YYYY-MM-DD HH:MM | @channel_username | পোস্টের লেখা"); return
    settings = read_json("settings.json", {})
    cid = int(settings.get("next_campaign_id", 1))
    settings["next_campaign_id"] = cid + 1
    write_json("settings.json", settings)
    campaigns = read_json("campaigns.json", {})
    campaigns[str(cid)] = {"channel": channel, "message": content[:3800], "run_at": run_at.isoformat(), "status": "pending_approval", "created_by": message.from_user.id}
    write_json("campaigns.json", campaigns)
    audit("campaign_draft_created", message.from_user.id, str(cid))
    await message.answer(f"📝 Campaign draft #{cid} তৈরি হয়েছে। প্রকাশ করতে /approve {cid} দিন।")

@router.message(Command("approvals"))
async def approvals(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Admin-only."); return
    campaigns = read_json("campaigns.json", {})
    pending = [(cid, x) for cid, x in campaigns.items() if x.get("status") == "pending_approval"]
    if not pending:
        await message.answer("Pending approval নেই।"); return
    text = "\n\n".join(f"#{cid} → {x['channel']} at {x['run_at']}\n{x['message'][:200]}" for cid, x in pending)
    await message.answer("⏳ <b>Pending Campaigns</b>\n\n" + text[:3800])

@router.message(Command("approve"))
async def approve(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Admin-only."); return
    cid = message.text.partition(" ")[2].strip()
    campaigns = read_json("campaigns.json", {})
    item = campaigns.get(cid)
    if not item or item.get("status") != "pending_approval":
        await message.answer("Pending campaign পাওয়া যায়নি।"); return
    run_at = datetime.fromisoformat(item["run_at"])
    if run_at <= datetime.now(ZoneInfo(TIMEZONE)):
        await message.answer("Campaign-এর সময় পেরিয়ে গেছে। নতুন draft তৈরি করুন।"); return
    item["status"] = "approved"
    item["approved_by"] = message.from_user.id
    write_json("campaigns.json", campaigns)
    await schedule_campaign(message.bot, cid, run_at)
    audit("campaign_approved", message.from_user.id, cid)
    await message.answer(f"✅ Campaign #{cid} approved এবং schedule করা হয়েছে। নিশ্চিত করুন bot-টি target channel-এ post করার permission পেয়েছে।")

@router.message(Command("cancel_campaign"))
async def cancel_campaign(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Admin-only."); return
    cid = message.text.partition(" ")[2].strip()
    campaigns = read_json("campaigns.json", {})
    item = campaigns.get(cid)
    if not item:
        await message.answer("Campaign পাওয়া যায়নি।"); return
    item["status"] = "cancelled"
    write_json("campaigns.json", campaigns)
    try:
        from services.scheduler_service import scheduler
        job = scheduler.get_job(f"campaign_{cid}")
        if job:
            job.remove()
    except Exception:
        pass
    audit("campaign_cancelled", message.from_user.id, cid)
    await message.answer(f"Campaign #{cid} cancelled.")
