from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Multi-Agent LLM Query API")

app.include_router(router)