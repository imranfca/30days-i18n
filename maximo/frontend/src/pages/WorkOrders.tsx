import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { WorkOrder, Asset, Labor, JobPlan } from "../lib/types";
import { Badge, PriorityBadge, Spinner, Empty, Modal, fmtMoney, fmtDate } from "../components/ui";

export default function WorkOrders() {
  const nav = useNavigate();
  const [wos, setWos] = useState<WorkOrder[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [labor, setLabor] = useState<Labor[]>([]);
  const [jobPlans, setJobPlans] = useState<JobPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");
  const [type, setType] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [form, setForm] = useState({ description: "", asset_id: "", assigned_to_id: "", priority: 3, work_type: "CM", estimated_hours: 4 });

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (status) params.set("status", status);
    if (type) params.set("work_type", type);
    api.get<WorkOrder[]>(`/api/workorders?${params}`).then((d) => { setWos(d); setLoading(false); });
  };

  useEffect(() => {
    api.get<Asset[]>("/api/assets").then(setAssets);
    api.get<Labor[]>("/api/labor").then(setLabor);
    api.get<JobPlan[]>("/api/jobplans").then(setJobPlans);
  }, []);
  useEffect(load, [status, type]);

  const create = async () => {
    await api.post("/api/workorders", {
      description: form.description,
      asset_id: form.asset_id ? Number(form.asset_id) : null,
      assigned_to_id: form.assigned_to_id ? Number(form.assigned_to_id) : null,
      priority: Number(form.priority),
      work_type: form.work_type,
      estimated_hours: Number(form.estimated_hours),
      estimated_cost: Number(form.estimated_hours) * 48,
    });
    setShowNew(false);
    setForm({ description: "", asset_id: "", assigned_to_id: "", priority: 3, work_type: "CM", estimated_hours: 4 });
    load();
  };

  return (
    <>
      <div className="toolbar">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          {["WAPPR", "APPR", "INPRG", "COMP", "CLOSE", "CAN"].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={type} onChange={(e) => setType(e.target.value)}>
          <option value="">All types</option>
          {["CM", "PM", "EM", "INSP"].map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <div className="spacer" />
        <button className="btn" onClick={() => setShowNew(true)}>+ New Work Order</button>
      </div>

      {loading ? <Spinner /> : wos.length === 0 ? <Empty text="No work orders match." /> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>WO</th><th>Description</th><th>Asset</th><th>Type</th><th>Priority</th><th>Status</th><th>Assigned</th><th>Scheduled</th><th className="right">Cost</th></tr></thead>
            <tbody>
              {wos.map((w) => (
                <tr key={w.id} onClick={() => nav(`/workorders/${w.id}`)}>
                  <td className="mono">{w.wo_num}</td>
                  <td>{w.description}</td>
                  <td>{w.asset?.asset_num || "—"}</td>
                  <td><Badge value={w.work_type} color="gray" /></td>
                  <td><PriorityBadge value={w.priority} /></td>
                  <td><Badge value={w.status} /></td>
                  <td>{w.assigned_to?.name || "—"}</td>
                  <td>{fmtDate(w.scheduled_start)}</td>
                  <td className="right">{fmtMoney(w.actual_cost || w.estimated_cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showNew && (
        <Modal title="New Work Order" onClose={() => setShowNew(false)}
          footer={<><button className="btn secondary" onClick={() => setShowNew(false)}>Cancel</button><button className="btn" disabled={!form.description} onClick={create}>Create</button></>}>
          <div className="field"><label>Description</label><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div className="field"><label>Asset</label>
            <select value={form.asset_id} onChange={(e) => setForm({ ...form, asset_id: e.target.value })}>
              <option value="">— none —</option>
              {assets.map((a) => <option key={a.id} value={a.id}>{a.asset_num} — {a.description}</option>)}
            </select>
          </div>
          <div className="grid cols-2">
            <div className="field"><label>Work Type</label>
              <select value={form.work_type} onChange={(e) => setForm({ ...form, work_type: e.target.value })}>
                <option value="CM">Corrective (CM)</option><option value="PM">Preventive (PM)</option>
                <option value="EM">Emergency (EM)</option><option value="INSP">Inspection (INSP)</option>
              </select>
            </div>
            <div className="field"><label>Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: Number(e.target.value) })}>
                {[1, 2, 3, 4, 5].map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>
          <div className="grid cols-2">
            <div className="field"><label>Assign To</label>
              <select value={form.assigned_to_id} onChange={(e) => setForm({ ...form, assigned_to_id: e.target.value })}>
                <option value="">— unassigned —</option>
                {labor.map((l) => <option key={l.id} value={l.id}>{l.name} ({l.craft?.name})</option>)}
              </select>
            </div>
            <div className="field"><label>Estimated Hours</label><input type="number" value={form.estimated_hours} onChange={(e) => setForm({ ...form, estimated_hours: Number(e.target.value) })} /></div>
          </div>
        </Modal>
      )}
    </>
  );
}
