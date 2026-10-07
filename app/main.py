from fastapi import FastAPI
from app.core.logging_config import set_logging
from app.routers.chat import router as chat_router

set_logging()

app = FastAPI()
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"ok": True}