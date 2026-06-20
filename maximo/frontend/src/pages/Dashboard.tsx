import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { DashboardData, WorkOrder, MonitorAlert, PM } from "../lib/types";
import { Kpi, Spinner, Badge, PriorityBadge, Donut, BarBreakdown, fmtMoney, fmtDate } from "../components/ui";

interface Trend { week: string; created: number; completed: number; }

export default function Dashboard() {
  const nav = useNavigate();
  const [d, setD] = useState<DashboardData | null>(null);
  const [trend, setTrend] = useState<Trend[]>([]);
  const [alerts, setAlerts] = useState<MonitorAlert[]>([]);
  const [pms, setPms] = useState<PM[]>([]);
  const [wos, setWos] = useState<WorkOrder[]>([]);

  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    api.get<DashboardData>("/api/dashboard").then(setD).catch(() => setLoadError("Failed to load dashboard data."));
    api.get<Trend[]>("/api/dashboard/wo-trend").then(setTrend).catch(() => {});
    api.get<MonitorAlert[]>("/api/ai/monitor/alerts?status=OPEN").then(setAlerts).catch(() => {});
    api.get<PM[]>("/api/pm").then(setPms).catch(() => {});
    api.get<WorkOrder[]>("/api/workorders").then(setWos).catch(() => {});
  }, []);

  if (loadError) return <div className="empty">{loadError}</div>;
  if (!d) return <Spinner />;

  const now = new Date();
  const overduePms = pms.filter((p) => p.next_due && new Date(p.next_due) < now).slice(0, 5);
  const recentWos = wos.slice(0, 6);
  const maxTrend = Math.max(...trend.flatMap((t) => [t.created, t.completed]), 1);

  const woStatusData = Object.entries(d.wo_by_status).map(([label, value]) => ({ label, value }));
  const statusColor = (k: string) =>
    ({ WAPPR: "var(--gray-50)", APPR: "var(--blue-60)", INPRG: "var(--purple)", COMP: "var(--green)", CLOSE: "var(--gray-70)", CAN: "var(--red)" }[k] || "var(--blue-60)");

  return (
    <>
      <div className="grid cols-4">
        <Kpi label="Total Assets" value={d.asset_count} sub={`${d.assets_operating} operating · ${d.assets_down} down`} />
        <Kpi label="Work Order Backlog" value={d.backlog_count} sub={`${d.work_order_count} total work orders`} tone={d.backlog_count > 8 ? "warn" : undefined} />
        <Kpi label="Overdue PMs" value={d.overdue_pm_count} sub={`${d.upcoming_pm_count} due this month`} tone={d.overdue_pm_count > 0 ? "danger" : "good"} />
        <Kpi label="Open AI Alerts" value={d.open_alert_count} sub={`${d.critical_alert_count} critical`} tone={d.critical_alert_count > 0 ? "danger" : undefined} />
      </div>

      <div className="grid cols-4" style={{ marginTop: 16 }}>
        <Kpi label="Avg Asset Health" value={`${d.avg_health}`} sub="0–100 condition index" tone={d.avg_health < 70 ? "warn" : "good"} />
        <Kpi label="Mean Time To Repair" value={`${d.mttr_hours}h`} sub="completed corrective work" />
        <Kpi label="Inventory Value" value={fmtMoney(d.inventory_value)} sub={`${d.below_reorder_count} items below reorder`} tone={d.below_reorder_count > 0 ? "warn" : undefined} />
        <Kpi label="Maintenance Cost" value={fmtMoney(d.total_maintenance_cost)} sub="actuals to date" />
      </div>

      <div className="grid cols-3" style={{ marginTop: 16 }}>
        <div className="card">
          <h3>Asset Health Distribution</h3>
          <Donut
            data={[
              { label: "Good (80+)", value: d.health_distribution.good, color: "var(--green)" },
              { label: "Fair (60–79)", value: d.health_distribution.fair, color: "var(--yellow)" },
              { label: "Poor (<60)", value: d.health_distribution.poor, color: "var(--red)" },
            ]}
          />
        </div>
        <div className="card">
          <h3>Work Orders by Status</h3>
          <BarBreakdown data={woStatusData} colorFor={statusColor} />
        </div>
        <div className="card">
          <h3>Work Orders by Type</h3>
          <BarBreakdown
            data={Object.entries(d.wo_by_type).map(([label, value]) => ({ label, value }))}
            colorFor={(k) => ({ CM: "var(--orange)", PM: "var(--blue-60)", EM: "var(--red)", INSP: "var(--teal)" }[k] || "var(--blue-60)")}
          />
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3>Work Order Volume (12 weeks)</h3>
        <div style={{ display: "flex", alignItems: "flex-end", gap: 10, height: 140, paddingTop: 10 }}>
          {trend.map((t) => (
            <div key={t.week} style={{ flex: 1, textAlign: "center" }}>
              <div style={{ display: "flex", flexDirection: "column", justifyContent: "flex-end", height: 110, gap: 2 }}>
                <div title={`Created ${t.created}`} style={{ background: "var(--blue-40)", height: `${(t.created / maxTrend) * 100}%`, borderRadius: "3px 3px 0 0" }} />
                <div title={`Completed ${t.completed}`} style={{ background: "var(--green)", height: `${(t.completed / maxTrend) * 100}%` }} />
              </div>
              <div style={{ fontSize: 9, color: "var(--gray-60)", marginTop: 4 }}>{t.week.split("-W")[1]}</div>
            </div>
          ))}
        </div>
        <div style={{ display: "flex", gap: 16, marginTop: 8, fontSize: 12 }}>
          <span><span style={{ display: "inline-block", width: 10, height: 10, background: "var(--blue-40)", borderRadius: 2 }} /> Created</span>
          <span><span style={{ display: "inline-block", width: 10, height: 10, background: "var(--green)", borderRadius: 2 }} /> Completed</span>
        </div>
      </div>

      <div className="grid cols-2" style={{ marginTop: 16 }}>
        <div className="card">
          <div className="card-title-row"><h3>Critical & Open Alerts</h3><div className="spacer" /><button type="button" className="btn ghost sm" onClick={() => nav("/ai/monitor")}>View all →</button></div>
          {alerts.slice(0, 5).map((a) => (
            <div key={a.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--gray-20)" }}>
              <Badge value={a.severity} />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 500 }}>{a.asset?.asset_num} — {a.metric}</div>
                <div className="muted" style={{ fontSize: 12 }}>{a.message}</div>
              </div>
            </div>
          ))}
          {alerts.length === 0 && <div className="muted">No open alerts.</div>}
        </div>

        <div className="card">
          <div className="card-title-row"><h3>Overdue Preventive Maintenance</h3><div className="spacer" /><button type="button" className="btn ghost sm" onClick={() => nav("/pm")}>View all →</button></div>
          {overduePms.map((p) => (
            <div key={p.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 0", borderBottom: "1px solid var(--gray-20)" }}>
              <span className="mono">{p.pm_num}</span>
              <div style={{ flex: 1 }}>{p.description}</div>
              <Badge value="Overdue" color="red" />
              <span className="muted" style={{ fontSize: 12 }}>{fmtDate(p.next_due)}</span>
            </div>
          ))}
          {overduePms.length === 0 && <div className="muted">No overdue PMs. 🎉</div>}
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <div className="card-title-row"><h3>Recent Work Orders</h3><div className="spacer" /><button type="button" className="btn ghost sm" onClick={() => nav("/workorders")}>View all →</button></div>
        <table>
          <thead><tr><th>WO</th><th>Description</th><th>Asset</th><th>Type</th><th>Priority</th><th>Status</th><th>Assigned</th></tr></thead>
          <tbody>
            {recentWos.map((w) => (
              <tr key={w.id} onClick={() => nav(`/workorders/${w.id}`)}>
                <td className="mono">{w.wo_num}</td>
                <td>{w.description}</td>
                <td>{w.asset?.asset_num || "—"}</td>
                <td><Badge value={w.work_type} color="gray" /></td>
                <td><PriorityBadge value={w.priority} /></td>
                <td><Badge value={w.status} /></td>
                <td>{w.assigned_to?.name || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
