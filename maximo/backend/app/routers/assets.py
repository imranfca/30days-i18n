"""Assets, Locations, and Meters endpoints."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api", tags=["assets"])


# ------------------------------- Locations -------------------------------- #
@router.get("/locations", response_model=List[schemas.Location])
def list_locations(db: Session = Depends(get_db)):
    return db.query(models.Location).all()


@router.post("/locations", response_model=schemas.Location)
def create_location(payload: schemas.LocationCreate, db: Session = Depends(get_db)):
    obj = models.Location(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# --------------------------------- Assets --------------------------------- #
@router.get("/assets", response_model=List[schemas.Asset])
def list_assets(
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    search: Optional[str] = None,
    location_id: Optional[int] = None,
):
    q = db.query(models.Asset)
    if status:
        q = q.filter(models.Asset.status == status)
    if location_id:
        q = q.filter(models.Asset.location_id == location_id)
    if search:
        like = f"%{search}%"
        q = q.filter(
            models.Asset.asset_num.ilike(like) | models.Asset.description.ilike(like)
        )
    return q.order_by(models.Asset.asset_num).all()


@router.get("/assets/{asset_id}", response_model=schemas.Asset)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Asset).get(asset_id)
    if not obj:
        raise HTTPException(404, "Asset not found")
    return obj


@router.get("/assets/{asset_id}/workorders", response_model=List[schemas.WorkOrder])
def asset_work_orders(asset_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.WorkOrder)
        .filter(models.WorkOrder.asset_id == asset_id)
        .order_by(models.WorkOrder.reported_date.desc())
        .all()
    )


@router.post("/assets", response_model=schemas.Asset)
def create_asset(payload: schemas.AssetCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if not data.get("install_date"):
        data["install_date"] = datetime.utcnow()
    if db.query(models.Asset).filter_by(asset_num=data["asset_num"]).first():
        raise HTTPException(400, "Asset number already exists")
    obj = models.Asset(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.patch("/assets/{asset_id}", response_model=schemas.Asset)
def update_asset(asset_id: int, payload: schemas.AssetUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.Asset).get(asset_id)
    if not obj:
        raise HTTPException(404, "Asset not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/assets/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Asset).get(asset_id)
    if not obj:
        raise HTTPException(404, "Asset not found")
    db.delete(obj)
    db.commit()
    return {"deleted": asset_id}


# --------------------------------- Meters --------------------------------- #
@router.get("/meters", response_model=List[schemas.Meter])
def list_meters(db: Session = Depends(get_db), asset_id: Optional[int] = None):
    q = db.query(models.Meter)
    if asset_id:
        q = q.filter(models.Meter.asset_id == asset_id)
    return q.all()


@router.get("/meters/{meter_id}/readings", response_model=List[schemas.MeterReading])
def meter_readings(meter_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.MeterReading)
        .filter(models.MeterReading.meter_id == meter_id)
        .order_by(models.MeterReading.reading_date)
        .all()
    )


@router.post("/meters/{meter_id}/readings", response_model=schemas.Meter)
def add_reading(meter_id: int, payload: schemas.MeterReadingCreate, db: Session = Depends(get_db)):
    meter = db.query(models.Meter).get(meter_id)
    if not meter:
        raise HTTPException(404, "Meter not found")
    when = payload.reading_date or datetime.utcnow()
    db.add(models.MeterReading(meter_id=meter_id, reading=payload.reading, reading_date=when))
    meter.last_reading = payload.reading
    meter.last_reading_date = when
    db.commit()
    db.refresh(meter)
    return meter
