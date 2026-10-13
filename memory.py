from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from services.approval_service import is_admin
from storage.json_store import read_json, write_json, audit

router = Router()

def private_denied():
    return "⛔ এটি owner-only কমান্ড।"

@router.message(Command("memory_add"))
async def memory_add(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(private_denied()); return
    raw = message.text.partition(" ")[2]
    if "|" not in raw:
        await message.answer("ব্যবহার: /memory_add key | value"); return
    key, value = [x.strip() for x in raw.split("|", 1)]
    if not key or not value or len(key) > 80 or len(value) > 1000:
        await message.answer("Key/value সঠিক নয়। Key সর্বোচ্চ 80 এবং value 1000 অক্ষর হতে পারে।"); return
    memory = read_json("owner_memory.json", {})
    memory[key] = value
    write_json("owner_memory.json", memory)
    audit("memory_added", message.from_user.id, key)
    await message.answer(f"✅ Owner memory সংরক্ষিত হয়েছে: <code>{key}</code>")

@router.message(Command("memory_list"))
async def memory_list(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(private_denied()); return
    memory = read_json("owner_memory.json", {})
    if not memory:
        await message.answer("Owner memory খালি।"); return
    text = "\n".join(f"• <b>{k}</b>: {v}" for k, v in memory.items())
    await message.answer("🧠 <b>Private Owner Memory</b>\n\n" + text[:3800])

@router.message(Command("memory_delete"))
async def memory_delete(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(private_denied()); return
    key = message.text.partition(" ")[2].strip()
    memory = read_json("owner_memory.json", {})
    if not key or key not in memory:
        await message.answer("এই key পাওয়া যায়নি।"); return
    del memory[key]
    write_json("owner_memory.json", memory)
    audit("memory_deleted", message.from_user.id, key)
    await message.answer("Memory মুছে ফেলা হয়েছে।")
