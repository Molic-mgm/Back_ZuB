from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas import LeaderboardOut, LeaderboardEntry
from app.services.leaderboard import get_top10

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/top10", response_model=LeaderboardOut)
async def top10(db: AsyncSession = Depends(get_db)):
    users = await get_top10(db)
    return LeaderboardOut(top=[
        LeaderboardEntry(user_id=u.id, nickname=u.nickname, total_points=u.total_points)
        for u in users
    ])
