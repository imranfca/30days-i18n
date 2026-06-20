"""Work Orders, Job Plans, Preventive Maintenance, Service Requests, Labor."""
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api", tags=["work"])

# Valid status transitions for work orders
WO_FLOW = {
    "WAPPR": ["APPR", "CAN"],
    "APPR": ["INPRG", "CAN"],
    "INPRG": ["COMP", "WAPPR"],
    "COMP": ["CLOSE", "INPRG"],
    "CLOSE": [],
    "CAN": [],
}


def _next_wo_num(db: Session) -> str:
    last = db.query(models.WorkOrder).order_by(models.WorkOrder.id.desc()).first()
    base = 2000 + (last.id if last else 0) + 1
    return f"WO-{base}"


# ------------------------------- Crafts ----------------------------------- #
@router.get("/crafts", response_model=List[schemas.Craft])
def list_crafts(db: Session = Depends(get_db)):
    return db.query(models.Craft).all()


# -------------------------------- Labor ----------------------------------- #
@router.get("/labor", response_model=List[schemas.Labor])
def list_labor(db: Session = Depends(get_db)):
    return db.query(models.Labor).all()


@router.post("/labor", response_model=schemas.Labor)
def create_labor(payload: schemas.LaborCreate, db: Session = Depends(get_db)):
    obj = models.Labor(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ------------------------------ Job Plans --------------------------------- #
@router.get("/jobplans", response_model=List[schemas.JobPlan])
def list_job_plans(db: Session = Depends(get_db)):
    return db.query(models.JobPlan).all()


@router.get("/jobplans/{jp_id}", response_model=schemas.JobPlan)
def get_job_plan(jp_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.JobPlan).get(jp_id)
    if not obj:
        raise HTTPException(404, "Job plan not found")
    return obj


@router.post("/jobplans", response_model=schemas.JobPlan)
def create_job_plan(payload: schemas.JobPlanCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    tasks = data.pop("tasks", [])
    obj = models.JobPlan(**data)
    for t in tasks:
        obj.tasks.append(models.JobPlanTask(**t))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ----------------------------- Work Orders -------------------------------- #
@router.get("/workorders", response_model=List[schemas.WorkOrder])
def list_work_orders(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    work_type: Optional[str] = None,
    asset_id: Optional[int] = None,
    assigned_to_id: Optional[int] = None,
):
    q = db.query(models.WorkOrder)
    if status:
        q = q.filter(models.WorkOrder.status == status)
    if work_type:
        q = q.filter(models.WorkOrder.work_type == work_type)
    if asset_id:
        q = q.filter(models.WorkOrder.asset_id == asset_id)
    if assigned_to_id:
        q = q.filter(models.WorkOrder.assigned_to_id == assigned_to_id)
    return q.order_by(models.WorkOrder.reported_date.desc()).all()


@router.get("/workorders/{wo_id}", response_model=schemas.WorkOrder)
def get_work_order(wo_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.WorkOrder).get(wo_id)
    if not obj:
        raise HTTPException(404, "Work order not found")
    return obj


@router.post("/workorders", response_model=schemas.WorkOrder)
def create_work_order(payload: schemas.WorkOrderCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    obj = models.WorkOrder(wo_num=_next_wo_num(db), reported_date=datetime.utcnow(), **data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/workorders/{wo_id}", response_model=schemas.WorkOrder)
def update_work_order(wo_id: int, payload: schemas.WorkOrderUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.WorkOrder).get(wo_id)
    if not obj:
        raise HTTPException(404, "Work order not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/workorders/{wo_id}/status", response_model=schemas.WorkOrder)
def change_wo_status(wo_id: int, payload: schemas.StatusUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.WorkOrder).get(wo_id)
    if not obj:
        raise HTTPException(404, "Work order not found")
    allowed = WO_FLOW.get(obj.status, [])
    if payload.status not in allowed:
        raise HTTPException(
            400, f"Invalid transition {obj.status} -> {payload.status}. Allowed: {allowed}"
        )
    obj.status = payload.status
    if payload.status == "INPRG" and not obj.actual_start:
        obj.actual_start = datetime.utcnow()
    if payload.status == "COMP":
        obj.actual_finish = datetime.utcnow()
        if not obj.actual_hours:
            obj.actual_hours = obj.estimated_hours
        if not obj.actual_cost:
            obj.actual_cost = obj.estimated_cost
    db.commit()
    db.refresh(obj)
    return obj


# ------------------------ Preventive Maintenance -------------------------- #
@router.get("/pm", response_model=List[schemas.PM])
def list_pm(db: Session = Depends(get_db)):
    return db.query(models.PreventiveMaintenance).order_by(models.PreventiveMaintenance.next_due).all()


@router.get("/pm/{pm_id}", response_model=schemas.PM)
def get_pm(pm_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.PreventiveMaintenance).get(pm_id)
    if not obj:
        raise HTTPException(404, "PM not found")
    return obj


@router.post("/pm", response_model=schemas.PM)
def create_pm(payload: schemas.PMCreate, db: Session = Depends(get_db)):
    obj = models.PreventiveMaintenance(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/pm/{pm_id}/generate", response_model=schemas.WorkOrder)
def generate_wo_from_pm(pm_id: int, db: Session = Depends(get_db)):
    pm = db.query(models.PreventiveMaintenance).get(pm_id)
    if not pm:
        raise HTTPException(404, "PM not found")
    jp = db.query(models.JobPlan).get(pm.job_plan_id) if pm.job_plan_id else None
    est_hours = jp.estimated_duration if jp else 4.0
    est_cost = (jp.estimated_labor_cost + jp.estimated_material_cost) if jp else 200.0
    wo = models.WorkOrder(
        wo_num=_next_wo_num(db),
        description=f"PM: {pm.description}",
        asset_id=pm.asset_id,
        location_id=pm.location_id,
        job_plan_id=pm.job_plan_id,
        status="WAPPR",
        priority=pm.priority,
        work_type="PM",
        reported_date=datetime.utcnow(),
        scheduled_start=pm.next_due,
        scheduled_finish=(pm.next_due or datetime.utcnow()) + timedelta(hours=est_hours),
        estimated_hours=est_hours,
        estimated_cost=est_cost,
        pm_id=pm.id,
    )
    db.add(wo)
    pm.last_generated = datetime.utcnow()
    pm.next_due = (pm.next_due or datetime.utcnow()) + timedelta(days=pm.frequency_days)
    db.commit()
    db.refresh(wo)
    return wo


# -------------------------- Service Requests ------------------------------ #
@router.get("/servicerequests", response_model=List[schemas.ServiceRequest])
def list_service_requests(db: Session = Depends(get_db), status: Optional[str] = None):
    q = db.query(models.ServiceRequest)
    if status:
        q = q.filter(models.ServiceRequest.status == status)
    return q.order_by(models.ServiceRequest.reported_date.desc()).all()


@router.post("/servicerequests", response_model=schemas.ServiceRequest)
def create_service_request(payload: schemas.ServiceRequestCreate, db: Session = Depends(get_db)):
    last = db.query(models.ServiceRequest).order_by(models.ServiceRequest.id.desc()).first()
    num = f"SR-{3000 + (last.id if last else 0) + 1}"
    obj = models.ServiceRequest(ticket_num=num, reported_date=datetime.utcnow(),
                                **payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/servicerequests/{sr_id}", response_model=schemas.ServiceRequest)
def update_service_request(sr_id: int, payload: schemas.ServiceRequestUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.ServiceRequest).get(sr_id)
    if not obj:
        raise HTTPException(404, "Service request not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/servicerequests/{sr_id}/convert", response_model=schemas.WorkOrder)
def convert_sr_to_wo(sr_id: int, db: Session = Depends(get_db)):
    sr = db.query(models.ServiceRequest).get(sr_id)
    if not sr:
        raise HTTPException(404, "Service request not found")
    if sr.status not in ("NEW", "QUEUED"):
        raise HTTPException(
            409, f"Service request {sr.ticket_num} is {sr.status} and cannot be converted"
        )
    existing = db.query(models.WorkOrder).filter(models.WorkOrder.sr_id == sr.id).first()
    if existing:
        raise HTTPException(
            409, f"Service request {sr.ticket_num} is already converted to {existing.wo_num}"
        )
    wo = models.WorkOrder(
        wo_num=_next_wo_num(db),
        description=sr.description,
        asset_id=sr.asset_id,
        location_id=sr.location_id,
        status="WAPPR",
        priority=sr.priority,
        work_type="CM",
        reported_date=datetime.utcnow(),
        sr_id=sr.id,
    )
    db.add(wo)
    sr.status = "INPROG"
    db.commit()
    db.refresh(wo)
    return wo
