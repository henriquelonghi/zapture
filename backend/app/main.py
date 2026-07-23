from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import data_sources, report
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="SaaS de Relatórios via WhatsApp — API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(report.router)
app.include_router(data_sources.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
