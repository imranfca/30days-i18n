# Maximo — Enterprise Asset Management Suite

**MaxiManage** is an end-to-end **Enterprise Asset Management (EAM/CMMS)** platform
inspired by the **IBM Maximo Application Suite**. It covers the full maintenance
lifecycle — assets, work orders, preventive maintenance, inventory, and
procurement — plus a suite of **AI applications** (Health, Monitor, Predict,
Visual Inspection, and Assist).

- **Backend:** FastAPI · SQLAlchemy · SQLite (seeded relational database)
- **Frontend:** React · TypeScript · Vite (IBM Carbon-inspired UI)
- **Single-deployable:** the API and the built single-page app are served from one process

## Quick start

```bash
cd maximo
./run.sh
```

Then open **http://localhost:8000**. The application lives in the
[`maximo/`](maximo/) directory — see [`maximo/README.md`](maximo/README.md) for the
full module breakdown, architecture, and development instructions.

---

*Educational/demo reimplementation of common EAM concepts. Not affiliated with or
endorsed by IBM; "Maximo" is a trademark of IBM.*
