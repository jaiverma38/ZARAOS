from fastapi import FastAPI
from zara_ai_server.api.routes import router

app = FastAPI(title="Zara AI Server", version="1.0.0")
app.include_router(router)
