"""SQLAlchemy ORM models for the Maximo-style Enterprise Asset Management suite."""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


# --------------------------------------------------------------------------- #
#  Foundation: Locations, Assets, Meters
# --------------------------------------------------------------------------- #
class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, default="OPERATING")  # OPERATING, COURIER, STOREROOM, VENDOR
    parent_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    status = Column(String, default="OPERATING")
    address = Column(String, default="")
    site = Column(String, default="HQ")

    parent = relationship("Location", remote_side=[id], backref="children")
    assets = relationship("Asset", back_populates="location")


class Asset(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    asset_num = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    parent_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    status = Column(String, default="OPERATING")  # OPERATING, DOWN, DECOMMISSIONED
    asset_type = Column(String, default="EQUIPMENT")
    manufacturer = Column(String, default="")
    model = Column(String, default="")
    serial_num = Column(String, default="")
    install_date = Column(DateTime, default=datetime.utcnow)
    purchase_cost = Column(Float, default=0.0)
    replacement_cost = Column(Float, default=0.0)
    criticality = Column(Integer, default=3)  # 1 (highest) .. 5 (lowest)
    health_score = Column(Integer, default=85)  # 0..100
    site = Column(String, default="HQ")

    location = relationship("Location", back_populates="assets")
    parent = relationship("Asset", remote_side=[id], backref="children")
    work_orders = relationship("WorkOrder", back_populates="asset")
    meters = relationship("Meter", back_populates="asset", cascade="all, delete-orphan")


class Meter(Base):
    __tablename__ = "meters"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g. RUNTIME-HRS, VIBRATION, TEMP
    unit = Column(String, default="")
    meter_type = Column(String, default="CONTINUOUS")  # CONTINUOUS, GAUGE
    last_reading = Column(Float, default=0.0)
    last_reading_date = Column(DateTime, default=datetime.utcnow)
    warning_limit = Column(Float, nullable=True)
    action_limit = Column(Float, nullable=True)

    asset = relationship("Asset", back_populates="meters")
    readings = relationship("MeterReading", back_populates="meter", cascade="all, delete-orphan")


class MeterReading(Base):
    __tablename__ = "meter_readings"
    id = Column(Integer, primary_key=True, index=True)
    meter_id = Column(Integer, ForeignKey("meters.id"), nullable=False)
    reading = Column(Float, nullable=False)
    reading_date = Column(DateTime, default=datetime.utcnow)

    meter = relationship("Meter", back_populates="readings")


# --------------------------------------------------------------------------- #
#  Work: Job Plans, Work Orders, Preventive Maintenance, Service Requests
# --------------------------------------------------------------------------- #
class Craft(Base):
    __tablename__ = "crafts"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    standard_rate = Column(Float, default=0.0)


class Labor(Base):
    __tablename__ = "labor"
    id = Column(Integer, primary_key=True, index=True)
    labor_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    craft_id = Column(Integer, ForeignKey("crafts.id"), nullable=True)
    hourly_rate = Column(Float, default=0.0)
    status = Column(String, default="ACTIVE")
    phone = Column(String, default="")
    email = Column(String, default="")

    craft = relationship("Craft")


class JobPlan(Base):
    __tablename__ = "job_plans"
    id = Column(Integer, primary_key=True, index=True)
    jp_num = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    estimated_duration = Column(Float, default=0.0)  # hours
    estimated_labor_cost = Column(Float, default=0.0)
    estimated_material_cost = Column(Float, default=0.0)

    tasks = relationship("JobPlanTask", back_populates="job_plan", cascade="all, delete-orphan")


class JobPlanTask(Base):
    __tablename__ = "job_plan_tasks"
    id = Column(Integer, primary_key=True, index=True)
    job_plan_id = Column(Integer, ForeignKey("job_plans.id"), nullable=False)
    sequence = Column(Integer, default=10)
    description = Column(String, nullable=False)
    estimated_hours = Column(Float, default=1.0)

    job_plan = relationship("JobPlan", back_populates="tasks")


class WorkOrder(Base):
    __tablename__ = "work_orders"
    id = Column(Integer, primary_key=True, index=True)
    wo_num = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    job_plan_id = Column(Integer, ForeignKey("job_plans.id"), nullable=True)
    assigned_to_id = Column(Integer, ForeignKey("labor.id"), nullable=True)
    status = Column(String, default="WAPPR")  # WAPPR, APPR, INPRG, COMP, CLOSE, CAN
    priority = Column(Integer, default=3)  # 1 (urgent) .. 5
    work_type = Column(String, default="CM")  # CM, PM, EM, INSP
    reported_date = Column(DateTime, default=datetime.utcnow)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_finish = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_finish = Column(DateTime, nullable=True)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    pm_id = Column(Integer, ForeignKey("preventive_maintenance.id"), nullable=True)
    sr_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True)
    site = Column(String, default="HQ")
    failure_code = Column(String, default="")

    asset = relationship("Asset", back_populates="work_orders")
    location = relationship("Location")
    job_plan = relationship("JobPlan")
    assigned_to = relationship("Labor")


class PreventiveMaintenance(Base):
    __tablename__ = "preventive_maintenance"
    id = Column(Integer, primary_key=True, index=True)
    pm_num = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    job_plan_id = Column(Integer, ForeignKey("job_plans.id"), nullable=True)
    frequency_days = Column(Integer, default=90)
    last_generated = Column(DateTime, nullable=True)
    next_due = Column(DateTime, nullable=True)
    status = Column(String, default="ACTIVE")
    meter_based = Column(Boolean, default=False)
    meter_id = Column(Integer, ForeignKey("meters.id"), nullable=True)
    meter_frequency = Column(Float, nullable=True)
    priority = Column(Integer, default=3)

    asset = relationship("Asset")
    location = relationship("Location")
    job_plan = relationship("JobPlan")


class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id = Column(Integer, primary_key=True, index=True)
    ticket_num = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    reported_by = Column(String, default="")
    affected_user = Column(String, default="")
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    status = Column(String, default="NEW")  # NEW, QUEUED, INPROG, RESOLVED, CLOSED
    priority = Column(Integer, default=3)
    reported_date = Column(DateTime, default=datetime.utcnow)
    classification = Column(String, default="")

    asset = relationship("Asset")
    location = relationship("Location")


# --------------------------------------------------------------------------- #
#  Materials: Items, Storerooms, Inventory, Vendors, Purchasing
# --------------------------------------------------------------------------- #
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    item_num = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, default="GENERAL")
    unit_of_measure = Column(String, default="EACH")
    unit_cost = Column(Float, default=0.0)
    rotating = Column(Boolean, default=False)


class Storeroom(Base):
    __tablename__ = "storerooms"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    location = relationship("Location")


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    storeroom_id = Column(Integer, ForeignKey("storerooms.id"), nullable=False)
    current_balance = Column(Float, default=0.0)
    reorder_point = Column(Float, default=0.0)
    reorder_quantity = Column(Float, default=0.0)
    unit_cost = Column(Float, default=0.0)
    bin = Column(String, default="")

    item = relationship("Item")
    storeroom = relationship("Storeroom")


class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    contact = Column(String, default="")
    email = Column(String, default="")
    phone = Column(String, default="")
    rating = Column(Float, default=0.0)  # 0..5


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True, index=True)
    po_num = Column(String, unique=True, index=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    status = Column(String, default="WAPPR")  # WAPPR, APPR, INPRG, RECEIVED, CLOSE
    order_date = Column(DateTime, default=datetime.utcnow)
    required_date = Column(DateTime, nullable=True)
    total_cost = Column(Float, default=0.0)
    description = Column(String, default="")

    vendor = relationship("Vendor")
    lines = relationship("POLine", back_populates="purchase_order", cascade="all, delete-orphan")


class POLine(Base):
    __tablename__ = "po_lines"
    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    description = Column(String, default="")
    quantity = Column(Float, default=1.0)
    unit_cost = Column(Float, default=0.0)
    line_cost = Column(Float, default=0.0)

    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    item = relationship("Item")


# --------------------------------------------------------------------------- #
#  AI Suite: Monitor, Health, Predict, Visual Inspection
# --------------------------------------------------------------------------- #
class MonitorAlert(Base):
    """Maximo Monitor — anomaly detection on IoT/meter data."""
    __tablename__ = "monitor_alerts"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    alert_type = Column(String, default="ANOMALY")  # ANOMALY, THRESHOLD, DRIFT
    severity = Column(String, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    metric = Column(String, default="")
    message = Column(String, default="")
    value = Column(Float, default=0.0)
    status = Column(String, default="OPEN")  # OPEN, ACKNOWLEDGED, CLOSED
    detected_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset")


class PredictForecast(Base):
    """Maximo Predict — failure probability & remaining useful life."""
    __tablename__ = "predict_forecasts"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    failure_probability = Column(Float, default=0.0)  # 0..1
    remaining_useful_life_days = Column(Integer, default=0)
    predicted_failure_date = Column(DateTime, nullable=True)
    recommended_action = Column(String, default="")
    confidence = Column(Float, default=0.0)  # 0..1
    model_name = Column(String, default="RUL-XGBoost-v2")
    generated_at = Column(DateTime, default=datetime.utcnow)

    asset = relationship("Asset")


class VisualInspection(Base):
    """Maximo Visual Inspection — computer-vision defect detection."""
    __tablename__ = "visual_inspections"
    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    image_label = Column(String, default="")
    defect_detected = Column(Boolean, default=False)
    defect_type = Column(String, default="")
    confidence = Column(Float, default=0.0)  # 0..1
    inspection_date = Column(DateTime, default=datetime.utcnow)
    inspector = Column(String, default="MVI-Model")

    asset = relationship("Asset")
