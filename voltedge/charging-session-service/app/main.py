import logging
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.api.telemetry_router import router as telemetry_router
from app.api.incident_router import router as incident_router
from app.infrastructure.database import init_db
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("voltedge.charging-session")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("VoltEdge Charging Session Service starting up")
    logger.info(f"Connecting to database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    init_db()
    yield
    logger.info("VoltEdge Charging Session Service shutting down")

app = FastAPI(
    title="VoltEdge Charging Session Service",
    description="Håndterer ladesessioner og driftsstabilitet",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(telemetry_router)
app.include_router(incident_router)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "service": "charging-session-service"}

@app.get("/")
def root():
    return {"message": "VoltEdge Charging Session Service er kørende"}