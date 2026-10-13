from services.ai_service import generate_reply

async def create_marketing_copy(user_id: int, brief: str, is_admin: bool = True) -> str:
    prompt = (
        "Create a marketing content package based on this brief. Return: (1) short campaign idea, "
        "(2) one polished Bengali promotional post, (3) one short Telegram caption, (4) a call to action, "
        "(5) optional hashtags. Do not invent prices, guarantees, user counts, or product features. "
        "Clearly mark unknown facts as placeholders.\n\nBrief:\n" + brief
    )
    return await generate_reply(user_id, prompt, is_admin=is_admin)
