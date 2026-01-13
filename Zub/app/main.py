from fastapi import FastAPI
from app.api.routes_auth import router as auth_router
from app.api.routes_users import router as users_router
from app.api.routes_points import router as points_router
from app.api.routes_leaderboard import router as leaderboard_router
from app.api.routes_admin_settings import router as admin_router
from app.admin import mount_admin

app = FastAPI(title="Unity Game Backend", version="1.0.0")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(points_router)
app.include_router(leaderboard_router)
app.include_router(admin_router)

mount_admin(app)

@app.get("/health")
async def health():
    return {"ok": True}
