from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .database import create_all, get_session
from .routers import router as terms_router
from .seed_data import seed_terms

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all()
    async with get_session() as session:
        await seed_terms(session)
    yield

app = FastAPI(
    title="Глоссарий паттернов",
    description="API для управления глоссарием терминов по распознаванию шаблонов проектирования",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for local dev and demos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


app.include_router(terms_router)
