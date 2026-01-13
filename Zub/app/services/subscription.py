import httpx
from app.config import settings

async def telegram_check_subscription(telegram_user_id: str) -> bool:
    """
    Check membership in clinic channel/group.
    Bot often must be admin in the channel to query membership.
    """
    chat_id = settings.TELEGRAM_REQUIRED_CHAT_ID
    if not settings.TELEGRAM_BOT_TOKEN or not chat_id:
        return True

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getChatMember"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params={"chat_id": chat_id, "user_id": telegram_user_id})
        if r.status_code != 200:
            return False
        data = r.json()
        if not data.get("ok"):
            return False
        status = data["result"]["status"]
        return status in ("member", "administrator", "creator")

async def vk_check_subscription(vk_user_id: str, vk_access_token: str) -> bool:
    group_id = settings.VK_REQUIRED_GROUP_ID
    if not group_id:
        return True

    url = "https://api.vk.com/method/groups.isMember"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params={
            "group_id": group_id,
            "user_id": vk_user_id,
            "access_token": vk_access_token,
            "v": "5.199"
        })
        r.raise_for_status()
        data = r.json()
        return bool(data.get("response") == 1)
