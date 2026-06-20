"""FastAPI application for the Maximo-style Enterprise Asset Management suite."""
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .database import Base, engine
from .routers import ai, assets, dashboard, materials, work
from .seed import seed

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MaxiManage — Enterprise Asset Management Suite",
    description="An end-to-end EAM/CMMS platform inspired by IBM Maximo Application Suite.",
    version="1.0.0",
)

# The SPA is served same-origin and the API uses no cookies/credentials, so a
# wildcard origin is fine — but per the CORS spec it must not be combined with
# allow_credentials=True. Origins can be restricted via the CORS_ORIGINS env var.
_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins],
    allow_credentials=False,
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
# Note: we deliberately do NOT mount StaticFiles at "/assets" — that path is also
# a SPA route (/assets, /assets/:id), and a mount there would shadow it so direct
# visits/reloads 404. The catch-all below serves real bundle files (including
# /assets/*.js) and falls back to index.html for client-side routes.
_DIST = Path(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")).resolve()
if _DIST.is_dir():

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        # Unknown /api/* paths should 404 as API routes, not fall back to the SPA.
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        # Resolve canonically and enforce the dist boundary to block path traversal
        # (e.g. requests like ../../etc/passwd). Real files (the JS/CSS bundle,
        # favicon, etc.) are served directly; everything else returns the SPA shell.
        candidate = (_DIST / full_path).resolve()
        if full_path and candidate.is_file() and _DIST in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(_DIST / "index.html")
