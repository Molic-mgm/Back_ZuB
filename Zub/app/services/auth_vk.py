from typing import Tuple
import httpx
from app.config import settings

VK_TOKEN_URL = "https://oauth.vk.com/access_token"
VK_API_VERSION = "5.199"

async def exchange_code_for_user(code: str) -> Tuple[str, str]:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(VK_TOKEN_URL, params={
            "client_id": settings.VK_CLIENT_ID,
            "client_secret": settings.VK_CLIENT_SECRET,
            "redirect_uri": settings.VK_REDIRECT_URI,
            "code": code,
        })
        r.raise_for_status()
        data = r.json()
        if "user_id" not in data or "access_token" not in data:
            raise ValueError(f"VK OAuth failed: {data}")
        return str(data["user_id"]), data["access_token"]
