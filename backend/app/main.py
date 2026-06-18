from fastapi import FastAPI

from app.routers import admin, health, stats, traffic


app = FastAPI(
    title="NetFlow Monitor API",
    description="Network traffic analysis backend service.",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(traffic.router)
app.include_router(stats.router)
app.include_router(admin.router)
