from fastapi import FastAPI

from app.application.config.lifespan import lifespan
from app.routers import health, job_application, profile

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(profile.router)
app.include_router(job_application.router)