import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import type { WorkOrder, Labor } from "../lib/types";
import { Badge, PriorityBadge, Spinner, fmtMoney, fmtDate } from "../components/ui";

const FLOW: Record<string, string[]> = {
  WAPPR: ["APPR", "CAN"],
  APPR: ["INPRG", "CAN"],
  INPRG: ["COMP", "WAPPR"],
  COMP: ["CLOSE", "INPRG"],
  CLOSE: [],
  CAN: [],
};
const LABELS: Record<string, string> = {
  APPR: "Approve", INPRG: "Start Work", COMP: "Complete", CLOSE: "Close",
  CAN: "Cancel", WAPPR: "Reopen",
};

export default function WorkOrderDetail() {
  const { id } = useParams();
  const [wo, setWo] = useState<WorkOrder | null>(null);
  const [labor, setLabor] = useState<Labor[]>([]);
  const [busy, setBusy] = useState(false);

  const load = () => api.get<WorkOrder>(`/api/workorders/${id}`).then(setWo);
  useEffect(() => { load(); api.get<Labor[]>("/api/labor").then(setLabor); }, [id]);

  if (!wo) return <Spinner />;

  const transition = async (status: string) => {
    setBusy(true);
    try { await api.post(`/api/workorders/${id}/status`, { status }); await load(); }
    catch (e: any) { alert(e.message); }
    finally { setBusy(false); }
  };

  const assign = async (laborId: string) => {
    await api.patch(`/api/workorders/${id}`, { assigned_to_id: laborId ? Number(laborId) : null });
    await load();
  };

  const next = FLOW[wo.status] || [];

  return (
    <>
      <div className="crumb"><Link to="/workorders">Work Orders</Link> / {wo.wo_num}</div>
      <div className="card">
        <div className="card-title-row">
          <h3 style={{ fontSize: 20 }}>{wo.wo_num} — {wo.description}</h3>
          <div className="spacer" />
          <Badge value={wo.status} />
        </div>
        <div style={{ display: "flex", gap: 10, marginBottom: 18, flexWrap: "wrap" }}>
          {next.map((s) => (
            <button key={s} className={"btn " + (s === "CAN" ? "danger" : s === "COMP" || s === "APPR" ? "" : "secondary")} disabled={busy} onClick={() => transition(s)}>
              {LABELS[s] || s}
            </button>
          ))}
          {next.length === 0 && <span className="muted">No further actions — work order is {wo.status}.</span>}
        </div>
        <div className="grid cols-2">
          <dl className="kv">
            <dt>Asset</dt><dd>{wo.asset ? <Link to={`/assets/${wo.asset.id}`}>{wo.asset.asset_num} — {wo.asset.description}</Link> : "—"}</dd>
            <dt>Location</dt><dd>{wo.location?.name || "—"}</dd>
            <dt>Work Type</dt><dd><Badge value={wo.work_type} color="gray" /></dd>
            <dt>Priority</dt><dd><PriorityBadge value={wo.priority} /></dd>
            <dt>Assigned To</dt>
            <dd>
              <select style={{ maxWidth: 240 }} value={wo.assigned_to?.id || ""} onChange={(e) => assign(e.target.value)}>
                <option value="">— unassigned —</option>
                {labor.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
              </select>
            </dd>
          </dl>
          <dl className="kv">
            <dt>Reported</dt><dd>{fmtDate(wo.reported_date)}</dd>
            <dt>Scheduled Start</dt><dd>{fmtDate(wo.scheduled_start)}</dd>
            <dt>Scheduled Finish</dt><dd>{fmtDate(wo.scheduled_finish)}</dd>
            <dt>Estimated</dt><dd>{wo.estimated_hours}h · {fmtMoney(wo.estimated_cost)}</dd>
            <dt>Actual</dt><dd>{wo.actual_hours || 0}h · {fmtMoney(wo.actual_cost)}</dd>
          </dl>
        </div>
      </div>

      {wo.job_plan && (
        <>
          <div className="section-title">Job Plan · {wo.job_plan.jp_num}</div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>Seq</th><th>Task</th><th className="right">Est. Hours</th></tr></thead>
              <tbody>
                {wo.job_plan.tasks.map((t) => (
                  <tr key={t.id} className="norow"><td>{t.sequence}</td><td>{t.description}</td><td className="right">{t.estimated_hours}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </>
  );
}
