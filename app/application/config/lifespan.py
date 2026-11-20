import logging
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sqlalchemy.orm.mapper import configure_mappers

from app.application.config.application import Settings
from app.application.config.database import Database
from app.application.config.logger_config import logger_config

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = Settings()
    logger_config(settings.debug)
    logger.debug("Starting API...")
    app.state.database = Database(settings.database_path)
    configure_mappers()
    
    
    yield
    logger.debug("Shutting down API...")
    app.state.database.dispose()
