import enum
from datetime import datetime
from sqlalchemy import (
    String, Integer, Boolean, DateTime, Enum, ForeignKey,
    UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

class Provider(str, enum.Enum):
    telegram = "telegram"
    vk = "vk"

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("nickname", name="uq_users_nickname"),
        UniqueConstraint("provider", "provider_user_id", name="uq_users_provider_uid"),
        Index("ix_users_total_points", "total_points"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider: Mapped[Provider] = mapped_column(Enum(Provider), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(64), nullable=False)

    nickname: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    currency: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # "Зубные щётки"
    skins: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    dau_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    referral_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weekly_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_daily_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_weekly_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    score_events: Mapped[list["ScoreEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class ScoreEvent(Base):
    __tablename__ = "score_events"
    __table_args__ = (
        Index("ix_score_events_user_time", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    user: Mapped["User"] = relationship(back_populates="score_events")

class AppSetting(Base):
    __tablename__ = "app_settings"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

class Prize(Base):
    __tablename__ = "prizes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    place_from: Mapped[int] = mapped_column(Integer, nullable=False)
    place_to: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user_prizes: Mapped[list["UserPrize"]] = relationship(back_populates="prize", cascade="all, delete-orphan")

class UserPrize(Base):
    __tablename__ = "user_prizes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    prize_id: Mapped[int] = mapped_column(ForeignKey("prizes.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="awarded", nullable=False)
    issued_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship()
    prize: Mapped["Prize"] = relationship(back_populates="user_prizes")

DAILY_POINTS_LIMIT_KEY = "daily_points_limit"
ANTI_CHEAT_MAX_POINTS_KEY = "anti_cheat_max_points"
IP_DAILY_LIMIT_KEY = "ip_daily_limit"
