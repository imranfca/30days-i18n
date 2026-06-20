import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { ServiceRequest, WorkOrder, Asset } from "../lib/types";
import { Badge, PriorityBadge, Spinner, Modal, fmtDate } from "../components/ui";

export default function ServiceRequests() {
  const nav = useNavigate();
  const [srs, setSrs] = useState<ServiceRequest[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNew, setShowNew] = useState(false);
  const [form, setForm] = useState({ description: "", reported_by: "", asset_id: "", priority: 3 });

  const load = () => api.get<ServiceRequest[]>("/api/servicerequests").then((d) => { setSrs(d); setLoading(false); });
  useEffect(() => { load(); api.get<Asset[]>("/api/assets").then(setAssets); }, []);

  const convert = async (sr: ServiceRequest) => {
    const wo = await api.post<WorkOrder>(`/api/servicerequests/${sr.id}/convert`);
    await load();
    if (confirm(`Created ${wo.wo_num} from this request. Open it?`)) nav(`/workorders/${wo.id}`);
  };

  const create = async () => {
    await api.post("/api/servicerequests", { ...form, asset_id: form.asset_id ? Number(form.asset_id) : null, priority: Number(form.priority) });
    setShowNew(false);
    setForm({ description: "", reported_by: "", asset_id: "", priority: 3 });
    load();
  };

  if (loading) return <Spinner />;

  return (
    <>
      <div className="toolbar"><div className="spacer" /><button className="btn" onClick={() => setShowNew(true)}>+ New Request</button></div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Ticket</th><th>Description</th><th>Asset</th><th>Reported By</th><th>Priority</th><th>Status</th><th>Reported</th><th></th></tr></thead>
          <tbody>
            {srs.map((s) => (
              <tr key={s.id} className="norow">
                <td className="mono">{s.ticket_num}</td>
                <td>{s.description}</td>
                <td>{s.asset?.asset_num || "—"}</td>
                <td>{s.reported_by || "—"}</td>
                <td><PriorityBadge value={s.priority} /></td>
                <td><Badge value={s.status} /></td>
                <td>{fmtDate(s.reported_date)}</td>
                <td>{["NEW", "QUEUED"].includes(s.status) && <button className="btn sm" onClick={() => convert(s)}>→ Work Order</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showNew && (
        <Modal title="New Service Request" onClose={() => setShowNew(false)}
          footer={<><button className="btn secondary" onClick={() => setShowNew(false)}>Cancel</button><button className="btn" disabled={!form.description} onClick={create}>Submit</button></>}>
          <div className="field"><label>Description</label><textarea rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div className="field"><label>Reported By</label><input value={form.reported_by} onChange={(e) => setForm({ ...form, reported_by: e.target.value })} /></div>
          <div className="grid cols-2">
            <div className="field"><label>Asset</label>
              <select value={form.asset_id} onChange={(e) => setForm({ ...form, asset_id: e.target.value })}>
                <option value="">— none —</option>
                {assets.map((a) => <option key={a.id} value={a.id}>{a.asset_num}</option>)}
              </select>
            </div>
            <div className="field"><label>Priority</label>
              <select value={form.priority} onChange={(e) => setForm({ ...form, priority: Number(e.target.value) })}>
                {[1, 2, 3, 4, 5].map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
          </div>
        </Modal>
      )}
    </>
  );
}
