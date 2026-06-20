"""Maximo-style AI applications: Health, Monitor, Predict, Visual Inspection, Assist."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/ai", tags=["ai-suite"])


# ------------------------------ Health ------------------------------------ #
@router.get("/health")
def asset_health(db: Session = Depends(get_db)):
    """Maximo Health — asset condition & risk ranking."""
    assets = db.query(models.Asset).order_by(models.Asset.health_score).all()
    ranked = []
    for a in assets:
        risk = "Low"
        if a.health_score < 60:
            risk = "High"
        elif a.health_score < 80:
            risk = "Medium"
        # Criticality 1 (highest) elevates effective risk
        if a.criticality <= 2 and a.health_score < 75:
            risk = "High"
        ranked.append({
            "asset_id": a.id,
            "asset_num": a.asset_num,
            "description": a.description,
            "health_score": a.health_score,
            "criticality": a.criticality,
            "status": a.status,
            "risk": risk,
        })
    return {
        "assets": ranked,
        "summary": {
            "high_risk": sum(1 for r in ranked if r["risk"] == "High"),
            "medium_risk": sum(1 for r in ranked if r["risk"] == "Medium"),
            "low_risk": sum(1 for r in ranked if r["risk"] == "Low"),
        },
    }


# ------------------------------ Monitor ----------------------------------- #
@router.get("/monitor/alerts", response_model=List[schemas.MonitorAlert])
def monitor_alerts(db: Session = Depends(get_db), status: Optional[str] = None):
    """Maximo Monitor — anomaly & threshold alerts from sensor data."""
    q = db.query(models.MonitorAlert)
    if status:
        q = q.filter(models.MonitorAlert.status == status)
    return q.order_by(models.MonitorAlert.detected_at.desc()).all()


@router.post("/monitor/alerts/{alert_id}/acknowledge", response_model=schemas.MonitorAlert)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.MonitorAlert).get(alert_id)
    if not obj:
        raise HTTPException(404, "Alert not found")
    obj.status = "ACKNOWLEDGED"
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/monitor/alerts/{alert_id}/create-wo", response_model=schemas.WorkOrder)
def alert_to_work_order(alert_id: int, db: Session = Depends(get_db)):
    from datetime import datetime
    from .work import _next_wo_num

    alert = db.query(models.MonitorAlert).get(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    asset = db.query(models.Asset).get(alert.asset_id)
    wo = models.WorkOrder(
        wo_num=_next_wo_num(db),
        description=f"Monitor alert: {alert.message}",
        asset_id=alert.asset_id,
        location_id=asset.location_id if asset else None,
        status="WAPPR",
        priority=1 if alert.severity in ("CRITICAL", "HIGH") else 3,
        work_type="CM",
        reported_date=datetime.utcnow(),
    )
    db.add(wo)
    alert.status = "ACKNOWLEDGED"
    db.commit()
    db.refresh(wo)
    return wo


# ------------------------------ Predict ----------------------------------- #
@router.get("/predict/forecasts", response_model=List[schemas.PredictForecast])
def predict_forecasts(db: Session = Depends(get_db)):
    """Maximo Predict — failure probability & remaining useful life."""
    return (
        db.query(models.PredictForecast)
        .order_by(models.PredictForecast.failure_probability.desc())
        .all()
    )


# -------------------------- Visual Inspection ----------------------------- #
@router.get("/visual/inspections", response_model=List[schemas.VisualInspection])
def visual_inspections(db: Session = Depends(get_db), defects_only: bool = False):
    """Maximo Visual Inspection — computer-vision defect detection."""
    q = db.query(models.VisualInspection)
    if defects_only:
        q = q.filter(models.VisualInspection.defect_detected.is_(True))
    return q.order_by(models.VisualInspection.inspection_date.desc()).all()


# ------------------------------- Assist ----------------------------------- #
@router.post("/assist", response_model=schemas.AssistResponse)
def assist(query: schemas.AssistQuery, db: Session = Depends(get_db)):
    """Maximo Assist — knowledge assistant grounded in live asset data.

    Rules-based reasoning over the database (no external LLM dependency) so the
    demo is fully self-contained.
    """
    q = query.question.lower()
    sources: List[str] = []
    actions: List[str] = []

    # Asset-specific context
    asset = None
    if query.asset_id:
        asset = db.query(models.Asset).get(query.asset_id)

    if any(k in q for k in ("health", "condition", "risk")):
        worst = db.query(models.Asset).order_by(models.Asset.health_score).first()
        sources = ["Maximo Health", "Asset master"]
        actions = ["Review high-risk assets in the Health module"]
        return schemas.AssistResponse(
            answer=(
                f"The lowest-health asset is {worst.asset_num} ({worst.description}) at "
                f"{worst.health_score}/100. Assets below 60 are flagged High risk and should be "
                f"prioritized for inspection or corrective work orders."
            ),
            sources=sources, suggested_actions=actions,
        )

    if any(k in q for k in ("overdue", "due", "pm", "preventive")):
        from datetime import datetime
        now = datetime(2026, 6, 20)
        pms = db.query(models.PreventiveMaintenance).all()
        overdue = [p for p in pms if p.next_due and p.next_due < now]
        actions = ["Generate work orders from overdue PMs"]
        return schemas.AssistResponse(
            answer=(
                f"There are {len(overdue)} overdue preventive maintenance schedules. "
                + (f"The most overdue is {overdue[0].pm_num} — {overdue[0].description}." if overdue else "")
            ),
            sources=["Maximo Manage — PM module"], suggested_actions=actions,
        )

    if any(k in q for k in ("part", "stock", "inventory", "reorder")):
        inv = db.query(models.Inventory).all()
        low = [i for i in inv if i.current_balance <= i.reorder_point]
        names = ", ".join(i.item.description for i in low[:3]) if low else "none"
        actions = ["Create a purchase order for low-stock items"]
        return schemas.AssistResponse(
            answer=f"{len(low)} item(s) are at or below reorder point. Examples: {names}.",
            sources=["Maximo Manage — Inventory"], suggested_actions=actions,
        )

    if asset:
        wos = db.query(models.WorkOrder).filter(models.WorkOrder.asset_id == asset.id).count()
        return schemas.AssistResponse(
            answer=(
                f"{asset.asset_num} — {asset.description}. Status: {asset.status}, health "
                f"{asset.health_score}/100, criticality {asset.criticality}. It has {wos} work "
                f"order(s) on record. Recommended: review open alerts and predictive forecasts."
            ),
            sources=["Asset master", "Work order history"],
            suggested_actions=["Open the asset detail page", "Check predictive forecast"],
        )

    return schemas.AssistResponse(
        answer=(
            "I'm the MaxiManage Assist agent. Ask me about asset health, overdue preventive "
            "maintenance, low-stock parts, or a specific asset's status and history."
        ),
        sources=["MaxiManage knowledge base"],
        suggested_actions=[
            "What assets are at highest risk?",
            "Which PMs are overdue?",
            "What parts are below reorder point?",
        ],
    )
