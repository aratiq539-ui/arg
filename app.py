import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_IDS, LOG_LEVEL
from handlers.start import router as start_router
from handlers.chat import router as chat_router
from handlers.admin import router as admin_router
from handlers.memory import router as memory_router
from handlers.tasks import router as tasks_router
from handlers.marketing import router as marketing_router
from services.scheduler_service import start_scheduler, shutdown_scheduler
from storage.json_store import initialize_storage

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("arx")

async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing. Set it in Render Environment Variables.")
    initialize_storage()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    for router in (start_router, chat_router, admin_router, memory_router, tasks_router, marketing_router):
        dp.include_router(router)
    await start_scheduler(bot)
    logger.info("ARX Personal AI Agent starting")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await shutdown_scheduler()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
