from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import router
from app.db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Email Generation Assistant",
    description="Professional email generation using LangGraph and advanced prompting techniques",
    version="0.1.0",
    lifespan=lifespan
)

# Include routes
app.include_router(router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "email-generation-assistant"}