"""Dashboard KPIs and reliability analytics."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    next_month_start = (
        datetime(now.year + 1, 1, 1) if now.month == 12
        else datetime(now.year, now.month + 1, 1)
    )
    assets = db.query(models.Asset).all()
    work_orders = db.query(models.WorkOrder).all()
    pms = db.query(models.PreventiveMaintenance).all()
    inventory = db.query(models.Inventory).all()
    alerts = db.query(models.MonitorAlert).filter(models.MonitorAlert.status == "OPEN").all()

    wo_by_status = {}
    for wo in work_orders:
        wo_by_status[wo.status] = wo_by_status.get(wo.status, 0) + 1

    open_statuses = {"WAPPR", "APPR", "INPRG"}
    backlog = [w for w in work_orders if w.status in open_statuses]

    overdue_pms = [p for p in pms if p.next_due and p.next_due < now and p.status == "ACTIVE"]
    upcoming_pms = [
        p for p in pms
        if p.next_due and now <= p.next_due < next_month_start
    ]

    below_reorder = [i for i in inventory if i.current_balance <= i.reorder_point]
    inv_value = sum(i.current_balance * i.unit_cost for i in inventory)

    # Reliability: MTTR from completed corrective work orders
    completed = [w for w in work_orders if w.status in ("COMP", "CLOSE") and w.actual_hours]
    mttr = round(sum(w.actual_hours for w in completed) / len(completed), 1) if completed else 0.0

    total_maint_cost = sum(w.actual_cost for w in work_orders if w.actual_cost)

    health_buckets = {"good": 0, "fair": 0, "poor": 0}
    for a in assets:
        if a.health_score >= 80:
            health_buckets["good"] += 1
        elif a.health_score >= 60:
            health_buckets["fair"] += 1
        else:
            health_buckets["poor"] += 1

    return {
        "asset_count": len(assets),
        "assets_operating": sum(1 for a in assets if a.status == "OPERATING"),
        "assets_down": sum(1 for a in assets if a.status == "DOWN"),
        "avg_health": round(sum(a.health_score for a in assets) / len(assets), 1) if assets else 0,
        "health_distribution": health_buckets,
        "work_order_count": len(work_orders),
        "wo_by_status": wo_by_status,
        "backlog_count": len(backlog),
        "wo_by_type": _count_by(work_orders, "work_type"),
        "overdue_pm_count": len(overdue_pms),
        "upcoming_pm_count": len(upcoming_pms),
        "inventory_value": round(inv_value, 2),
        "below_reorder_count": len(below_reorder),
        "open_alert_count": len(alerts),
        "critical_alert_count": sum(1 for a in alerts if a.severity == "CRITICAL"),
        "mttr_hours": mttr,
        "total_maintenance_cost": round(total_maint_cost, 2),
    }


@router.get("/dashboard/wo-trend")
def wo_trend(db: Session = Depends(get_db)):
    """Work-order volume by week for the last 12 weeks (for charting)."""
    cutoff = datetime.utcnow() - timedelta(weeks=12)
    work_orders = (
        db.query(models.WorkOrder)
        .filter(models.WorkOrder.reported_date >= cutoff)
        .all()
    )
    buckets = {}
    for w in work_orders:
        if not w.reported_date:
            continue
        week = w.reported_date.isocalendar()
        key = f"{week[0]}-W{week[1]:02d}"
        buckets.setdefault(key, {"week": key, "created": 0, "completed": 0})
        buckets[key]["created"] += 1
        if w.status in ("COMP", "CLOSE"):
            buckets[key]["completed"] += 1
    return sorted(buckets.values(), key=lambda x: x["week"])


def _count_by(rows, attr):
    out = {}
    for r in rows:
        key = getattr(r, attr)
        out[key] = out.get(key, 0) + 1
    return out
