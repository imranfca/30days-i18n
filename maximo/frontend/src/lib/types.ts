export interface Location {
  id: number;
  code: string;
  name: string;
  type: string;
  status: string;
  address: string;
  site: string;
  parent_id?: number | null;
}

export interface Meter {
  id: number;
  asset_id: number;
  name: string;
  unit: string;
  meter_type: string;
  last_reading: number;
  last_reading_date?: string;
  warning_limit?: number | null;
  action_limit?: number | null;
}

export interface MeterReading {
  id: number;
  meter_id: number;
  reading: number;
  reading_date?: string;
}

export interface Asset {
  id: number;
  asset_num: string;
  description: string;
  location_id?: number | null;
  status: string;
  asset_type: string;
  manufacturer: string;
  model: string;
  serial_num: string;
  install_date?: string;
  purchase_cost: number;
  replacement_cost: number;
  criticality: number;
  health_score: number;
  site: string;
  location?: Location | null;
  meters?: Meter[];
}

export interface Labor {
  id: number;
  labor_code: string;
  name: string;
  craft_id?: number | null;
  hourly_rate: number;
  status: string;
  phone: string;
  email: string;
  craft?: Craft | null;
}

export interface Craft {
  id: number;
  code: string;
  name: string;
  standard_rate: number;
}

export interface JobPlanTask {
  id: number;
  sequence: number;
  description: string;
  estimated_hours: number;
}

export interface JobPlan {
  id: number;
  jp_num: string;
  description: string;
  estimated_duration: number;
  estimated_labor_cost: number;
  estimated_material_cost: number;
  tasks: JobPlanTask[];
}

export interface WorkOrder {
  id: number;
  wo_num: string;
  description: string;
  asset_id?: number | null;
  location_id?: number | null;
  status: string;
  priority: number;
  work_type: string;
  reported_date?: string;
  scheduled_start?: string | null;
  scheduled_finish?: string | null;
  actual_start?: string | null;
  actual_finish?: string | null;
  estimated_cost: number;
  actual_cost: number;
  estimated_hours: number;
  actual_hours: number;
  failure_code: string;
  asset?: Asset | null;
  location?: Location | null;
  assigned_to?: Labor | null;
  job_plan?: JobPlan | null;
}

export interface PM {
  id: number;
  pm_num: string;
  description: string;
  asset_id?: number | null;
  job_plan_id?: number | null;
  frequency_days: number;
  last_generated?: string | null;
  next_due?: string | null;
  status: string;
  meter_based: boolean;
  priority: number;
  asset?: Asset | null;
  job_plan?: JobPlan | null;
}

export interface ServiceRequest {
  id: number;
  ticket_num: string;
  description: string;
  reported_by: string;
  affected_user: string;
  status: string;
  priority: number;
  reported_date?: string;
  classification: string;
  asset?: Asset | null;
  location?: Location | null;
}

export interface Item {
  id: number;
  item_num: string;
  description: string;
  category: string;
  unit_of_measure: string;
  unit_cost: number;
  rotating: boolean;
}

export interface Storeroom {
  id: number;
  code: string;
  name: string;
}

export interface Inventory {
  id: number;
  item_id: number;
  storeroom_id: number;
  current_balance: number;
  reorder_point: number;
  reorder_quantity: number;
  unit_cost: number;
  bin: string;
  item?: Item | null;
  storeroom?: Storeroom | null;
}

export interface Vendor {
  id: number;
  code: string;
  name: string;
  contact: string;
  email: string;
  phone: string;
  rating: number;
}

export interface POLine {
  id: number;
  item_id?: number | null;
  description: string;
  quantity: number;
  unit_cost: number;
  line_cost: number;
}

export interface PurchaseOrder {
  id: number;
  po_num: string;
  vendor_id?: number | null;
  status: string;
  order_date?: string;
  required_date?: string | null;
  total_cost: number;
  description: string;
  vendor?: Vendor | null;
  lines: POLine[];
}

export interface MonitorAlert {
  id: number;
  asset_id: number;
  alert_type: string;
  severity: string;
  metric: string;
  message: string;
  value: number;
  status: string;
  detected_at?: string;
  asset?: Asset | null;
}

export interface PredictForecast {
  id: number;
  asset_id: number;
  failure_probability: number;
  remaining_useful_life_days: number;
  predicted_failure_date?: string | null;
  recommended_action: string;
  confidence: number;
  model_name: string;
  asset?: Asset | null;
}

export interface VisualInspection {
  id: number;
  asset_id: number;
  image_label: string;
  defect_detected: boolean;
  defect_type: string;
  confidence: number;
  inspection_date?: string;
  inspector: string;
  asset?: Asset | null;
}

export interface DashboardData {
  asset_count: number;
  assets_operating: number;
  assets_down: number;
  avg_health: number;
  health_distribution: { good: number; fair: number; poor: number };
  work_order_count: number;
  wo_by_status: Record<string, number>;
  backlog_count: number;
  wo_by_type: Record<string, number>;
  overdue_pm_count: number;
  upcoming_pm_count: number;
  inventory_value: number;
  below_reorder_count: number;
  open_alert_count: number;
  critical_alert_count: number;
  mttr_hours: number;
  total_maintenance_cost: number;
}
