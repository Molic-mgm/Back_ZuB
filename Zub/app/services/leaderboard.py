from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

async def get_top10(session: AsyncSession):
    q = select(User).where(User.is_blocked == False).order_by(desc(User.total_points)).limit(10)  # noqa
    res = await session.execute(q)
    return res.scalars().all()
