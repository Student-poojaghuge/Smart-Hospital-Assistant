from fastapi import FastAPI
from backend.routes import auth

app = FastAPI(
    title="Smart Hospital Assistant API",
    version="1.0.0"
)

app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "message": "Smart Hospital Assistant API is running"
    }