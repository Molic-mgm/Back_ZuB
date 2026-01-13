from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    id: int
    provider: str
    provider_user_id: str
    nickname: Optional[str]
    is_blocked: bool
    currency: int
    skins: Dict[str, Any]
    dau_count: int
    total_points: int
    daily_points: int
    weekly_points: int

    class Config:
        from_attributes = True

class NicknameSetIn(BaseModel):
    nickname: str = Field(min_length=3, max_length=32)

class PointsAddIn(BaseModel):
    amount: int = Field(gt=0, le=100000)
    reason: str | None = Field(default=None, max_length=64)

class LeaderboardEntry(BaseModel):
    user_id: int
    nickname: str | None
    total_points: int

class LeaderboardOut(BaseModel):
    top: List[LeaderboardEntry]

class AdminSettingOut(BaseModel):
    key: str
    value: Dict[str, Any]

class DailyLimitIn(BaseModel):
    limit: int = Field(ge=0, le=1000000)
