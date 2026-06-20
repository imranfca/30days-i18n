import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { Asset, Location } from "../lib/types";
import { Badge, HealthPill, Spinner, Empty, Modal, fmtMoney } from "../components/ui";

export default function Assets() {
  const nav = useNavigate();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [form, setForm] = useState({ asset_num: "", description: "", manufacturer: "", model: "", location_id: "", criticality: 3, purchase_cost: 0 });

  const load = () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (status) params.set("status", status);
    api.get<Asset[]>(`/api/assets?${params}`).then((d) => { setAssets(d); setLoading(false); });
  };

  useEffect(() => { api.get<Location[]>("/api/locations").then(setLocations); }, []);
  useEffect(() => { const t = setTimeout(load, 200); return () => clearTimeout(t); }, [search, status]);

  const create = async () => {
    await api.post("/api/assets", {
      ...form,
      location_id: form.location_id ? Number(form.location_id) : null,
      criticality: Number(form.criticality),
      purchase_cost: Number(form.purchase_cost),
      health_score: 90,
    });
    setShowNew(false);
    setForm({ asset_num: "", description: "", manufacturer: "", model: "", location_id: "", criticality: 3, purchase_cost: 0 });
    load();
  };

  return (
    <>
      <div className="toolbar">
        <input placeholder="Search assets…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          <option value="OPERATING">Operating</option>
          <option value="DOWN">Down</option>
          <option value="DECOMMISSIONED">Decommissioned</option>
        </select>
        <div className="spacer" />
        <button className="btn" onClick={() => setShowNew(true)}>+ New Asset</button>
      </div>

      {loading ? <Spinner /> : assets.length === 0 ? <Empty text="No assets match your filters." /> : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Asset #</th><th>Description</th><th>Location</th><th>Manufacturer</th><th>Status</th><th>Crit.</th><th>Health</th><th className="right">Cost</th></tr></thead>
            <tbody>
              {assets.map((a) => (
                <tr key={a.id} onClick={() => nav(`/assets/${a.id}`)}>
                  <td className="mono">{a.asset_num}</td>
                  <td>{a.description}</td>
                  <td>{a.location?.name || "—"}</td>
                  <td>{a.manufacturer} {a.model}</td>
                  <td><Badge value={a.status} /></td>
                  <td>{a.criticality}</td>
                  <td><HealthPill score={a.health_score} /></td>
                  <td className="right">{fmtMoney(a.purchase_cost)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showNew && (
        <Modal title="New Asset" onClose={() => setShowNew(false)}
          footer={<><button className="btn secondary" onClick={() => setShowNew(false)}>Cancel</button><button className="btn" disabled={!form.asset_num || !form.description} onClick={create}>Create Asset</button></>}>
          <div className="field"><label>Asset Number</label><input value={form.asset_num} onChange={(e) => setForm({ ...form, asset_num: e.target.value })} placeholder="e.g. PUMP-099" /></div>
          <div className="field"><label>Description</label><input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></div>
          <div className="grid cols-2">
            <div className="field"><label>Manufacturer</label><input value={form.manufacturer} onChange={(e) => setForm({ ...form, manufacturer: e.target.value })} /></div>
            <div className="field"><label>Model</label><input value={form.model} onChange={(e) => setForm({ ...form, model: e.target.value })} /></div>
          </div>
          <div className="field"><label>Location</label>
            <select value={form.location_id} onChange={(e) => setForm({ ...form, location_id: e.target.value })}>
              <option value="">— none —</option>
              {locations.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
            </select>
          </div>
          <div className="grid cols-2">
            <div className="field"><label>Criticality (1–5)</label><input type="number" min={1} max={5} value={form.criticality} onChange={(e) => setForm({ ...form, criticality: Number(e.target.value) })} /></div>
            <div className="field"><label>Purchase Cost</label><input type="number" value={form.purchase_cost} onChange={(e) => setForm({ ...form, purchase_cost: Number(e.target.value) })} /></div>
          </div>
        </Modal>
      )}
    </>
  );
}
