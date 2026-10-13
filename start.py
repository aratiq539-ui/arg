from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from storage.json_store import read_json, write_json

router = Router()

def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="💬 AI Chat", callback_data="menu_chat")
    kb.button(text="✍️ Writing Assistant", callback_data="menu_writing")
    kb.button(text="📣 Marketing Ideas", callback_data="menu_marketing")
    kb.button(text="⚙️ Settings", callback_data="menu_settings")
    kb.button(text="❓ Help & Privacy", callback_data="menu_help")
    kb.adjust(2, 1, 2)
    return kb.as_markup()

@router.message(CommandStart())
async def start(message: Message):
    users = read_json("users.json", {})
    users[str(message.from_user.id)] = {
        **users.get(str(message.from_user.id), {}),
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "blocked": False,
    }
    write_json("users.json", users)
    await message.answer(
        "👋 <b>Welcome to ARX Personal AI Agent!</b>\n\n"
        "আপনার স্মার্ট AI সহকারী। প্রশ্নের উত্তর, লেখা, পড়াশোনা, আইডিয়া ও পরিকল্পনায় সাহায্য করতে পারি।\n\n"
        "নিচের মেনু থেকে শুরু করুন।",
        reply_markup=main_keyboard()
    )

@router.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "<b>ARX AI Help</b>\n"
        "/start — Main menu\n/chat — AI chat\n/newchat — Reset conversation\n"
        "/privacy — Privacy information\n/clearhistory — Delete chat history\n"
        "Admin-only: /admin, /memory_add, /memory_list, /memory_delete, /task_add, /tasks, /marketing"
    )

@router.message(Command("myid"))
async def myid(message: Message):
    await message.answer(f"Your Telegram ID: <code>{message.from_user.id}</code>")

@router.message(Command("privacy"))
async def privacy(message: Message):
    await message.answer(
        "🔐 <b>Privacy</b>\nআপনার কথোপকথন উত্তর তৈরি ও ধারাবাহিকতা বজায় রাখার জন্য সংরক্ষণ করা হতে পারে। "
        "ব্যক্তিগত owner memory শুধু অনুমোদিত admin-এর জন্য। /clearhistory দিয়ে নিজের chat history মুছতে পারবেন। "
        "কোনো গোপন তথ্য, পাসওয়ার্ড বা API key পাঠাবেন না।"
    )

@router.message(Command("clearhistory"))
async def clearhistory(message: Message):
    data = read_json("conversations.json", {})
    data.pop(str(message.from_user.id), None)
    write_json("conversations.json", data)
    await message.answer("আপনার conversation history মুছে ফেলা হয়েছে।")

@router.message(Command("newchat"))
async def newchat(message: Message):
    data = read_json("conversations.json", {})
    data.pop(str(message.from_user.id), None)
    write_json("conversations.json", data)
    await message.answer("নতুন chat শুরু হয়েছে। এখন আপনার প্রশ্ন পাঠান।")

@router.message(Command("settings"))
async def settings(message: Message):
    await message.answer("⚙️ Settings\nভাষা: স্বয়ংক্রিয় (বাংলা/Banglish/English)\nChat history মুছতে /clearhistory ব্যবহার করুন।")

@router.callback_query(F.data.startswith("menu_"))
async def menu_callback(callback: CallbackQuery):
    choices = {
        "menu_chat": "আপনার প্রশ্ন লিখে পাঠান। আমি সাহায্য করার চেষ্টা করব।",
        "menu_writing": "কী ধরনের লেখা চান—চিঠি, পোস্ট, ক্যাপশন বা অন্য কিছু—বিস্তারিত লিখুন।",
        "menu_marketing": "কোন অ্যাপ/সার্ভিসের জন্য মার্কেটিং আইডিয়া চান? নাম ও তথ্য লিখুন।",
        "menu_settings": "Settings: /settings\nChat history মুছতে: /clearhistory",
        "menu_help": "সাহায্য: /help\nPrivacy: /privacy"
    }
    await callback.message.answer(choices.get(callback.data, "মেনু অপশন পাওয়া যায়নি।"))
    await callback.answer()
