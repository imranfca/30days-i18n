import React, { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { api } from "../lib/api";
import type { DashboardData } from "../lib/types";

interface NavItem {
  to: string;
  label: string;
  icon: string;
  badgeKey?: keyof DashboardData;
}

const SECTIONS: { title: string; items: NavItem[] }[] = [
  {
    title: "Monitor",
    items: [{ to: "/", label: "Dashboard", icon: "▤" }],
  },
  {
    title: "Maximo Manage",
    items: [
      { to: "/assets", label: "Assets", icon: "⚙" },
      { to: "/workorders", label: "Work Orders", icon: "🛠", badgeKey: "backlog_count" },
      { to: "/pm", label: "Preventive Maint.", icon: "⟳", badgeKey: "overdue_pm_count" },
      { to: "/servicerequests", label: "Service Requests", icon: "✉" },
      { to: "/inventory", label: "Inventory", icon: "📦", badgeKey: "below_reorder_count" },
      { to: "/purchasing", label: "Purchasing", icon: "🛒" },
    ],
  },
  {
    title: "AI Applications",
    items: [
      { to: "/ai/health", label: "Health", icon: "❤" },
      { to: "/ai/monitor", label: "Monitor", icon: "📡", badgeKey: "open_alert_count" },
      { to: "/ai/predict", label: "Predict", icon: "📈" },
      { to: "/ai/visual", label: "Visual Inspection", icon: "👁" },
      { to: "/ai/assist", label: "Assist", icon: "💬" },
    ],
  },
];

const TITLES: Record<string, { title: string; sub: string }> = {
  "/": { title: "Operations Dashboard", sub: "Enterprise asset & maintenance overview" },
  "/assets": { title: "Assets", sub: "Equipment register and asset hierarchy" },
  "/workorders": { title: "Work Orders", sub: "Plan, assign and track maintenance work" },
  "/pm": { title: "Preventive Maintenance", sub: "Scheduled maintenance plans" },
  "/servicerequests": { title: "Service Requests", sub: "Incoming requests and tickets" },
  "/inventory": { title: "Inventory", sub: "Spare parts and storeroom stock" },
  "/purchasing": { title: "Purchasing", sub: "Vendors and purchase orders" },
  "/ai/health": { title: "Maximo Health", sub: "Asset condition and risk ranking" },
  "/ai/monitor": { title: "Maximo Monitor", sub: "AI anomaly & threshold detection" },
  "/ai/predict": { title: "Maximo Predict", sub: "Predictive failure & remaining useful life" },
  "/ai/visual": { title: "Maximo Visual Inspection", sub: "Computer-vision defect detection" },
  "/ai/assist": { title: "Maximo Assist", sub: "AI maintenance knowledge assistant" },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  const loc = useLocation();
  const [kpis, setKpis] = useState<DashboardData | null>(null);

  useEffect(() => {
    api.get<DashboardData>("/api/dashboard").then(setKpis).catch(() => {});
  }, [loc.pathname]);

  const base = "/" + (loc.pathname.split("/")[1] || "");
  const meta = TITLES[loc.pathname] || TITLES[base] || { title: "MaxiManage", sub: "" };

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">M</div>
          <div className="name">
            MaxiManage
            <small>Asset Management Suite</small>
          </div>
        </div>
        {SECTIONS.map((sec) => (
          <div key={sec.title}>
            <div className="nav-section">{sec.title}</div>
            {sec.items.map((it) => {
              const badge = it.badgeKey && kpis ? (kpis[it.badgeKey] as number) : 0;
              return (
                <NavLink
                  key={it.to}
                  to={it.to}
                  end={it.to === "/"}
                  className={({ isActive }) => "nav-link" + (isActive ? " active" : "")}
                >
                  <span className="ico">{it.icon}</span>
                  {it.label}
                  {badge > 0 && <span className="nav-badge">{badge}</span>}
                </NavLink>
              );
            })}
          </div>
        ))}
        <div style={{ marginTop: "auto", padding: "16px 20px", fontSize: 11, color: "var(--gray-60)" }}>
          v1.0.0 · Demo environment
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <div>
            <h1>{meta.title}</h1>
            <div className="sub">{meta.sub}</div>
          </div>
          <div className="spacer" />
          <div style={{ textAlign: "right" }}>
            <div style={{ fontWeight: 600 }}>Site: HQ</div>
            <div className="sub">Maintenance Planner</div>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  );
}
