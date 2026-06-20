import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { PurchaseOrder, Vendor } from "../lib/types";
import { Badge, Spinner, Modal, fmtMoney, fmtDate } from "../components/ui";

const PO_NEXT: Record<string, string> = { WAPPR: "APPR", APPR: "INPRG", INPRG: "RECEIVED", RECEIVED: "CLOSE" };
const PO_LABEL: Record<string, string> = { APPR: "Approve", INPRG: "Issue to Vendor", RECEIVED: "Receive", CLOSE: "Close" };

export default function Purchasing() {
  const [pos, setPos] = useState<PurchaseOrder[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<PurchaseOrder | null>(null);
  const [tab, setTab] = useState<"orders" | "vendors">("orders");

  const load = () => api.get<PurchaseOrder[]>("/api/purchaseorders").then((d) => { setPos(d); setLoading(false); });
  useEffect(() => { load(); api.get<Vendor[]>("/api/vendors").then(setVendors); }, []);

  const advance = async (po: PurchaseOrder) => {
    const next = PO_NEXT[po.status];
    if (!next) return;
    await api.post(`/api/purchaseorders/${po.id}/status`, { status: next });
    load();
    if (open) setOpen({ ...open, status: next });
  };

  if (loading) return <Spinner />;

  return (
    <>
      <div className="toolbar">
        <button className={"btn " + (tab === "orders" ? "" : "secondary")} onClick={() => setTab("orders")}>Purchase Orders</button>
        <button className={"btn " + (tab === "vendors" ? "" : "secondary")} onClick={() => setTab("vendors")}>Vendors</button>
      </div>

      {tab === "orders" ? (
        <div className="table-wrap">
          <table>
            <thead><tr><th>PO #</th><th>Vendor</th><th>Description</th><th>Order Date</th><th>Required</th><th>Status</th><th className="right">Total</th><th></th></tr></thead>
            <tbody>
              {pos.map((p) => (
                <tr key={p.id} onClick={() => setOpen(p)}>
                  <td className="mono">{p.po_num}</td>
                  <td>{p.vendor?.name || "—"}</td>
                  <td>{p.description}</td>
                  <td>{fmtDate(p.order_date)}</td>
                  <td>{fmtDate(p.required_date)}</td>
                  <td><Badge value={p.status} /></td>
                  <td className="right">{fmtMoney(p.total_cost)}</td>
                  <td onClick={(e) => e.stopPropagation()}>
                    {PO_NEXT[p.status] && <button className="btn sm" onClick={() => advance(p)}>{PO_LABEL[PO_NEXT[p.status]]}</button>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead><tr><th>Code</th><th>Vendor</th><th>Contact</th><th>Email</th><th>Phone</th><th>Rating</th></tr></thead>
            <tbody>
              {vendors.map((v) => (
                <tr key={v.id} className="norow">
                  <td className="mono">{v.code}</td>
                  <td>{v.name}</td>
                  <td>{v.contact}</td>
                  <td>{v.email}</td>
                  <td>{v.phone}</td>
                  <td>{"★".repeat(Math.round(v.rating))}<span className="muted">{"★".repeat(5 - Math.round(v.rating))}</span> {v.rating}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {open && (
        <Modal title={`${open.po_num} · ${open.vendor?.name || ""}`} onClose={() => setOpen(null)}
          footer={PO_NEXT[open.status] ? <button className="btn" onClick={() => advance(open)}>{PO_LABEL[PO_NEXT[open.status]]}</button> : <span className="muted">No further actions</span>}>
          <div style={{ marginBottom: 14 }}><Badge value={open.status} /> · Total {fmtMoney(open.total_cost)}</div>
          <table>
            <thead><tr><th>Item</th><th className="right">Qty</th><th className="right">Unit</th><th className="right">Line</th></tr></thead>
            <tbody>
              {open.lines.map((l) => (
                <tr key={l.id} className="norow"><td>{l.description}</td><td className="right">{l.quantity}</td><td className="right">{fmtMoney(l.unit_cost)}</td><td className="right">{fmtMoney(l.line_cost)}</td></tr>
              ))}
            </tbody>
          </table>
          {open.status === "RECEIVED" && <p className="muted" style={{ marginTop: 12 }}>✓ Received items have been added to inventory balances.</p>}
        </Modal>
      )}
    </>
  );
}
