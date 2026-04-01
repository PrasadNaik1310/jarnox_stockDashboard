from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .routes.stock import router as stock_router

app = FastAPI()

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://jarnox-stock-dashboard.vercel.app,http://localhost:5500,http://127.0.0.1:5500").split(",")

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