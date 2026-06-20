import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "../lib/api";
import type { Asset, WorkOrder, MeterReading, Meter } from "../lib/types";
import { Badge, HealthPill, PriorityBadge, Spinner, fmtMoney, fmtDate } from "../components/ui";

function MeterChart({ meter }: { meter: Meter }) {
  const [readings, setReadings] = useState<MeterReading[]>([]);
  useEffect(() => { api.get<MeterReading[]>(`/api/meters/${meter.id}/readings`).then(setReadings); }, [meter.id]);
  const vals = readings.map((r) => r.reading);
  const max = Math.max(...vals, meter.action_limit || 0, 1);
  return (
    <div className="card">
      <div className="card-title-row">
        <h3>{meter.name} <span className="muted" style={{ fontWeight: 400 }}>({meter.unit})</span></h3>
        <div className="spacer" />
        <strong>{meter.last_reading} {meter.unit}</strong>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 90 }}>
        {readings.map((r) => {
          const over = meter.action_limit && r.reading >= meter.action_limit;
          const warn = meter.warning_limit && r.reading >= meter.warning_limit;
          return <div key={r.id} title={`${r.reading} on ${fmtDate(r.reading_date)}`} style={{ flex: 1, height: `${(r.reading / max) * 100}%`, background: over ? "var(--red)" : warn ? "var(--yellow)" : "var(--blue-40)", borderRadius: "2px 2px 0 0" }} />;
        })}
      </div>
      {meter.warning_limit && <div className="muted" style={{ fontSize: 12, marginTop: 8 }}>Warning ≥ {meter.warning_limit} · Action ≥ {meter.action_limit}</div>}
    </div>
  );
}

export default function AssetDetail() {
  const { id } = useParams();
  const nav = useNavigate();
  const [asset, setAsset] = useState<Asset | null>(null);
  const [wos, setWos] = useState<WorkOrder[]>([]);

  useEffect(() => {
    api.get<Asset>(`/api/assets/${id}`).then(setAsset);
    api.get<WorkOrder[]>(`/api/assets/${id}/workorders`).then(setWos);
  }, [id]);

  if (!asset) return <Spinner />;

  return (
    <>
      <div className="crumb"><Link to="/assets">Assets</Link> / {asset.asset_num}</div>
      <div className="card">
        <div className="card-title-row">
          <h3 style={{ fontSize: 20 }}>{asset.asset_num} — {asset.description}</h3>
          <div className="spacer" />
          <Badge value={asset.status} />
        </div>
        <div className="grid cols-2">
          <dl className="kv">
            <dt>Location</dt><dd>{asset.location?.name || "—"}</dd>
            <dt>Manufacturer</dt><dd>{asset.manufacturer || "—"}</dd>
            <dt>Model</dt><dd>{asset.model || "—"}</dd>
            <dt>Serial Number</dt><dd>{asset.serial_num || "—"}</dd>
            <dt>Asset Type</dt><dd>{asset.asset_type}</dd>
          </dl>
          <dl className="kv">
            <dt>Health Score</dt><dd><HealthPill score={asset.health_score} /></dd>
            <dt>Criticality</dt><dd>{asset.criticality} of 5</dd>
            <dt>Install Date</dt><dd>{fmtDate(asset.install_date)}</dd>
            <dt>Purchase Cost</dt><dd>{fmtMoney(asset.purchase_cost)}</dd>
            <dt>Replacement Cost</dt><dd>{fmtMoney(asset.replacement_cost)}</dd>
          </dl>
        </div>
      </div>

      {asset.meters && asset.meters.length > 0 && (
        <>
          <div className="section-title">Condition Monitoring · Meters</div>
          <div className="grid cols-2">{asset.meters.map((m) => <MeterChart key={m.id} meter={m} />)}</div>
        </>
      )}

      <div className="section-title">Work Order History</div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>WO</th><th>Description</th><th>Type</th><th>Priority</th><th>Status</th><th>Reported</th><th className="right">Cost</th></tr></thead>
          <tbody>
            {wos.map((w) => (
              <tr key={w.id} onClick={() => nav(`/workorders/${w.id}`)}>
                <td className="mono">{w.wo_num}</td>
                <td>{w.description}</td>
                <td><Badge value={w.work_type} color="gray" /></td>
                <td><PriorityBadge value={w.priority} /></td>
                <td><Badge value={w.status} /></td>
                <td>{fmtDate(w.reported_date)}</td>
                <td className="right">{fmtMoney(w.actual_cost || w.estimated_cost)}</td>
              </tr>
            ))}
            {wos.length === 0 && <tr className="norow"><td colSpan={7} className="muted">No work orders for this asset.</td></tr>}
          </tbody>
        </table>
      </div>
    </>
  );
}
