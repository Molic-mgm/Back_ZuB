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
    referral_count: int
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

class PrizeOut(BaseModel):
    title: str
    description: str | None
    place_from: int
    place_to: int
    is_active: bool = True

class LeaderboardEntry(BaseModel):
    user_id: int
    nickname: str | None
    total_points: int
    prize: PrizeOut | None = None

class LeaderboardOut(BaseModel):
    top: List[LeaderboardEntry]

class AdminSettingOut(BaseModel):
    key: str
    value: Dict[str, Any]

class DailyLimitIn(BaseModel):
    limit: int = Field(ge=0, le=1000000)

class AntiCheatLimitIn(BaseModel):
    max_points: int = Field(ge=0, le=1000000)

class IpDailyLimitIn(BaseModel):
    limit: int = Field(ge=0, le=1000000)

class RunSubmitIn(BaseModel):
    points: int = Field(gt=0, le=1000000)
    duration_seconds: int = Field(gt=0, le=86400)
    reason: str | None = Field(default="run_submit", max_length=64)

class RunSubmitOut(BaseModel):
    accepted_points: int
    rejected_points: int
    daily_remaining: int
    is_suspicious: bool
    user: UserOut

class ReferralUpdateIn(BaseModel):
    amount: int = Field(gt=0, le=1000000)

class ReferralOut(BaseModel):
    referral_count: int

class PrizeCreateIn(BaseModel):
    title: str = Field(min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=255)
    place_from: int = Field(ge=1, le=1000)
    place_to: int = Field(ge=1, le=1000)
    is_active: bool = True

class PrizeAssignIn(BaseModel):
    user_id: int = Field(ge=1)
    prize_id: int = Field(ge=1)
    notes: str | None = Field(default=None, max_length=255)

class PrizeAssignOut(BaseModel):
    user_id: int
    prize_id: int
    status: str
    issued_by: str | None
    notes: str | None

class PrizeAssignSkipped(BaseModel):
    user_id: int
    prize_id: int
    reason: str

class PrizeAssignBatchOut(BaseModel):
    assigned: list[PrizeAssignOut]
    skipped: list[PrizeAssignSkipped]
