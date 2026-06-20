# MaxiManage — Enterprise Asset Management Suite

An end-to-end **Enterprise Asset Management (EAM/CMMS)** platform inspired by the
**IBM Maximo Application Suite**. It covers the full maintenance lifecycle — assets,
work orders, preventive maintenance, inventory, and procurement — plus a suite of
**AI applications** (Health, Monitor, Predict, Visual Inspection, and Assist).

> Built as a complete, runnable product: a **FastAPI + SQLAlchemy + SQLite** backend
> with a seeded relational database, and a **React + TypeScript (Vite)** single-page
> frontend with an IBM Carbon-inspired UI.

---

## Quick start

```bash
cd maximo
./run.sh
```

Then open **http://localhost:8000**. The script builds the frontend, installs the
backend, seeds the database with realistic sample data, and serves both the API and
the UI from a single server.

### Run the two tiers separately (for development)

```bash
# Terminal 1 — backend (API + auto-seed) on :8000
cd maximo/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend dev server on :5173 (proxies /api -> :8000)
cd maximo/frontend
npm install
npm run dev
```

Interactive API docs are available at **http://localhost:8000/docs**.

---

## Modules

### Maximo Manage (core CMMS)
| Module | What it does |
|--------|--------------|
| **Dashboard** | KPIs: backlog, overdue PMs, asset health, MTTR, inventory value, maintenance cost; trend & breakdown charts |
| **Assets** | Equipment register with hierarchy, location, criticality, health score, condition meters & reading charts, and full work-order history. Create assets. |
| **Work Orders** | Create, assign, schedule and drive work through a governed status flow (`WAPPR → APPR → INPRG → COMP → CLOSE`), with job-plan tasks |
| **Preventive Maintenance** | Time-based PM schedules that **generate work orders** on demand and roll forward the next-due date |
| **Service Requests** | Intake tickets that **convert into work orders** |
| **Inventory** | Storeroom stock with reorder points; issue/receive adjusts balances; low-stock flags |
| **Purchasing** | Vendors and purchase orders with a status flow; **receiving a PO replenishes inventory** |

### AI Applications
| App | What it does |
|-----|--------------|
| **Health** | Scores and ranks every asset by condition + criticality into reliability-risk tiers |
| **Monitor** | Anomaly / threshold alerts from sensor & meter data; acknowledge or spin up a work order |
| **Predict** | Failure probability and remaining-useful-life (RUL) forecasts with recommended actions |
| **Visual Inspection** | Computer-vision-style defect detection results (corrosion, cracks, leaks) with confidence |
| **Assist** | A conversational agent grounded in live asset, PM, and inventory data |

---

## Architecture

```
maximo/
├── backend/                  FastAPI + SQLAlchemy + SQLite
│   ├── app/
│   │   ├── main.py           App, CORS, static SPA hosting, startup seed
│   │   ├── database.py       Engine / session / Base
│   │   ├── models.py         ORM models (assets, work, materials, AI)
│   │   ├── schemas.py        Pydantic v2 request/response contracts
│   │   ├── seed.py           Realistic sample-data seeding
│   │   └── routers/          assets · work · materials · dashboard · ai
│   └── requirements.txt
└── frontend/                 React + TypeScript + Vite
    └── src/
        ├── lib/              API client + shared types
        ├── components/       Layout (nav shell) + UI kit (badges, KPIs, charts, modal)
        └── pages/            One page per module (14 routes)
```

### Notable backend behaviours
- **Governed work-order workflow** — invalid status transitions are rejected (HTTP 400).
- **PM → Work Order** — `POST /api/pm/{id}/generate` creates a WO from the PM's job plan
  and advances `next_due` by the frequency.
- **Service Request → Work Order** — `POST /api/servicerequests/{id}/convert`.
- **PO receipt → Inventory** — moving a PO to `RECEIVED` increments stock balances.
- **Monitor alert → Work Order** — `POST /api/ai/monitor/alerts/{id}/create-wo`.
- The database **auto-seeds on first startup** (16 assets, work orders, PMs, inventory,
  POs, alerts, forecasts, inspections). Re-seed with
  `python -m app.seed --force`.

## Tech stack
- **Backend:** Python 3.11, FastAPI, SQLAlchemy 2.0, Pydantic v2, Uvicorn, SQLite
- **Frontend:** React 18, TypeScript, Vite, React Router 6 (hand-rolled SVG/CSS charts — no chart deps)

---

*This is an educational/demo reimplementation of common EAM concepts. It is not
affiliated with or endorsed by IBM. “Maximo” is a trademark of IBM.*
