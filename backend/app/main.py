from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.database import init_db, session_scope
from .models.rulepack import Tenant
from sqlmodel import select
from .routers import audit, health, rulepacks, runs, settings

app_settings = get_settings()

app = FastAPI(title=app_settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    init_db()
    with session_scope() as session:
        existing = session.exec(select(Tenant)).first()
        if not existing:
            session.add(Tenant(name="Presight Demo"))
            session.commit()


app.include_router(health.router)
app.include_router(settings.router)
app.include_router(rulepacks.router)
app.include_router(runs.router)
app.include_router(audit.router)
