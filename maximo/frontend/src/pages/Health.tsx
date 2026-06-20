import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { Badge, HealthPill, Spinner, Kpi } from "../components/ui";

interface HealthRow {
  asset_id: number; asset_num: string; description: string;
  health_score: number; criticality: number; status: string; risk: string;
}
interface HealthResp { assets: HealthRow[]; summary: { high_risk: number; medium_risk: number; low_risk: number }; }

export default function Health() {
  const nav = useNavigate();
  const [data, setData] = useState<HealthResp | null>(null);
  useEffect(() => { api.get<HealthResp>("/api/ai/health").then(setData); }, []);
  if (!data) return <Spinner />;

  return (
    <>
      <p className="muted" style={{ marginTop: 0 }}>Maximo Health scores every asset on condition and criticality to rank reliability risk and prioritize intervention.</p>
      <div className="grid cols-3">
        <Kpi label="High Risk Assets" value={data.summary.high_risk} tone="danger" />
        <Kpi label="Medium Risk" value={data.summary.medium_risk} tone="warn" />
        <Kpi label="Low Risk" value={data.summary.low_risk} tone="good" />
      </div>
      <div className="table-wrap" style={{ marginTop: 16 }}>
        <table>
          <thead><tr><th>Asset #</th><th>Description</th><th>Status</th><th>Criticality</th><th>Health Score</th><th>Reliability Risk</th></tr></thead>
          <tbody>
            {data.assets.map((a) => (
              <tr key={a.asset_id} onClick={() => nav(`/assets/${a.asset_id}`)}>
                <td className="mono">{a.asset_num}</td>
                <td>{a.description}</td>
                <td><Badge value={a.status} /></td>
                <td>{a.criticality}</td>
                <td><HealthPill score={a.health_score} /></td>
                <td><Badge value={a.risk} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
