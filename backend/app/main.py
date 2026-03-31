from fastapi import FastAPI
from app.routes.stock import router as stock_router

app = FastAPI()
app.include_router(stock_router)

@app.get("/")
def root():
    return {"message": "API is running"}