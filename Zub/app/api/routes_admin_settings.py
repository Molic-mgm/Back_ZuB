from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models import AppSetting, DAILY_POINTS_LIMIT_KEY
from app.schemas import DailyLimitIn, AdminSettingOut
from app.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])

def _basic_admin_guard(x_admin_user: str | None, x_admin_pass: str | None):
    if x_admin_user != settings.ADMIN_USERNAME or x_admin_pass != settings.ADMIN_PASSWORD:
        raise HTTPException(401, "Admin auth failed")

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
    row = await db.get(AppSetting, DAILY_POINTS_LIMIT_KEY)
    if not row:
        row = AppSetting(key=DAILY_POINTS_LIMIT_KEY, value={"limit": 0})
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return AdminSettingOut(key=row.key, value=row.value)
