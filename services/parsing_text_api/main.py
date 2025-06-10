# services/parsing_text_api/main.py
from api import router
from fastapi import FastAPI

app = FastAPI(title="Text Ingestion API", version="1.0.0")

app.include_router(router, prefix="/api")
