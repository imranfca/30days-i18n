import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { VisualInspection } from "../lib/types";
import { Spinner, Badge, Kpi, fmtDate } from "../components/ui";

export default function Visual() {
  const nav = useNavigate();
  const [rows, setRows] = useState<VisualInspection[]>([]);
  const [defectsOnly, setDefectsOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.get<VisualInspection[]>(`/api/ai/visual/inspections?defects_only=${defectsOnly}`)
      .then(setRows)
      .catch((e: any) => setError(e?.message ?? "Failed to load inspections"))
      .finally(() => setLoading(false));
  }, [defectsOnly]);
  if (loading) return <Spinner />;
  if (error) return <div className="empty">Error: {error}</div>;

  const defects = rows.filter((r) => r.defect_detected).length;

  return (
    <>
      <p className="muted" style={{ marginTop: 0 }}>Maximo Visual Inspection uses computer-vision models to analyze inspection imagery and automatically flag defects like corrosion, cracks, and leaks.</p>
      <div className="grid cols-3">
        <Kpi label="Inspections" value={rows.length} />
        <Kpi label="Defects Detected" value={defects} tone={defects > 0 ? "warn" : "good"} />
        <Kpi label="Detection Rate" value={`${rows.length ? Math.round((defects / rows.length) * 100) : 0}%`} />
      </div>
      <div className="toolbar" style={{ marginTop: 16 }}>
        <label style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 14 }}>
          <input type="checkbox" style={{ width: "auto" }} checked={defectsOnly} onChange={(e) => setDefectsOnly(e.target.checked)} />
          Show defects only
        </label>
      </div>
      <div className="grid cols-3">
        {rows.map((r) => (
          <div className="card" key={r.id} style={{ cursor: "pointer" }} onClick={() => nav(`/assets/${r.asset_id}`)}>
            <div style={{ height: 120, borderRadius: 6, background: r.defect_detected ? "linear-gradient(135deg,#fff1f1,#ffd7d9)" : "linear-gradient(135deg,#defbe6,#a7f0ba)", display: "grid", placeItems: "center", marginBottom: 12, fontSize: 38 }}>
              {r.defect_detected ? "⚠" : "✓"}
            </div>
            <div className="card-title-row"><h3 style={{ fontSize: 14 }}>{r.asset?.asset_num}</h3><div className="spacer" /><span className="muted" style={{ fontSize: 12 }}>{fmtDate(r.inspection_date)}</span></div>
            <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>{r.image_label}</div>
            {r.defect_detected
              ? <div><Badge value={r.defect_type} color="red" /> <span className="muted" style={{ fontSize: 12 }}>{Math.round(r.confidence * 100)}% confidence</span></div>
              : <div><Badge value="No defect" color="green" /> <span className="muted" style={{ fontSize: 12 }}>{Math.round(r.confidence * 100)}% confidence</span></div>}
          </div>
        ))}
      </div>
    </>
  );
}
