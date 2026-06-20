import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import type { PredictForecast } from "../lib/types";
import { Spinner, Badge, fmtDate } from "../components/ui";

function ProbBar({ p }: { p: number }) {
  const pct = Math.round(p * 100);
  const color = p > 0.7 ? "var(--red)" : p > 0.4 ? "var(--orange)" : "var(--yellow)";
  return (
    <span className="health-pill">
      <span className="bar" style={{ width: 90 }}><span style={{ width: `${pct}%`, background: color }} /></span>
      <strong>{pct}%</strong>
    </span>
  );
}

export default function Predict() {
  const nav = useNavigate();
  const [rows, setRows] = useState<PredictForecast[]>([]);
  useEffect(() => { api.get<PredictForecast[]>("/api/ai/predict/forecasts").then(setRows); }, []);
  if (!rows.length) return <Spinner />;

  return (
    <>
      <p className="muted" style={{ marginTop: 0 }}>Maximo Predict applies machine-learning models to operational data to estimate failure probability and remaining useful life (RUL), enabling condition-based maintenance.</p>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Asset</th><th>Failure Probability</th><th>Remaining Useful Life</th><th>Predicted Failure</th><th>Confidence</th><th>Model</th><th>Recommended Action</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} onClick={() => nav(`/assets/${r.asset_id}`)}>
                <td className="mono">{r.asset?.asset_num}<div className="muted" style={{ fontWeight: 400 }}>{r.asset?.description}</div></td>
                <td><ProbBar p={r.failure_probability} /></td>
                <td>{r.remaining_useful_life_days} days</td>
                <td>{fmtDate(r.predicted_failure_date)}</td>
                <td>{Math.round(r.confidence * 100)}%</td>
                <td><span className="muted" style={{ fontSize: 12 }}>{r.model_name}</span></td>
                <td>{r.failure_probability > 0.7 ? <Badge value="Act now" color="red" /> : r.failure_probability > 0.4 ? <Badge value="Plan" color="orange" /> : <Badge value="Monitor" color="yellow" />} {r.recommended_action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
