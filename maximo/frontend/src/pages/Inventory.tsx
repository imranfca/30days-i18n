import { useEffect, useState } from "react";
import { api } from "../lib/api";
import type { Inventory } from "../lib/types";
import { Badge, Spinner, fmtMoney } from "../components/ui";

export default function InventoryPage() {
  const [rows, setRows] = useState<Inventory[]>([]);
  const [loading, setLoading] = useState(true);
  const [belowOnly, setBelowOnly] = useState(false);

  const load = () => {
    setLoading(true);
    api.get<Inventory[]>(`/api/inventory?below_reorder=${belowOnly}`).then((d) => { setRows(d); setLoading(false); });
  };
  useEffect(load, [belowOnly]);

  const adjust = async (inv: Inventory, delta: number) => {
    try { await api.post(`/api/inventory/${inv.id}/adjust`, { delta }); load(); }
    catch (e: any) { alert(e.message); }
  };

  const totalValue = rows.reduce((s, r) => s + r.current_balance * r.unit_cost, 0);

  if (loading) return <Spinner />;

  return (
    <>
      <div className="toolbar">
        <label style={{ display: "flex", gap: 8, alignItems: "center", fontSize: 14 }}>
          <input type="checkbox" style={{ width: "auto" }} checked={belowOnly} onChange={(e) => setBelowOnly(e.target.checked)} />
          Below reorder point only
        </label>
        <div className="spacer" />
        <span className="muted">Total stock value: <strong>{fmtMoney(totalValue)}</strong></span>
      </div>
      <div className="table-wrap">
        <table>
          <thead><tr><th>Item #</th><th>Description</th><th>Category</th><th>Storeroom</th><th>Bin</th><th className="right">Balance</th><th className="right">Reorder Pt</th><th className="right">Unit Cost</th><th>Stock</th><th>Issue / Receive</th></tr></thead>
          <tbody>
            {rows.map((r) => {
              const low = r.current_balance <= r.reorder_point;
              return (
                <tr key={r.id} className="norow">
                  <td className="mono">{r.item?.item_num}</td>
                  <td>{r.item?.description}</td>
                  <td>{r.item?.category}</td>
                  <td>{r.storeroom?.name}</td>
                  <td>{r.bin}</td>
                  <td className="right"><strong>{r.current_balance}</strong></td>
                  <td className="right">{r.reorder_point}</td>
                  <td className="right">{fmtMoney(r.unit_cost)}</td>
                  <td>{low ? <Badge value="Reorder" color="red" /> : <Badge value="OK" color="green" />}</td>
                  <td>
                    <button className="btn sm secondary" onClick={() => adjust(r, -1)} style={{ marginRight: 6 }}>−</button>
                    <button className="btn sm secondary" onClick={() => adjust(r, +1)}>+</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
