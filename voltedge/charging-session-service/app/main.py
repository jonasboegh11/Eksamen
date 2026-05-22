import logging
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
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
    yield
    logger.info("VoltEdge Charging Session Service shutting down")

app = FastAPI(
    title="VoltEdge Charging Session Service",
    description="Håndterer ladesessioner og driftsstabilitet",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "service": "charging-session-service"}

@app.get("/")
def root():
    return {"message": "VoltEdge Charging Session Service er kørende"}