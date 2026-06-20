import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { MonitorAlert, WorkOrder } from "../lib/types";
import { Badge, Spinner, Kpi, fmtDate } from "../components/ui";

export default function Monitor() {
  const nav = useNavigate();
  const [alerts, setAlerts] = useState<MonitorAlert[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = () => api.get<MonitorAlert[]>("/api/ai/monitor/alerts").then((d) => setAlerts(d)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const ack = async (a: MonitorAlert) => { await api.post(`/api/ai/monitor/alerts/${a.id}/acknowledge`); load(); };
  const createWo = async (a: MonitorAlert) => {
    if (busyId !== null) return;
    setBusyId(a.id);
    try {
      const wo = await api.post<WorkOrder>(`/api/ai/monitor/alerts/${a.id}/create-wo`);
      await load();
      if (confirm(`Created ${wo.wo_num} from alert. Open it?`)) nav(`/workorders/${wo.id}`);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setBusyId(null);
    }
  };

  if (loading) return <Spinner />;
  const open = alerts.filter((a) => a.status === "OPEN");
  const bySev = (s: string) => open.filter((a) => a.severity === s).length;

  return (
    <>
      <p className="muted" style={{ marginTop: 0 }}>Maximo Monitor ingests sensor & meter data and applies anomaly detection to surface developing failures before they cause downtime.</p>
      <div className="grid cols-4">
        <Kpi label="Critical" value={bySev("CRITICAL")} tone="danger" />
        <Kpi label="High" value={bySev("HIGH")} tone="warn" />
        <Kpi label="Medium" value={bySev("MEDIUM")} />
        <Kpi label="Open Total" value={open.length} />
      </div>
      <div className="table-wrap" style={{ marginTop: 16 }}>
        <table>
          <thead><tr><th>Severity</th><th>Asset</th><th>Metric</th><th>Type</th><th>Message</th><th>Value</th><th>Detected</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {alerts.map((a) => (
              <tr key={a.id} className="norow">
                <td><Badge value={a.severity} /></td>
                <td className="mono" style={{ cursor: "pointer" }} onClick={() => nav(`/assets/${a.asset_id}`)}>{a.asset?.asset_num}</td>
                <td>{a.metric}</td>
                <td><Badge value={a.alert_type} color="gray" /></td>
                <td>{a.message}</td>
                <td>{a.value ?? "—"}</td>
                <td>{fmtDate(a.detected_at)}</td>
                <td><Badge value={a.status} /></td>
                <td style={{ whiteSpace: "nowrap" }}>
                  {a.status === "OPEN" && <button className="btn sm secondary" onClick={() => ack(a)} style={{ marginRight: 6 }}>Ack</button>}
                  {a.status === "OPEN" && <button className="btn sm" disabled={busyId === a.id} onClick={() => createWo(a)}>+ WO</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
