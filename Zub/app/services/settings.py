from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AppSetting

async def get_setting_int(session: AsyncSession, key: str, default: int = 0) -> int:
    row = await session.get(AppSetting, key)
    if not row:
        return default
    return int(row.value.get("value", row.value.get("limit", row.value.get("max_points", default))))

async def set_setting_int(session: AsyncSession, key: str, value: int) -> AppSetting:
    row = await session.get(AppSetting, key)
    payload = {"value": value}
    if not row:
        row = AppSetting(key=key, value=payload)
        session.add(row)
    else:
        row.value = payload
    await session.commit()
    await session.refresh(row)
    return row
