import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { PM, WorkOrder } from "../lib/types";
import { Badge, PriorityBadge, Spinner, fmtDate } from "../components/ui";

export default function PreventiveMaintenance() {
  const nav = useNavigate();
  const [pms, setPms] = useState<PM[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<number | null>(null);
  const now = new Date();

  const load = () => api.get<PM[]>("/api/pm").then((d) => setPms(d)).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const generate = async (pm: PM) => {
    setBusy(pm.id);
    try {
      const wo = await api.post<WorkOrder>(`/api/pm/${pm.id}/generate`);
      await load();
      if (confirm(`Created ${wo.wo_num}. Open it now?`)) nav(`/workorders/${wo.id}`);
    } finally { setBusy(null); }
  };

  if (loading) return <Spinner />;

  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>PM #</th><th>Description</th><th>Asset</th><th>Frequency</th><th>Last Generated</th><th>Next Due</th><th>Priority</th><th>Status</th><th></th></tr></thead>
        <tbody>
          {pms.map((p) => {
            const overdue = p.next_due && new Date(p.next_due) < now;
            return (
              <tr key={p.id} className="norow">
                <td className="mono">{p.pm_num}</td>
                <td>{p.description}</td>
                <td>{p.asset?.asset_num || "—"}</td>
                <td>{p.frequency_days} days</td>
                <td>{fmtDate(p.last_generated)}</td>
                <td>{fmtDate(p.next_due)} {overdue && <Badge value="Overdue" color="red" />}</td>
                <td><PriorityBadge value={p.priority} /></td>
                <td><Badge value={p.status} /></td>
                <td><button className="btn sm" disabled={busy === p.id} onClick={() => generate(p)}>{busy === p.id ? "…" : "Generate WO"}</button></td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
