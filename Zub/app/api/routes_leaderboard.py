from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas import LeaderboardOut, LeaderboardEntry, PrizeOut
from app.services.leaderboard import get_top10_entries
from app.services.prizes import list_active_prizes, find_prize_for_place

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

@router.get("/top10", response_model=LeaderboardOut)
async def top10(db: AsyncSession = Depends(get_db)):
    entries = await get_top10_entries(db)
    prizes = await list_active_prizes(db)
    top = []
    for index, entry in enumerate(entries, start=1):
        prize = find_prize_for_place(prizes, index)
        prize_out = None
        if prize:
            prize_out = PrizeOut(
                title=prize.title,
                description=prize.description,
                place_from=prize.place_from,
                place_to=prize.place_to,
                is_active=prize.is_active,
            )
        top.append(
            LeaderboardEntry(
                user_id=entry["user_id"],
                nickname=entry["nickname"],
                total_points=entry["total_points"],
                prize=prize_out,
            )
        )
    return LeaderboardOut(top=top)
