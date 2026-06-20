import React from "react";

/* ----------------------------- Status colors ----------------------------- */
const STATUS_COLOR: Record<string, string> = {
  // work order / general
  WAPPR: "gray", APPR: "blue", INPRG: "purple", COMP: "green", CLOSE: "gray", CAN: "red",
  // assets
  OPERATING: "green", DOWN: "red", DECOMMISSIONED: "gray",
  // service requests
  NEW: "blue", QUEUED: "yellow", INPROG: "purple", RESOLVED: "green", CLOSED: "gray",
  // PM / labor
  ACTIVE: "green", INACTIVE: "gray",
  // PO
  RECEIVED: "green",
  // alerts
  OPEN: "red", ACKNOWLEDGED: "yellow",
  // severity
  CRITICAL: "red", HIGH: "orange", MEDIUM: "yellow", LOW: "blue",
  // risk
  High: "red", Medium: "yellow", Low: "green",
};

export function Badge({ value, color }: { value: string; color?: string }) {
  const c = color || STATUS_COLOR[value] || "gray";
  return (
    <span className={`badge ${c}`}>
      <span className="dot" />
      {value}
    </span>
  );
}

export function PriorityBadge({ value }: { value: number }) {
  const map: Record<number, string> = { 1: "red", 2: "orange", 3: "yellow", 4: "blue", 5: "gray" };
  const label: Record<number, string> = { 1: "1 - Urgent", 2: "2 - High", 3: "3 - Medium", 4: "4 - Low", 5: "5 - Planning" };
  return <span className={`badge ${map[value] || "gray"}`}>{label[value] || value}</span>;
}

/* ------------------------------- KPI card -------------------------------- */
export function Kpi({
  label, value, sub, tone,
}: { label: string; value: React.ReactNode; sub?: string; tone?: "warn" | "danger" | "good" }) {
  return (
    <div className={`kpi ${tone || ""}`}>
      <span className="accent" />
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {sub && <div className="delta">{sub}</div>}
    </div>
  );
}

/* ------------------------------- Health bar ------------------------------ */
export function HealthPill({ score }: { score: number }) {
  const color = score >= 80 ? "var(--green)" : score >= 60 ? "var(--yellow)" : "var(--red)";
  return (
    <span className="health-pill">
      <span className="bar">
        <span style={{ width: `${score}%`, background: color }} />
      </span>
      <span style={{ fontWeight: 600 }}>{score}</span>
    </span>
  );
}

/* -------------------------------- Spinner -------------------------------- */
export function Spinner() {
  return <div className="spinner">Loading…</div>;
}

export function Empty({ text }: { text: string }) {
  return <div className="empty">{text}</div>;
}

/* --------------------------------- Modal --------------------------------- */
export function Modal({
  title, onClose, children, footer,
}: { title: string; onClose: () => void; children: React.ReactNode; footer?: React.ReactNode }) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h2>{title}</h2>
          <button className="close-x" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">{children}</div>
        {footer && <div className="modal-foot">{footer}</div>}
      </div>
    </div>
  );
}

/* ------------------------------ Formatters ------------------------------- */
export const fmtMoney = (n: number) =>
  "$" + (n || 0).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });

export const fmtDate = (s?: string | null) =>
  s ? new Date(s).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) : "—";

/* --------------------------- Simple donut chart -------------------------- */
export function Donut({ data }: { data: { label: string; value: number; color: string }[] }) {
  const total = data.reduce((s, d) => s + d.value, 0) || 1;
  let acc = 0;
  const r = 52, cx = 60, cy = 60, sw = 16;
  const circ = 2 * Math.PI * r;
  return (
    <div className="donut">
      <svg width="120" height="120" viewBox="0 0 120 120">
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="var(--gray-20)" strokeWidth={sw} />
        {data.map((d, i) => {
          const frac = d.value / total;
          const dash = frac * circ;
          const el = (
            <circle
              key={i}
              cx={cx} cy={cy} r={r} fill="none" stroke={d.color} strokeWidth={sw}
              strokeDasharray={`${dash} ${circ - dash}`}
              strokeDashoffset={-acc * circ}
              transform={`rotate(-90 ${cx} ${cy})`}
            />
          );
          acc += frac;
          return el;
        })}
        <text x={cx} y={cy + 5} textAnchor="middle" fontSize="22" fontWeight="700">
          {total}
        </text>
      </svg>
      <div className="legend">
        {data.map((d, i) => (
          <div className="row" key={i}>
            <span className="sw" style={{ background: d.color }} />
            {d.label} <strong style={{ marginLeft: "auto" }}>{d.value}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ----------------------------- Bar breakdown ----------------------------- */
export function BarBreakdown({
  data, colorFor,
}: { data: { label: string; value: number }[]; colorFor?: (k: string) => string }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div className="stat-bars">
      {data.map((d) => (
        <div className="row" key={d.label}>
          <span className="lbl">{d.label}</span>
          <div className="bar" style={{ flex: 1 }}>
            <span style={{ width: `${(d.value / max) * 100}%`, background: colorFor ? colorFor(d.label) : "var(--blue-60)" }} />
          </div>
          <span className="num">{d.value}</span>
        </div>
      ))}
    </div>
  );
}
