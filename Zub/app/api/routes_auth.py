from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models import User, Provider
from app.schemas import TokenOut, NicknameSetIn, UserOut
from app.security import create_access_token
from app.services.auth_telegram import verify_telegram_login
from app.services.auth_vk import exchange_code_for_user
from app.services.subscription import telegram_check_subscription, vk_check_subscription
from app.services.points import ensure_resets

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/telegram", response_model=TokenOut)
async def auth_telegram(payload: dict, db: AsyncSession = Depends(get_db)):
    if not verify_telegram_login(payload):
        raise HTTPException(401, "Telegram auth failed")

    tg_id = str(payload["id"])

    if not await telegram_check_subscription(tg_id):
        raise HTTPException(403, "Subscribe to clinic channel/group to access the game")

    q = select(User).where(User.provider == Provider.telegram, User.provider_user_id == tg_id)
    res = await db.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        user = User(provider=Provider.telegram, provider_user_id=tg_id, skins={})
        db.add(user)

    await ensure_resets(user)
    await db.commit()
    await db.refresh(user)

    return TokenOut(access_token=create_access_token(str(user.id)))

@router.post("/vk", response_model=TokenOut)
async def auth_vk(payload: dict, db: AsyncSession = Depends(get_db)):
    code = payload.get("code")
    if not code:
        raise HTTPException(400, "Missing code")

    vk_user_id, access_token = await exchange_code_for_user(code)

    if not await vk_check_subscription(vk_user_id, access_token):
        raise HTTPException(403, "Subscribe to clinic VK group to access the game")

    q = select(User).where(User.provider == Provider.vk, User.provider_user_id == vk_user_id)
    res = await db.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        user = User(provider=Provider.vk, provider_user_id=vk_user_id, skins={})
        db.add(user)

    await ensure_resets(user)
    await db.commit()
    await db.refresh(user)

    return TokenOut(access_token=create_access_token(str(user.id)))

@router.post("/nickname", response_model=UserOut)
async def set_nickname(body: NicknameSetIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    nick = body.nickname.strip()

    q = select(User).where(User.nickname == nick, User.id != user.id)
    res = await db.execute(q)
    if res.scalar_one_or_none():
        raise HTTPException(409, "Ник уже занят, придумайте другой")

    user.nickname = nick
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user, from_attributes=True)
