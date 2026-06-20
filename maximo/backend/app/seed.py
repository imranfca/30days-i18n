"""Seed the Maximo clone database with realistic enterprise asset data."""
import random
from datetime import datetime, timedelta

from .database import Base, SessionLocal, engine
from . import models

random.seed(42)
NOW = datetime(2026, 6, 20)


def _dt(days_offset):
    return NOW + timedelta(days=days_offset)


def seed(force: bool = False):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Asset).count() > 0 and not force:
            return
        if force:
            for tbl in reversed(Base.metadata.sorted_tables):
                db.execute(tbl.delete())
            db.commit()

        # ---------------------- Locations ---------------------- #
        locations = [
            models.Location(code="HQ", name="Headquarters Campus", type="OPERATING", site="HQ"),
            models.Location(code="PLANT-A", name="Manufacturing Plant A", type="OPERATING", site="HQ", address="100 Industrial Way"),
            models.Location(code="PLANT-A-L1", name="Plant A — Production Line 1", type="OPERATING", site="HQ"),
            models.Location(code="PLANT-A-L2", name="Plant A — Production Line 2", type="OPERATING", site="HQ"),
            models.Location(code="UTILITY", name="Central Utility Building", type="OPERATING", site="HQ"),
            models.Location(code="HVAC-ZONE", name="HVAC Mechanical Room", type="OPERATING", site="HQ"),
            models.Location(code="FLEET-DEPOT", name="Fleet Depot", type="OPERATING", site="HQ"),
            models.Location(code="WAREHOUSE", name="Central Warehouse", type="STOREROOM", site="HQ"),
        ]
        db.add_all(locations)
        db.flush()
        loc = {l.code: l.id for l in locations}
        # parent relationships
        locations[2].parent_id = loc["PLANT-A"]
        locations[3].parent_id = loc["PLANT-A"]
        locations[5].parent_id = loc["UTILITY"]
        db.flush()

        # ---------------------- Crafts & Labor ---------------------- #
        crafts = [
            models.Craft(code="MECH", name="Mechanic", standard_rate=45.0),
            models.Craft(code="ELEC", name="Electrician", standard_rate=52.0),
            models.Craft(code="HVAC", name="HVAC Technician", standard_rate=48.0),
            models.Craft(code="INST", name="Instrumentation Tech", standard_rate=58.0),
            models.Craft(code="GEN", name="General Maintenance", standard_rate=38.0),
        ]
        db.add_all(crafts)
        db.flush()
        craft = {c.code: c.id for c in crafts}

        labor_data = [
            ("L-1001", "James Carter", "MECH", 46.0, "555-0101"),
            ("L-1002", "Maria Gomez", "ELEC", 54.0, "555-0102"),
            ("L-1003", "David Chen", "HVAC", 49.0, "555-0103"),
            ("L-1004", "Aisha Khan", "INST", 60.0, "555-0104"),
            ("L-1005", "Robert Smith", "MECH", 44.0, "555-0105"),
            ("L-1006", "Linda Park", "ELEC", 53.0, "555-0106"),
            ("L-1007", "Tom Nguyen", "GEN", 39.0, "555-0107"),
            ("L-1008", "Sarah Williams", "HVAC", 50.0, "555-0108"),
        ]
        labors = [
            models.Labor(labor_code=c, name=n, craft_id=craft[cr], hourly_rate=r,
                         phone=p, email=f"{n.split()[0].lower()}@maximo-demo.com")
            for c, n, cr, r, p in labor_data
        ]
        db.add_all(labors)
        db.flush()
        labor_ids = [l.id for l in labors]

        # ---------------------- Job Plans ---------------------- #
        job_plans_spec = [
            ("JP-100", "Quarterly Pump Inspection", [
                ("Lock out / tag out equipment", 0.5),
                ("Inspect seals and bearings", 1.0),
                ("Check alignment and vibration", 1.0),
                ("Lubricate and record readings", 0.5),
            ], 4.0),
            ("JP-200", "Annual Motor Overhaul", [
                ("De-energize and isolate motor", 0.5),
                ("Disassemble and clean windings", 2.0),
                ("Replace bearings", 1.5),
                ("Reassemble and test run", 2.0),
            ], 8.0),
            ("JP-300", "Monthly HVAC Filter Service", [
                ("Replace air filters", 0.5),
                ("Inspect belts and coils", 0.75),
                ("Check refrigerant pressures", 0.75),
            ], 3.0),
            ("JP-400", "Conveyor Belt PM", [
                ("Inspect belt tension and tracking", 1.0),
                ("Lubricate rollers", 0.5),
                ("Test emergency stops", 0.5),
            ], 4.0),
            ("JP-500", "Electrical Panel Inspection", [
                ("Thermographic scan of panel", 1.0),
                ("Torque check connections", 1.0),
                ("Test breakers", 1.0),
            ], 5.0),
            ("JP-600", "Vehicle Preventive Service", [
                ("Oil and filter change", 1.0),
                ("Brake and tire inspection", 1.0),
                ("Fluid top-up and diagnostics", 0.5),
            ], 3.0),
        ]
        job_plans = []
        for jp_num, desc, tasks, dur in job_plans_spec:
            jp = models.JobPlan(jp_num=jp_num, description=desc, estimated_duration=dur,
                                estimated_labor_cost=dur * 48, estimated_material_cost=dur * 25)
            for i, (tdesc, th) in enumerate(tasks):
                jp.tasks.append(models.JobPlanTask(sequence=(i + 1) * 10, description=tdesc, estimated_hours=th))
            job_plans.append(jp)
        db.add_all(job_plans)
        db.flush()
        jp = {j.jp_num: j.id for j in job_plans}

        # ---------------------- Assets ---------------------- #
        asset_specs = [
            ("PUMP-001", "Centrifugal Water Pump #1", "PLANT-A-L1", "OPERATING", "Grundfos", "CR-95", 1, 92, 24000),
            ("PUMP-002", "Centrifugal Water Pump #2", "PLANT-A-L1", "OPERATING", "Grundfos", "CR-95", 1, 67, 24000),
            ("PUMP-003", "Coolant Circulation Pump", "PLANT-A-L2", "DOWN", "KSB", "Etanorm", 2, 38, 18000),
            ("MOTOR-001", "200HP Drive Motor Line 1", "PLANT-A-L1", "OPERATING", "Siemens", "1LE1", 1, 88, 32000),
            ("MOTOR-002", "150HP Drive Motor Line 2", "PLANT-A-L2", "OPERATING", "ABB", "M3BP", 2, 74, 28000),
            ("CONV-001", "Main Assembly Conveyor", "PLANT-A-L1", "OPERATING", "Dorner", "3200", 2, 81, 45000),
            ("CONV-002", "Packaging Conveyor", "PLANT-A-L2", "OPERATING", "Hytrol", "TA", 3, 90, 22000),
            ("HVAC-001", "Rooftop AHU North", "HVAC-ZONE", "OPERATING", "Carrier", "48TC", 2, 79, 65000),
            ("HVAC-002", "Chiller Unit 1", "HVAC-ZONE", "OPERATING", "Trane", "RTAC", 1, 56, 120000),
            ("PANEL-001", "Main Distribution Panel", "UTILITY", "OPERATING", "Schneider", "PowerPact", 1, 95, 40000),
            ("GEN-001", "Backup Diesel Generator", "UTILITY", "OPERATING", "Cummins", "C1100D5", 1, 84, 95000),
            ("COMP-001", "Air Compressor 500CFM", "UTILITY", "OPERATING", "Atlas Copco", "GA-90", 2, 71, 38000),
            ("FORK-001", "Forklift Toyota 8FGU25", "FLEET-DEPOT", "OPERATING", "Toyota", "8FGU25", 3, 86, 35000),
            ("FORK-002", "Forklift Hyster H50FT", "FLEET-DEPOT", "DOWN", "Hyster", "H50FT", 3, 42, 33000),
            ("TRUCK-001", "Delivery Truck #1", "FLEET-DEPOT", "OPERATING", "Ford", "F-650", 3, 77, 78000),
            ("BOIL-001", "Steam Boiler Unit", "UTILITY", "OPERATING", "Cleaver-Brooks", "CBEX", 1, 63, 150000),
        ]
        assets = []
        for an, desc, lcode, status, mfg, model, crit, health, cost in asset_specs:
            assets.append(models.Asset(
                asset_num=an, description=desc, location_id=loc[lcode], status=status,
                manufacturer=mfg, model=model, serial_num=f"SN{random.randint(100000, 999999)}",
                install_date=_dt(-random.randint(400, 2200)), purchase_cost=cost,
                replacement_cost=cost * 1.3, criticality=crit, health_score=health,
                asset_type="EQUIPMENT" if "FORK" not in an and "TRUCK" not in an else "FLEET",
            ))
        db.add_all(assets)
        db.flush()
        asset = {a.asset_num: a.id for a in assets}
        asset_by_id = {a.id: a for a in assets}

        # ---------------------- Meters & Readings ---------------------- #
        meter_specs = [
            ("PUMP-001", "VIBRATION", "mm/s", 2.1, 4.5, 7.0),
            ("PUMP-002", "VIBRATION", "mm/s", 5.8, 4.5, 7.0),
            ("PUMP-003", "VIBRATION", "mm/s", 8.2, 4.5, 7.0),
            ("MOTOR-001", "RUNTIME-HRS", "hrs", 14200, None, None),
            ("MOTOR-002", "TEMP", "°C", 78, 75, 90),
            ("HVAC-002", "TEMP", "°C", 6.4, 8, 12),
            ("COMP-001", "PRESSURE", "psi", 118, 130, 145),
            ("GEN-001", "RUNTIME-HRS", "hrs", 980, None, None),
            ("BOIL-001", "PRESSURE", "psi", 142, 150, 165),
        ]
        meters = []
        for an, name, unit, last, warn, act in meter_specs:
            m = models.Meter(asset_id=asset[an], name=name, unit=unit, last_reading=last,
                             last_reading_date=_dt(-random.randint(0, 5)),
                             warning_limit=warn, action_limit=act)
            meters.append(m)
        db.add_all(meters)
        db.flush()
        for m in meters:
            base = m.last_reading
            for d in range(12, 0, -1):
                jitter = base * random.uniform(0.85, 1.0)
                db.add(models.MeterReading(meter_id=m.id, reading=round(jitter, 2), reading_date=_dt(-d * 7)))
        db.flush()

        # ---------------------- Preventive Maintenance ---------------------- #
        pm_specs = [
            ("PM-001", "Quarterly Pump Inspection — Pump 1", "PUMP-001", "JP-100", 90, -15),
            ("PM-002", "Quarterly Pump Inspection — Pump 2", "PUMP-002", "JP-100", 90, 5),
            ("PM-003", "Annual Motor Overhaul — Motor 1", "MOTOR-001", "JP-200", 365, 40),
            ("PM-004", "Monthly HVAC Filter Service — AHU", "HVAC-001", "JP-300", 30, -3),
            ("PM-005", "Monthly HVAC Filter Service — Chiller", "HVAC-002", "JP-300", 30, 12),
            ("PM-006", "Conveyor PM — Main Assembly", "CONV-001", "JP-400", 60, -8),
            ("PM-007", "Electrical Panel Inspection", "PANEL-001", "JP-500", 180, 25),
            ("PM-008", "Forklift Service — Toyota", "FORK-001", "JP-600", 90, 2),
            ("PM-009", "Generator Monthly Test", "GEN-001", "JP-500", 30, -1),
            ("PM-010", "Compressor Quarterly PM", "COMP-001", "JP-100", 90, 18),
        ]
        for pm_num, desc, an, jpnum, freq, due_offset in pm_specs:
            db.add(models.PreventiveMaintenance(
                pm_num=pm_num, description=desc, asset_id=asset[an], job_plan_id=jp[jpnum],
                frequency_days=freq, last_generated=_dt(due_offset - freq),
                next_due=_dt(due_offset), status="ACTIVE",
                priority=asset_by_id[asset[an]].criticality,
            ))
        db.flush()

        # ---------------------- Work Orders ---------------------- #
        wo_templates = [
            ("Replace worn pump seal", "PUMP-002", "CM", "INPRG", 1),
            ("Coolant pump not starting — investigate", "PUMP-003", "EM", "INPRG", 1),
            ("Quarterly pump inspection", "PUMP-001", "PM", "APPR", 3),
            ("Motor bearing noise diagnosis", "MOTOR-002", "CM", "WAPPR", 2),
            ("Replace HVAC filters and inspect coils", "HVAC-001", "PM", "COMP", 3),
            ("Chiller low refrigerant — recharge", "HVAC-002", "CM", "APPR", 2),
            ("Conveyor belt tracking adjustment", "CONV-001", "CM", "INPRG", 3),
            ("Forklift hydraulic leak repair", "FORK-002", "EM", "WAPPR", 2),
            ("Generator load bank test", "GEN-001", "PM", "APPR", 3),
            ("Compressor pressure switch replacement", "COMP-001", "CM", "WAPPR", 3),
            ("Panel thermographic inspection", "PANEL-001", "INSP", "COMP", 3),
            ("Boiler pressure relief valve test", "BOIL-001", "PM", "APPR", 1),
            ("Truck brake service", "TRUCK-001", "PM", "COMP", 3),
            ("Replace conveyor drive belt", "CONV-002", "CM", "CLOSE", 3),
            ("Lubricate line 1 drive motor", "MOTOR-001", "PM", "COMP", 4),
            ("Investigate vibration alarm on pump", "PUMP-002", "CM", "APPR", 1),
        ]
        for i, (desc, an, wtype, status, prio) in enumerate(wo_templates):
            aid = asset[an]
            sched = _dt(random.randint(-20, 20))
            est_hrs = random.choice([2, 3, 4, 6, 8])
            wo = models.WorkOrder(
                wo_num=f"WO-{2001 + i}", description=desc, asset_id=aid,
                location_id=asset_by_id[aid].location_id, status=status, priority=prio,
                work_type=wtype, reported_date=_dt(-random.randint(1, 30)),
                scheduled_start=sched, scheduled_finish=sched + timedelta(hours=est_hrs),
                assigned_to_id=random.choice(labor_ids), estimated_hours=est_hrs,
                estimated_cost=est_hrs * 48 + random.randint(50, 500),
            )
            if status in ("COMP", "CLOSE"):
                wo.actual_start = sched
                wo.actual_finish = sched + timedelta(hours=est_hrs * random.uniform(0.8, 1.4))
                wo.actual_hours = round(est_hrs * random.uniform(0.8, 1.4), 1)
                wo.actual_cost = round(wo.actual_hours * 48 + random.randint(50, 500), 2)
            db.add(wo)
        db.flush()

        # ---------------------- Service Requests ---------------------- #
        sr_specs = [
            ("AC not cooling in office area", "HVAC-001", "NEW", 2, "Jane Doe"),
            ("Strange noise from production line 2", "MOTOR-002", "QUEUED", 2, "Floor Supervisor"),
            ("Forklift #2 won't lift loads", "FORK-002", "INPROG", 1, "Warehouse Lead"),
            ("Lights flickering in utility area", "PANEL-001", "RESOLVED", 3, "Security"),
            ("Water leak near pump station", "PUMP-003", "INPROG", 1, "Operator"),
            ("Compressor running loud", "COMP-001", "NEW", 3, "Maintenance"),
            ("Conveyor jammed intermittently", "CONV-001", "QUEUED", 2, "Line Operator"),
        ]
        for i, (desc, an, status, prio, reporter) in enumerate(sr_specs):
            db.add(models.ServiceRequest(
                ticket_num=f"SR-{3001 + i}", description=desc, asset_id=asset[an],
                location_id=asset_by_id[asset[an]].location_id, status=status, priority=prio,
                reported_by=reporter, affected_user=reporter,
                reported_date=_dt(-random.randint(1, 14)), classification="Equipment Problem",
            ))
        db.flush()

        # ---------------------- Items, Storerooms, Inventory ---------------------- #
        store = models.Storeroom(code="CENTRAL", name="Central Warehouse", location_id=loc["WAREHOUSE"])
        store2 = models.Storeroom(code="PLANT-A-SR", name="Plant A Storeroom", location_id=loc["PLANT-A"])
        db.add_all([store, store2])
        db.flush()

        item_specs = [
            ("ITM-1001", "Mechanical Pump Seal 2in", "SEALS", "EACH", 85.0, 12, 8, 20),
            ("ITM-1002", "SKF Deep Groove Bearing 6205", "BEARINGS", "EACH", 24.5, 30, 15, 40),
            ("ITM-1003", "HVAC Air Filter 20x25x4", "FILTERS", "EACH", 18.0, 6, 24, 48),
            ("ITM-1004", "V-Belt A-Section 4L360", "BELTS", "EACH", 12.0, 20, 10, 30),
            ("ITM-1005", "Synthetic Lubricant ISO 68 5gal", "LUBRICANTS", "PAIL", 95.0, 4, 5, 12),
            ("ITM-1006", "Circuit Breaker 100A 3-Pole", "ELECTRICAL", "EACH", 145.0, 8, 4, 10),
            ("ITM-1007", "Hydraulic Hose 1/2in", "HYDRAULICS", "FOOT", 6.5, 50, 40, 100),
            ("ITM-1008", "Refrigerant R-410A 25lb", "HVAC", "CYLINDER", 210.0, 2, 3, 6),
            ("ITM-1009", "Motor Coupling Spider", "MECHANICAL", "EACH", 34.0, 14, 8, 20),
            ("ITM-1010", "Pressure Switch 0-150psi", "INSTRUMENTS", "EACH", 67.0, 5, 4, 10),
            ("ITM-1011", "Diesel Engine Oil Filter", "FILTERS", "EACH", 22.0, 16, 10, 24),
            ("ITM-1012", "Conveyor Roller 50mm", "MECHANICAL", "EACH", 41.0, 9, 6, 15),
        ]
        for inum, desc, cat, uom, cost, bal, rop, roq in item_specs:
            it = models.Item(item_num=inum, description=desc, category=cat,
                             unit_of_measure=uom, unit_cost=cost,
                             rotating=cat in ("MECHANICAL", "ELECTRICAL"))
            db.add(it)
            db.flush()
            db.add(models.Inventory(item_id=it.id, storeroom_id=store.id, current_balance=bal,
                                    reorder_point=rop, reorder_quantity=roq, unit_cost=cost,
                                    bin=f"A-{random.randint(1, 40):02d}"))
        db.flush()

        # ---------------------- Vendors & Purchase Orders ---------------------- #
        vendors = [
            models.Vendor(code="V-100", name="Industrial Supply Co", contact="Mark Lee",
                          email="sales@indsupply.com", phone="555-0200", rating=4.5),
            models.Vendor(code="V-200", name="Bearings & Power Transmission", contact="Nina Patel",
                          email="orders@bptrans.com", phone="555-0201", rating=4.1),
            models.Vendor(code="V-300", name="HVAC Wholesale Direct", contact="Carlos Ruiz",
                          email="info@hvacwd.com", phone="555-0202", rating=3.8),
            models.Vendor(code="V-400", name="ElectroParts Inc", contact="Dana White",
                          email="quotes@electroparts.com", phone="555-0203", rating=4.7),
        ]
        db.add_all(vendors)
        db.flush()
        items_all = db.query(models.Item).all()
        po_status = ["WAPPR", "APPR", "INPRG", "RECEIVED", "CLOSE"]
        for i in range(6):
            po = models.PurchaseOrder(
                po_num=f"PO-{4001 + i}", vendor_id=random.choice(vendors).id,
                status=random.choice(po_status), order_date=_dt(-random.randint(1, 45)),
                required_date=_dt(random.randint(3, 30)), description="Maintenance parts replenishment",
            )
            db.add(po)
            db.flush()
            total = 0.0
            for _ in range(random.randint(1, 3)):
                it = random.choice(items_all)
                qty = random.randint(2, 20)
                line_cost = round(qty * it.unit_cost, 2)
                total += line_cost
                db.add(models.POLine(po_id=po.id, item_id=it.id, description=it.description,
                                     quantity=qty, unit_cost=it.unit_cost, line_cost=line_cost))
            po.total_cost = round(total, 2)
        db.flush()

        # ---------------------- AI: Monitor Alerts ---------------------- #
        alert_specs = [
            ("PUMP-002", "ANOMALY", "HIGH", "VIBRATION", "Vibration trending above baseline — bearing wear likely", 5.8),
            ("PUMP-003", "THRESHOLD", "CRITICAL", "VIBRATION", "Vibration exceeded action limit (8.2 > 7.0 mm/s)", 8.2),
            ("MOTOR-002", "THRESHOLD", "MEDIUM", "TEMP", "Winding temperature approaching warning limit", 78.0),
            ("HVAC-002", "DRIFT", "MEDIUM", "TEMP", "Supply temperature drifting — possible refrigerant loss", 6.4),
            ("COMP-001", "ANOMALY", "LOW", "PRESSURE", "Pressure cycling pattern deviates from normal", 118.0),
            ("BOIL-001", "THRESHOLD", "HIGH", "PRESSURE", "Pressure near warning threshold under load", 142.0),
            ("FORK-002", "ANOMALY", "HIGH", "HYDRAULIC", "Hydraulic pressure drop detected", 0.0),
        ]
        for an, atype, sev, metric, msg, val in alert_specs:
            db.add(models.MonitorAlert(asset_id=asset[an], alert_type=atype, severity=sev,
                                       metric=metric, message=msg, value=val, status="OPEN",
                                       detected_at=_dt(-random.randint(0, 6))))
        db.flush()

        # ---------------------- AI: Predict Forecasts ---------------------- #
        for a in assets:
            if a.health_score < 80:
                prob = round((80 - a.health_score) / 100 + random.uniform(0.05, 0.25), 2)
                prob = min(prob, 0.97)
                rul = int(max(5, (a.health_score / 100) * 365 * random.uniform(0.4, 1.2)))
                action = "Schedule corrective work order" if prob > 0.6 else "Monitor closely; plan inspection"
                if prob > 0.8:
                    action = "Urgent: plan immediate intervention to avoid failure"
                db.add(models.PredictForecast(
                    asset_id=a.id, failure_probability=prob, remaining_useful_life_days=rul,
                    predicted_failure_date=_dt(rul), recommended_action=action,
                    confidence=round(random.uniform(0.72, 0.95), 2), generated_at=_dt(-1),
                ))
        db.flush()

        # ---------------------- AI: Visual Inspections ---------------------- #
        vi_specs = [
            ("PUMP-003", "pump_housing_thermal.jpg", True, "Corrosion", 0.91),
            ("MOTOR-002", "motor_terminal_box.jpg", True, "Loose Connection", 0.84),
            ("CONV-001", "belt_surface.jpg", True, "Surface Crack", 0.78),
            ("PANEL-001", "panel_thermal.jpg", False, "", 0.96),
            ("HVAC-001", "coil_inspection.jpg", True, "Fouling", 0.88),
            ("BOIL-001", "weld_seam.jpg", False, "", 0.93),
            ("FORK-002", "hydraulic_cylinder.jpg", True, "Oil Leak", 0.89),
        ]
        for an, label, defect, dtype, conf in vi_specs:
            db.add(models.VisualInspection(asset_id=asset[an], image_label=label,
                                           defect_detected=defect, defect_type=dtype,
                                           confidence=conf, inspection_date=_dt(-random.randint(1, 10))))
        db.commit()
        print("Database seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    seed(force="--force" in sys.argv)
