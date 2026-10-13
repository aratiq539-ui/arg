# ARX Personal AI Agent

A Telegram AI assistant built with Python, aiogram 3, Gemini API, JSON storage, and APScheduler.

## Features
- Public AI chat with per-user conversation histories
- Owner-only commands and private memory
- Task/reminder creation and scheduled notifications
- Marketing copy generation and draft scheduling
- Admin approval before publishing/sending campaign drafts
- JSON data storage and Render deployment configuration

## Local run
1. Install Python 3.11+.
2. `python -m venv .venv`
3. Activate the environment.
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and set `BOT_TOKEN`, `ADMIN_IDS`, and `GEMINI_API_KEY`.
6. `python app.py`

## Render deployment (recommended: Background Worker)
1. Push this folder to a private GitHub repository.
2. In Render, create a new **Background Worker** from that repository, or use the supplied `render.yaml` Blueprint.
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add environment variables: `BOT_TOKEN`, `ADMIN_IDS`, `GEMINI_API_KEY`.
6. Add a persistent disk mounted at `/var/data`; set `DATA_DIR=/var/data`.
7. Deploy and inspect logs. Send `/start` to the bot.

Important: JSON files on Render's ordinary ephemeral filesystem can be lost on redeploy/restart. Use a persistent disk for JSON storage. Persistent disks may require a paid Render plan; check current Render plan terms. Do not run multiple worker instances against the same JSON files.

## Admin commands
- `/admin` — admin menu
- `/memory_add key | value` — save owner-only personal memory
- `/memory_list` — list saved memory keys and values privately
- `/memory_delete key` — delete a memory
- `/task_add YYYY-MM-DD HH:MM | task description` — schedule a reminder in Asia/Dhaka
- `/tasks` — list owner tasks
- `/task_done TASK_ID` — mark task done
- `/marketing` — create marketing content
- `/campaign YYYY-MM-DD HH:MM | channel_username | message` — save a campaign draft for approval
- `/approvals` — list pending drafts
- `/approve CAMPAIGN_ID` — approve and schedule publication
- `/cancel_campaign CAMPAIGN_ID` — cancel a draft

## Safety notes
- Never commit `.env`, tokens, API keys, or JSON data files.
- Only IDs in `ADMIN_IDS` can use owner/admin commands.
- The bot does not execute arbitrary shell commands or user-uploaded code.
- Campaign posting requires the bot to be an admin in the target channel with permission to post.
- Do not use this bot for unsolicited spam. Obtain consent and comply with Telegram rules.
- This initial implementation uses JSON files; for heavy multi-user production workloads, migrate to a transactional database.
