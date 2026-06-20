"""Items, Inventory, Storerooms, Vendors, and Purchase Orders."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api", tags=["materials"])


# --------------------------------- Items ---------------------------------- #
@router.get("/items", response_model=List[schemas.Item])
def list_items(db: Session = Depends(get_db), search: Optional[str] = None):
    q = db.query(models.Item)
    if search:
        like = f"%{search}%"
        q = q.filter(models.Item.item_num.ilike(like) | models.Item.description.ilike(like))
    return q.order_by(models.Item.item_num).all()


@router.post("/items", response_model=schemas.Item)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    obj = models.Item(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ------------------------------ Storerooms -------------------------------- #
@router.get("/storerooms", response_model=List[schemas.Storeroom])
def list_storerooms(db: Session = Depends(get_db)):
    return db.query(models.Storeroom).all()


# ------------------------------- Inventory -------------------------------- #
@router.get("/inventory", response_model=List[schemas.Inventory])
def list_inventory(db: Session = Depends(get_db), below_reorder: bool = False):
    q = db.query(models.Inventory)
    rows = q.all()
    if below_reorder:
        rows = [r for r in rows if r.current_balance <= r.reorder_point]
    return rows


@router.post("/inventory", response_model=schemas.Inventory)
def create_inventory(payload: schemas.InventoryCreate, db: Session = Depends(get_db)):
    obj = models.Inventory(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/inventory/{inv_id}/adjust", response_model=schemas.Inventory)
def adjust_inventory(inv_id: int, payload: schemas.InventoryAdjust, db: Session = Depends(get_db)):
    obj = db.query(models.Inventory).get(inv_id)
    if not obj:
        raise HTTPException(404, "Inventory record not found")
    new_balance = obj.current_balance + payload.delta
    if new_balance < 0:
        raise HTTPException(400, "Insufficient balance for issue")
    obj.current_balance = new_balance
    db.commit()
    db.refresh(obj)
    return obj


# -------------------------------- Vendors --------------------------------- #
@router.get("/vendors", response_model=List[schemas.Vendor])
def list_vendors(db: Session = Depends(get_db)):
    return db.query(models.Vendor).all()


@router.post("/vendors", response_model=schemas.Vendor)
def create_vendor(payload: schemas.VendorCreate, db: Session = Depends(get_db)):
    obj = models.Vendor(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ----------------------------- Purchase Orders ---------------------------- #
@router.get("/purchaseorders", response_model=List[schemas.PurchaseOrder])
def list_purchase_orders(db: Session = Depends(get_db), status: Optional[str] = None):
    q = db.query(models.PurchaseOrder)
    if status:
        q = q.filter(models.PurchaseOrder.status == status)
    return q.order_by(models.PurchaseOrder.order_date.desc()).all()


@router.get("/purchaseorders/{po_id}", response_model=schemas.PurchaseOrder)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.PurchaseOrder).get(po_id)
    if not obj:
        raise HTTPException(404, "Purchase order not found")
    return obj


@router.post("/purchaseorders", response_model=schemas.PurchaseOrder)
def create_purchase_order(payload: schemas.PurchaseOrderCreate, db: Session = Depends(get_db)):
    last = db.query(models.PurchaseOrder).order_by(models.PurchaseOrder.id.desc()).first()
    num = f"PO-{4000 + (last.id if last else 0) + 1}"
    data = payload.model_dump()
    lines = data.pop("lines", [])
    obj = models.PurchaseOrder(po_num=num, order_date=datetime.utcnow(), **data)
    total = 0.0
    for ln in lines:
        ln["line_cost"] = round(ln["quantity"] * ln["unit_cost"], 2)
        total += ln["line_cost"]
        obj.lines.append(models.POLine(**ln))
    obj.total_cost = round(total, 2)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/purchaseorders/{po_id}/status", response_model=schemas.PurchaseOrder)
def change_po_status(po_id: int, payload: schemas.StatusUpdate, db: Session = Depends(get_db)):
    obj = db.query(models.PurchaseOrder).get(po_id)
    if not obj:
        raise HTTPException(404, "Purchase order not found")
    obj.status = payload.status
    # Receiving a PO replenishes inventory balances for its lines
    if payload.status == "RECEIVED":
        for ln in obj.lines:
            if ln.item_id:
                inv = (
                    db.query(models.Inventory)
                    .filter(models.Inventory.item_id == ln.item_id)
                    .first()
                )
                if inv:
                    inv.current_balance += ln.quantity
    db.commit()
    db.refresh(obj)
    return obj
