from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .routes.stock import router as stock_router
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

async def ping_server():
    """Ping the server to keep it alive"""
    try:
        api_url = os.getenv("API_URL", "http://localhost:8000")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{api_url}/", timeout=10)
            logger.info(f"Keep-alive ping successful: {response.status_code}")
    except Exception as e:
        logger.error(f"Keep-alive ping failed: {e}")

def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        # Schedule the ping to run every 13 minutes
        scheduler.add_job(ping_server, 'interval', minutes=13, id='keep_alive_ping')
        scheduler.start()
        logger.info("Keep-alive scheduler started - pinging every 13 minutes")

def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Keep-alive scheduler stopped")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(lifespan=lifespan)

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://jarnox-stock-dashboard.vercel.app,http://localhost:5500").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(stock_router)

@app.get("/")
def root():
    return {"message": "API is running"}