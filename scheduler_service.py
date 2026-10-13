import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import TIMEZONE, ADMIN_IDS
from storage.json_store import read_json, write_json

log = logging.getLogger(__name__)
scheduler = AsyncIOScheduler(timezone=ZoneInfo(TIMEZONE))

async def _send_task(bot, task_id):
    tasks = read_json("tasks.json", {})
    task = tasks.get(str(task_id))
    if not task or task.get("done"):
        return
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, f"⏰ <b>ARX Reminder</b>\n\n{task['description']}\n\nID: <code>{task_id}</code>")
        except Exception:
            log.exception("Unable to deliver task reminder")
    task["notified"] = True
    write_json("tasks.json", tasks)

async def _publish_campaign(bot, campaign_id):
    campaigns = read_json("campaigns.json", {})
    item = campaigns.get(str(campaign_id))
    if not item or item.get("status") != "approved":
        return
    try:
        await bot.send_message(item["channel"], item["message"])
        item["status"] = "published"
        item["published_at"] = datetime.now(ZoneInfo(TIMEZONE)).isoformat()
    except Exception as exc:
        item["status"] = "failed"
        item["error"] = str(exc)[:200]
        log.exception("Campaign publication failed")
    write_json("campaigns.json", campaigns)

async def start_scheduler(bot):
    if not scheduler.running:
        scheduler.start()
    tasks = read_json("tasks.json", {})
    campaigns = read_json("campaigns.json", {})
    now = datetime.now(ZoneInfo(TIMEZONE))
    for task_id, task in tasks.items():
        if not task.get("done") and not task.get("notified"):
            try:
                run_at = datetime.fromisoformat(task["run_at"])
                if run_at > now:
                    scheduler.add_job(_send_task, "date", run_date=run_at, args=[bot, task_id], id=f"task_{task_id}", replace_existing=True)
            except Exception:
                log.warning("Skipping invalid task %s", task_id)
    for campaign_id, item in campaigns.items():
        if item.get("status") == "approved":
            try:
                run_at = datetime.fromisoformat(item["run_at"])
                if run_at > now:
                    scheduler.add_job(_publish_campaign, "date", run_date=run_at, args=[bot, campaign_id], id=f"campaign_{campaign_id}", replace_existing=True)
            except Exception:
                log.warning("Skipping invalid campaign %s", campaign_id)

async def schedule_task(bot, task_id, run_at):
    scheduler.add_job(_send_task, "date", run_date=run_at, args=[bot, str(task_id)], id=f"task_{task_id}", replace_existing=True)

async def schedule_campaign(bot, campaign_id, run_at):
    scheduler.add_job(_publish_campaign, "date", run_date=run_at, args=[bot, str(campaign_id)], id=f"campaign_{campaign_id}", replace_existing=True)

async def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
