from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.stock import router as stock_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(stock_router)

@app.get("/")
def root():
    return {"message": "API is running"}