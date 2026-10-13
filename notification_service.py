async def notify_admins(bot, admin_ids, message):
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, message)
        except Exception:
            pass
