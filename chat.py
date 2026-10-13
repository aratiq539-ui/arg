from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from config import ADMIN_IDS
from services.ai_service import generate_reply
from services.rate_limit_service import allow_message
from storage.json_store import read_json

router = Router()

@router.message(Command("chat"))
async def chat_command(message: Message):
    await message.answer("আপনার প্রশ্ন লিখে পাঠান।")

@router.message(Command("feedback"))
async def feedback(message: Message):
    text = message.text.partition(" ")[2].strip()
    if not text:
        await message.answer("ব্যবহার: /feedback আপনার মতামত")
        return
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await message.bot.send_message(admin_id, f"📝 Feedback from {message.from_user.id}:\n{text[:1500]}")
        except Exception:
            pass
    await message.answer("ধন্যবাদ! আপনার feedback পাঠানো হয়েছে।")

@router.message()
async def public_chat(message: Message):
    if not message.text or message.text.startswith("/"):
        return
    users = read_json("users.json", {})
    user = users.get(str(message.from_user.id), {})
    if user.get("blocked"):
        await message.answer("আপনার বট ব্যবহারের অনুমতি বন্ধ করা হয়েছে।")
        return
    if not allow_message(message.from_user.id):
        await message.answer("আজকের free message limit শেষ হয়েছে। পরে আবার চেষ্টা করুন।")
        return
    is_admin = message.from_user.id in ADMIN_IDS
    await message.bot.send_chat_action(message.chat.id, "typing")
    answer = await generate_reply(message.from_user.id, message.text, is_admin=is_admin)
    await message.answer(answer)
