import { useState } from "react";
import { api } from "../lib/api";

interface Msg { role: "user" | "bot"; text: string; sources?: string[]; }
interface AssistResp { answer: string; sources: string[]; suggested_actions: string[]; }

const STARTERS = [
  "What assets are at highest risk?",
  "Which PMs are overdue?",
  "What parts are below reorder point?",
];

export default function Assist() {
  const [log, setLog] = useState<Msg[]>([
    { role: "bot", text: "Hi, I'm the MaxiManage Assist agent. I'm grounded in your live asset, work order, PM and inventory data. Ask me anything about your maintenance operation.", sources: ["MaxiManage knowledge base"] },
  ]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  const send = async (q: string) => {
    if (busy || !q.trim()) return;
    setLog((l) => [...l, { role: "user", text: q }]);
    setInput("");
    setBusy(true);
    try {
      const r = await api.post<AssistResp>("/api/ai/assist", { question: q });
      setLog((l) => [...l, { role: "bot", text: r.answer, sources: r.sources }]);
    } catch (e: any) {
      setLog((l) => [...l, { role: "bot", text: "Sorry, something went wrong: " + e.message }]);
    } finally { setBusy(false); }
  };

  return (
    <div className="card" style={{ maxWidth: 820 }}>
      <p className="muted" style={{ marginTop: 0 }}>Maximo Assist — a generative AI agent that answers questions and recommends actions using your operational data.</p>
      <div className="chat-log">
        {log.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            {m.text}
            {m.sources && m.sources.length > 0 && <div style={{ fontSize: 11, opacity: 0.7, marginTop: 6 }}>Sources: {m.sources.join(", ")}</div>}
          </div>
        ))}
        {busy && <div className="bubble bot">Thinking…</div>}
      </div>
      <div className="suggest" style={{ marginBottom: 12 }}>
        {STARTERS.map((s) => <button key={s} type="button" className="chip" disabled={busy} onClick={() => send(s)}>{s}</button>)}
      </div>
      <form style={{ display: "flex", gap: 10 }} onSubmit={(e) => { e.preventDefault(); send(input); }}>
        <input placeholder="Ask about assets, PMs, inventory…" value={input} onChange={(e) => setInput(e.target.value)} disabled={busy} />
        <button className="btn" type="submit" disabled={busy}>Send</button>
      </form>
    </div>
  );
}
