"""Pydantic schemas (API contracts) for the Maximo clone."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ----------------------------- Locations ---------------------------------- #
class LocationBase(ORMModel):
    code: str
    name: str
    type: str = "OPERATING"
    parent_id: Optional[int] = None
    status: str = "OPERATING"
    address: str = ""
    site: str = "HQ"


class LocationCreate(LocationBase):
    pass


class Location(LocationBase):
    id: int


# ------------------------------- Meters ----------------------------------- #
class MeterBase(ORMModel):
    asset_id: int
    name: str
    unit: str = ""
    meter_type: str = "CONTINUOUS"
    last_reading: float = 0.0
    last_reading_date: Optional[datetime] = None
    warning_limit: Optional[float] = None
    action_limit: Optional[float] = None


class MeterCreate(MeterBase):
    pass


class Meter(MeterBase):
    id: int


class MeterReadingCreate(ORMModel):
    meter_id: int
    reading: float
    reading_date: Optional[datetime] = None


class MeterReading(ORMModel):
    id: int
    meter_id: int
    reading: float
    reading_date: Optional[datetime] = None


# ------------------------------- Assets ----------------------------------- #
class AssetBase(ORMModel):
    asset_num: str
    description: str
    location_id: Optional[int] = None
    parent_id: Optional[int] = None
    status: str = "OPERATING"
    asset_type: str = "EQUIPMENT"
    manufacturer: str = ""
    model: str = ""
    serial_num: str = ""
    install_date: Optional[datetime] = None
    purchase_cost: float = 0.0
    replacement_cost: float = 0.0
    criticality: int = 3
    health_score: int = 85
    site: str = "HQ"


class AssetCreate(AssetBase):
    pass


class AssetUpdate(ORMModel):
    description: Optional[str] = None
    location_id: Optional[int] = None
    status: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    criticality: Optional[int] = None
    health_score: Optional[int] = None


class Asset(AssetBase):
    id: int
    location: Optional[Location] = None
    meters: List[Meter] = []


# ------------------------------- Crafts/Labor ----------------------------- #
class CraftBase(ORMModel):
    code: str
    name: str
    standard_rate: float = 0.0


class CraftCreate(CraftBase):
    pass


class Craft(CraftBase):
    id: int


class LaborBase(ORMModel):
    labor_code: str
    name: str
    craft_id: Optional[int] = None
    hourly_rate: float = 0.0
    status: str = "ACTIVE"
    phone: str = ""
    email: str = ""


class LaborCreate(LaborBase):
    pass


class Labor(LaborBase):
    id: int
    craft: Optional[Craft] = None


# ------------------------------ Job Plans --------------------------------- #
class JobPlanTaskBase(ORMModel):
    sequence: int = 10
    description: str
    estimated_hours: float = 1.0


class JobPlanTaskCreate(JobPlanTaskBase):
    pass


class JobPlanTask(JobPlanTaskBase):
    id: int
    job_plan_id: int


class JobPlanBase(ORMModel):
    jp_num: str
    description: str
    estimated_duration: float = 0.0
    estimated_labor_cost: float = 0.0
    estimated_material_cost: float = 0.0


class JobPlanCreate(JobPlanBase):
    tasks: List[JobPlanTaskCreate] = []


class JobPlan(JobPlanBase):
    id: int
    tasks: List[JobPlanTask] = []


# ----------------------------- Work Orders -------------------------------- #
class WorkOrderBase(ORMModel):
    wo_num: str
    description: str
    asset_id: Optional[int] = None
    location_id: Optional[int] = None
    job_plan_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    status: str = "WAPPR"
    priority: int = 3
    work_type: str = "CM"
    reported_date: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_finish: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_finish: Optional[datetime] = None
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    site: str = "HQ"
    failure_code: str = ""


class WorkOrderCreate(ORMModel):
    description: str
    asset_id: Optional[int] = None
    location_id: Optional[int] = None
    job_plan_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    priority: int = 3
    work_type: str = "CM"
    scheduled_start: Optional[datetime] = None
    scheduled_finish: Optional[datetime] = None
    estimated_cost: float = 0.0
    estimated_hours: float = 0.0


class WorkOrderUpdate(ORMModel):
    # Note: status is intentionally excluded — status changes must go through
    # POST /workorders/{id}/status so the workflow guard & side effects apply.
    description: Optional[str] = None
    priority: Optional[int] = None
    assigned_to_id: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_finish: Optional[datetime] = None
    actual_cost: Optional[float] = None
    actual_hours: Optional[float] = None
    failure_code: Optional[str] = None


class WorkOrder(WorkOrderBase):
    id: int
    asset: Optional[Asset] = None
    location: Optional[Location] = None
    assigned_to: Optional[Labor] = None
    job_plan: Optional[JobPlan] = None


# ------------------------ Preventive Maintenance -------------------------- #
class PMBase(ORMModel):
    pm_num: str
    description: str
    asset_id: Optional[int] = None
    location_id: Optional[int] = None
    job_plan_id: Optional[int] = None
    frequency_days: int = 90
    last_generated: Optional[datetime] = None
    next_due: Optional[datetime] = None
    status: str = "ACTIVE"
    meter_based: bool = False
    meter_id: Optional[int] = None
    meter_frequency: Optional[float] = None
    priority: int = 3


class PMCreate(PMBase):
    pass


class PM(PMBase):
    id: int
    asset: Optional[Asset] = None
    location: Optional[Location] = None
    job_plan: Optional[JobPlan] = None


# -------------------------- Service Requests ------------------------------ #
class ServiceRequestBase(ORMModel):
    ticket_num: str
    description: str
    reported_by: str = ""
    affected_user: str = ""
    asset_id: Optional[int] = None
    location_id: Optional[int] = None
    status: str = "NEW"
    priority: int = 3
    reported_date: Optional[datetime] = None
    classification: str = ""


class ServiceRequestCreate(ORMModel):
    description: str
    reported_by: str = ""
    affected_user: str = ""
    asset_id: Optional[int] = None
    location_id: Optional[int] = None
    priority: int = 3
    classification: str = ""


class ServiceRequestUpdate(ORMModel):
    status: Optional[str] = None
    priority: Optional[int] = None


class ServiceRequest(ServiceRequestBase):
    id: int
    asset: Optional[Asset] = None
    location: Optional[Location] = None


# ------------------------------ Materials --------------------------------- #
class ItemBase(ORMModel):
    item_num: str
    description: str
    category: str = "GENERAL"
    unit_of_measure: str = "EACH"
    unit_cost: float = 0.0
    rotating: bool = False


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int


class StoreroomBase(ORMModel):
    code: str
    name: str
    location_id: Optional[int] = None


class Storeroom(StoreroomBase):
    id: int


class InventoryBase(ORMModel):
    item_id: int
    storeroom_id: int
    current_balance: float = 0.0
    reorder_point: float = 0.0
    reorder_quantity: float = 0.0
    unit_cost: float = 0.0
    bin: str = ""


class InventoryCreate(InventoryBase):
    pass


class InventoryAdjust(ORMModel):
    delta: float


class Inventory(InventoryBase):
    id: int
    item: Optional[Item] = None
    storeroom: Optional[Storeroom] = None


# ------------------------------ Purchasing -------------------------------- #
class VendorBase(ORMModel):
    code: str
    name: str
    contact: str = ""
    email: str = ""
    phone: str = ""
    rating: float = 0.0


class VendorCreate(VendorBase):
    pass


class Vendor(VendorBase):
    id: int


class POLineBase(ORMModel):
    item_id: Optional[int] = None
    description: str = ""
    quantity: float = 1.0
    unit_cost: float = 0.0
    line_cost: float = 0.0


class POLineCreate(POLineBase):
    pass


class POLine(POLineBase):
    id: int
    po_id: int


class PurchaseOrderBase(ORMModel):
    po_num: str
    vendor_id: Optional[int] = None
    status: str = "WAPPR"
    order_date: Optional[datetime] = None
    required_date: Optional[datetime] = None
    total_cost: float = 0.0
    description: str = ""


class PurchaseOrderCreate(ORMModel):
    vendor_id: Optional[int] = None
    description: str = ""
    required_date: Optional[datetime] = None
    lines: List[POLineCreate] = []


class PurchaseOrder(PurchaseOrderBase):
    id: int
    vendor: Optional[Vendor] = None
    lines: List[POLine] = []


# ------------------------------- AI Suite --------------------------------- #
class MonitorAlert(ORMModel):
    id: int
    asset_id: int
    alert_type: str
    severity: str
    metric: str
    message: str
    value: float
    status: str
    detected_at: Optional[datetime] = None
    asset: Optional[Asset] = None


class PredictForecast(ORMModel):
    id: int
    asset_id: int
    failure_probability: float
    remaining_useful_life_days: int
    predicted_failure_date: Optional[datetime] = None
    recommended_action: str
    confidence: float
    model_name: str
    generated_at: Optional[datetime] = None
    asset: Optional[Asset] = None


class VisualInspection(ORMModel):
    id: int
    asset_id: int
    image_label: str
    defect_detected: bool
    defect_type: str
    confidence: float
    inspection_date: Optional[datetime] = None
    inspector: str
    asset: Optional[Asset] = None


# ------------------------------- Generic ---------------------------------- #
class StatusUpdate(ORMModel):
    status: str


class AssistQuery(ORMModel):
    question: str
    asset_id: Optional[int] = None


class AssistResponse(ORMModel):
    answer: str
    sources: List[str] = []
    suggested_actions: List[str] = []
