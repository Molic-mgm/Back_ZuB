from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db import engine
from app.models import User, ScoreEvent, AppSetting, Prize, UserPrize

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            request.session.update({"admin": True})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin"))

class UserAdmin(ModelView, model=User):
    column_list = [
        User.id, User.provider, User.provider_user_id, User.nickname, User.is_blocked,
        User.currency, User.total_points, User.daily_points, User.weekly_points, User.dau_count, User.referral_count,
        User.created_at, User.updated_at
    ]
    column_searchable_list = [User.nickname, User.provider_user_id]
    column_sortable_list = [User.id, User.total_points, User.created_at]
    name = "User"
    name_plural = "Users"

class ScoreEventAdmin(ModelView, model=ScoreEvent):
    column_list = [
        ScoreEvent.id,
        ScoreEvent.user_id,
        ScoreEvent.amount,
        ScoreEvent.reason,
        ScoreEvent.ip_address,
        ScoreEvent.is_suspicious,
        ScoreEvent.created_at,
    ]
    column_sortable_list = [ScoreEvent.id, ScoreEvent.created_at]

class SettingsAdmin(ModelView, model=AppSetting):
    column_list = [AppSetting.key, AppSetting.value]

class PrizeAdmin(ModelView, model=Prize):
    column_list = [
        Prize.id, Prize.title, Prize.description, Prize.place_from, Prize.place_to, Prize.is_active,
        Prize.created_at, Prize.updated_at,
    ]
    column_sortable_list = [Prize.id, Prize.place_from]

class UserPrizeAdmin(ModelView, model=UserPrize):
    column_list = [
        UserPrize.id, UserPrize.user_id, UserPrize.prize_id, UserPrize.status,
        UserPrize.issued_by, UserPrize.notes, UserPrize.awarded_at,
    ]
    column_sortable_list = [UserPrize.id, UserPrize.awarded_at]

def mount_admin(app):
    app.add_middleware(SessionMiddleware, secret_key=settings.ADMIN_SESSION_SECRET)
    auth_backend = AdminAuth(secret_key=settings.ADMIN_SESSION_SECRET)
    admin = Admin(app, engine, authentication_backend=auth_backend)
    admin.add_view(UserAdmin)
    admin.add_view(ScoreEventAdmin)
    admin.add_view(SettingsAdmin)
    admin.add_view(PrizeAdmin)
    admin.add_view(UserPrizeAdmin)
    return admin
