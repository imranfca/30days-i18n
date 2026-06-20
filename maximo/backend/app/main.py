"""FastAPI application for the Maximo-style Enterprise Asset Management suite."""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import ai, assets, dashboard, materials, work
from .seed import seed

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MaxiManage — Enterprise Asset Management Suite",
    description="An end-to-end EAM/CMMS platform inspired by IBM Maximo Application Suite.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup():
    seed()


@app.get("/api/health", tags=["system"])
def health():
    return {"status": "ok", "product": "MaxiManage EAM Suite", "version": "1.0.0"}


app.include_router(dashboard.router)
app.include_router(assets.router)
app.include_router(work.router)
app.include_router(materials.router)
app.include_router(ai.router)


# Serve the built React frontend (single-deployable bundle) when present.
_DIST = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.isdir(_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(_DIST, "assets")), name="static-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        candidate = os.path.join(_DIST, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_DIST, "index.html"))
