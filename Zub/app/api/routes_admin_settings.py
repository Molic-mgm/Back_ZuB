from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import AppSetting, DAILY_POINTS_LIMIT_KEY, ANTI_CHEAT_MAX_POINTS_KEY, IP_DAILY_LIMIT_KEY
from app.schemas import DailyLimitIn, AdminSettingOut, AntiCheatLimitIn, IpDailyLimitIn
from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

def _basic_admin_guard(x_admin_user: str | None, x_admin_pass: str | None):
    if x_admin_user != settings.ADMIN_USERNAME or x_admin_pass != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "Admin auth failed")

async def _get_setting(db: AsyncSession, key: str, default_payload: dict):
    row = await db.get(AppSetting, key)
    if not row:
        row = AppSetting(key=key, value=default_payload)
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row

@router.post("/daily-limit", response_model=AdminSettingOut)
async def set_daily_limit(
    body: DailyLimitIn,
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    row = await db.get(AppSetting, DAILY_POINTS_LIMIT_KEY)
    if not row:
        row = AppSetting(key=DAILY_POINTS_LIMIT_KEY, value={"limit": body.limit})
        db.add(row)
    else:
        row.value = {"limit": body.limit}
    await db.commit()
    await db.refresh(row)
    return AdminSettingOut(key=row.key, value=row.value)

@router.get("/daily-limit", response_model=AdminSettingOut)
async def get_daily_limit(
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    row = await _get_setting(db, DAILY_POINTS_LIMIT_KEY, {"limit": 0})
    return AdminSettingOut(key=row.key, value=row.value)

@router.post("/anti-cheat", response_model=AdminSettingOut)
async def set_anti_cheat_limit(
    body: AntiCheatLimitIn,
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    row = await db.get(AppSetting, ANTI_CHEAT_MAX_POINTS_KEY)
    if not row:
        row = AppSetting(key=ANTI_CHEAT_MAX_POINTS_KEY, value={"max_points": body.max_points})
        db.add(row)
    else:
        row.value = {"max_points": body.max_points}
    await db.commit()
    await db.refresh(row)
    return AdminSettingOut(key=row.key, value=row.value)

@router.get("/anti-cheat", response_model=AdminSettingOut)
async def get_anti_cheat_limit(
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    row = await _get_setting(db, ANTI_CHEAT_MAX_POINTS_KEY, {"max_points": 0})
    return AdminSettingOut(key=row.key, value=row.value)

@router.post("/ip-limit", response_model=AdminSettingOut)
async def set_ip_limit(
    body: IpDailyLimitIn,
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    row = await db.get(AppSetting, IP_DAILY_LIMIT_KEY)
    if not row:
        row = AppSetting(key=IP_DAILY_LIMIT_KEY, value={"limit": body.limit})
        db.add(row)
    else:
        row.value = {"limit": body.limit}
    await db.commit()
    await db.refresh(row)
    return AdminSettingOut(key=row.key, value=row.value)

@router.get("/ip-limit", response_model=AdminSettingOut)
async def get_ip_limit(
    db: AsyncSession = Depends(get_db),
    x_admin_user: str | None = Header(default=None),
    x_admin_pass: str | None = Header(default=None),
):
    _basic_admin_guard(x_admin_user, x_admin_pass)
    row = await _get_setting(db, IP_DAILY_LIMIT_KEY, {"limit": 0})
    return AdminSettingOut(key=row.key, value=row.value)
