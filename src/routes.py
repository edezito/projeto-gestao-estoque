from fastapi import FastAPI
from src.Application.Controllers import seller_controllers

app = FastAPI(title="Mini Mercado API")

app.include_router(seller_controllers.router)

@app.get("/")
def home():
    return {"message": "API Mini Mercado funcionando"}
