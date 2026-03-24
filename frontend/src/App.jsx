import { useState, useCallback, useRef } from "react";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid, Legend
} from "recharts";

// API base: /api is proxied to backend by nginx (Docker) or Vite (dev)
const API_BASE = "/api";

// ─── Severity Badge ───────────────────────────────────────────────────────────
const SeverityBadge = ({ severity }) => {
  const map = {
    None:     { bg: "#064e3b", text: "#34d399", label: "✅ Healthy" },
    Moderate: { bg: "#78350f", text: "#fbbf24", label: "⚠️ Moderate" },
    High:     { bg: "#7c2d12", text: "#fb923c", label: "🔴 High Risk" },
    Critical: { bg: "#4c0519", text: "#f87171", label: "🚨 Critical" },
    Unknown:  { bg: "#1e293b", text: "#94a3b8", label: "❓ Unknown" },
  };
  const s = map[severity] || map.Unknown;
  return (
    <span style={{
      background: s.bg, color: s.text,
      padding: "4px 14px", borderRadius: 999,
      fontSize: 13, fontWeight: 700, letterSpacing: "0.05em",
      border: `1px solid ${s.text}33`
    }}>{s.label}</span>
  );
};

// ─── Confidence Bar ───────────────────────────────────────────────────────────
const ConfidenceBar = ({ value, color = "#4ade80" }) => (
  <div style={{ width: "100%", background: "#1e293b", borderRadius: 999, height: 10, overflow: "hidden" }}>
    <div style={{
      width: `${value}%`, height: "100%",
      background: `linear-gradient(90deg, ${color}, ${color}cc)`,
      borderRadius: 999,
      transition: "width 1.2s cubic-bezier(0.4,0,0.2,1)",
      boxShadow: `0 0 8px ${color}88`
    }} />
  </div>
);

// ─── Upload Zone ──────────────────────────────────────────────────────────────
const UploadZone = ({ onFile, loading }) => {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const handleDrop = useCallback(e => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) onFile(file);
  }, [onFile]);

  return (
    <div
      onClick={() => !loading && inputRef.current.click()}
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      style={{
        border: `2px dashed ${dragging ? "#4ade80" : "#334155"}`,
        borderRadius: 20,
        padding: "52px 32px",
        textAlign: "center",
        cursor: loading ? "not-allowed" : "pointer",
        background: dragging ? "#0f2818" : "#0f172a",
        transition: "all 0.3s",
        position: "relative",
        overflow: "hidden"
      }}
    >
      {/* Subtle grid bg */}
      <div style={{
        position: "absolute", inset: 0, opacity: 0.04,
        backgroundImage: "linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px)",
        backgroundSize: "40px 40px", pointerEvents: "none"
      }} />

      <div style={{ fontSize: 56, marginBottom: 16 }}>🌿</div>
      <p style={{ color: "#e2e8f0", fontSize: 18, fontWeight: 700, margin: "0 0 8px" }}>
        {loading ? "Analyzing your crop..." : "Drop a leaf photo here"}
      </p>
      <p style={{ color: "#64748b", fontSize: 14, margin: 0 }}>
        {loading ? "AI model processing..." : "or click to select · JPEG, PNG, WebP · Max 10MB"}
      </p>
      {loading && (
        <div style={{ marginTop: 20 }}>
          <div style={{
            width: 48, height: 48, border: "3px solid #1e293b",
            borderTop: "3px solid #4ade80", borderRadius: "50%",
            animation: "spin 1s linear infinite", margin: "0 auto"
          }} />
        </div>
      )}
      <input ref={inputRef} type="file" accept="image/*" hidden
        onChange={e => e.target.files[0] && onFile(e.target.files[0])} />
    </div>
  );
};

// ─── Result Card ──────────────────────────────────────────────────────────────
const ResultCard = ({ result, imageUrl }) => {
  const severityColor = result.severity_color || "#4ade80";
  return (
    <div style={{
      background: "#0f172a", borderRadius: 20,
      border: "1px solid #1e293b", overflow: "hidden"
    }}>
      {/* Header */}
      <div style={{
        padding: "24px 28px", borderBottom: "1px solid #1e293b",
        background: `linear-gradient(135deg, ${severityColor}11, transparent)`
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
          <div>
            <p style={{ color: "#64748b", fontSize: 12, margin: "0 0 6px", textTransform: "uppercase", letterSpacing: "0.1em" }}>Diagnosis</p>
            <h2 style={{ color: "#f1f5f9", margin: 0, fontSize: 22, fontWeight: 800 }}>{result.display_name}</h2>
          </div>
          <SeverityBadge severity={result.severity} />
        </div>

        <div style={{ marginTop: 20 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <span style={{ color: "#94a3b8", fontSize: 13 }}>Confidence</span>
            <span style={{ color: severityColor, fontSize: 13, fontWeight: 700 }}>{result.confidence}%</span>
          </div>
          <ConfidenceBar value={result.confidence} color={severityColor} />
        </div>
      </div>

      {/* Body */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
        {/* Left: Image + Top-5 */}
        <div style={{ padding: "24px 28px", borderRight: "1px solid #1e293b" }}>
          {imageUrl && (
            <img src={imageUrl} alt="Uploaded crop"
              style={{ width: "100%", borderRadius: 12, marginBottom: 20, maxHeight: 200, objectFit: "cover" }} />
          )}

          <p style={{ color: "#94a3b8", fontSize: 12, margin: "0 0 12px", textTransform: "uppercase", letterSpacing: "0.08em" }}>Top Predictions</p>
          {result.top5?.map((item, i) => (
            <div key={i} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ color: i === 0 ? "#f1f5f9" : "#64748b", fontSize: 12, maxWidth: "75%", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {item.class.replace("___", " - ").replace(/_/g, " ")}
                </span>
                <span style={{ color: i === 0 ? "#4ade80" : "#475569", fontSize: 12, fontWeight: 600 }}>
                  {(item.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <ConfidenceBar value={item.confidence * 100} color={i === 0 ? severityColor : "#334155"} />
            </div>
          ))}
        </div>

        {/* Right: Info */}
        <div style={{ padding: "24px 28px" }}>
          <div style={{ marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", fontSize: 12, margin: "0 0 8px", textTransform: "uppercase", letterSpacing: "0.08em" }}>About this Disease</p>
            <p style={{ color: "#cbd5e1", fontSize: 14, lineHeight: 1.7, margin: 0 }}>{result.description}</p>
          </div>

          <div style={{ marginBottom: 20 }}>
            <p style={{ color: "#94a3b8", fontSize: 12, margin: "0 0 10px", textTransform: "uppercase", letterSpacing: "0.08em" }}>💊 Treatment Steps</p>
            {result.treatment?.map((t, i) => (
              <div key={i} style={{ display: "flex", gap: 10, marginBottom: 8, alignItems: "flex-start" }}>
                <span style={{ color: "#4ade80", fontSize: 11, fontWeight: 700, minWidth: 20, marginTop: 2 }}>{i + 1}.</span>
                <span style={{ color: "#cbd5e1", fontSize: 13, lineHeight: 1.5 }}>{t}</span>
              </div>
            ))}
          </div>

          <div style={{
            background: "#0c2340", borderRadius: 12, padding: "14px 16px",
            border: "1px solid #1e3a5f"
          }}>
            <p style={{ color: "#60a5fa", fontSize: 12, margin: "0 0 6px", fontWeight: 700 }}>🛡️ Prevention</p>
            <p style={{ color: "#93c5fd", fontSize: 13, margin: 0, lineHeight: 1.5 }}>{result.prevention}</p>
          </div>

          {result.demo_mode && (
            <div style={{
              marginTop: 14, background: "#1a1a0f", borderRadius: 10, padding: "10px 14px",
              border: "1px solid #ca8a04"
            }}>
              <p style={{ color: "#facc15", fontSize: 11, margin: 0 }}>
                ⚡ Demo mode — train the model to get real predictions
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ─── Dashboard Tab ────────────────────────────────────────────────────────────
const Dashboard = ({ stats }) => {
  if (!stats) return (
    <div style={{ textAlign: "center", padding: 60, color: "#64748b" }}>
      <p style={{ fontSize: 36, margin: "0 0 12px" }}>📊</p>
      <p>Loading dashboard...</p>
    </div>
  );

  const cards = [
    { label: "Total Scans", value: stats.total_scans.toLocaleString(), icon: "🔬", color: "#60a5fa" },
    { label: "Diseases Found", value: stats.diseases_detected.toLocaleString(), icon: "🦠", color: "#f87171" },
    { label: "Healthy Plants", value: stats.healthy_plants.toLocaleString(), icon: "🌱", color: "#4ade80" },
    { label: "Model Accuracy", value: `${stats.accuracy}%`, icon: "🎯", color: "#a78bfa" },
  ];

  return (
    <div>
      {/* Stat Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
        {cards.map((c, i) => (
          <div key={i} style={{
            background: "#0f172a", borderRadius: 16, padding: "20px 22px",
            border: "1px solid #1e293b"
          }}>
            <div style={{ fontSize: 28, marginBottom: 10 }}>{c.icon}</div>
            <div style={{ color: c.color, fontSize: 28, fontWeight: 800 }}>{c.value}</div>
            <div style={{ color: "#64748b", fontSize: 13, marginTop: 4 }}>{c.label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr", gap: 20 }}>
        {/* Weekly Scans Chart */}
        <div style={{ background: "#0f172a", borderRadius: 16, padding: 24, border: "1px solid #1e293b" }}>
          <h3 style={{ color: "#e2e8f0", margin: "0 0 20px", fontSize: 16 }}>📈 Weekly Scans</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={stats.recent_scans}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 12 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
              <Tooltip contentStyle={{ background: "#1e293b", border: "none", borderRadius: 8, color: "#e2e8f0" }} />
              <Bar dataKey="scans" fill="#3b82f6" radius={[4,4,0,0]} name="Total Scans" />
              <Bar dataKey="diseased" fill="#ef4444" radius={[4,4,0,0]} name="Diseased" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Pie */}
        <div style={{ background: "#0f172a", borderRadius: 16, padding: 24, border: "1px solid #1e293b" }}>
          <h3 style={{ color: "#e2e8f0", margin: "0 0 20px", fontSize: 16 }}>🎯 Severity Breakdown</h3>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={stats.severity_breakdown} dataKey="count" nameKey="severity"
                cx="50%" cy="50%" outerRadius={70} innerRadius={35} paddingAngle={3}>
                {stats.severity_breakdown.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ background: "#1e293b", border: "none", borderRadius: 8, color: "#e2e8f0" }} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
            {stats.severity_breakdown.map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: s.color }} />
                <span style={{ color: "#94a3b8", fontSize: 12 }}>{s.severity} ({s.count})</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Most Common Diseases */}
      <div style={{ background: "#0f172a", borderRadius: 16, padding: 24, border: "1px solid #1e293b", marginTop: 20 }}>
        <h3 style={{ color: "#e2e8f0", margin: "0 0 20px", fontSize: 16 }}>🦠 Most Common Diseases</h3>
        {stats.most_common.map((d, i) => (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 14 }}>
            <span style={{ color: "#64748b", fontSize: 13, minWidth: 24, textAlign: "right" }}>#{i+1}</span>
            <span style={{ color: "#cbd5e1", fontSize: 14, minWidth: 200 }}>{d.name}</span>
            <div style={{ flex: 1 }}>
              <ConfidenceBar value={d.percentage} color={i === 0 ? "#ef4444" : "#3b82f6"} />
            </div>
            <span style={{ color: "#94a3b8", fontSize: 13, minWidth: 60, textAlign: "right" }}>{d.count} scans</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [tab, setTab] = useState("scan");
  const [result, setResult] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);

  const handleFile = async (file) => {
    setLoading(true);
    setResult(null);
    setError(null);
    const url = URL.createObjectURL(file);
    setImageUrl(url);

    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/predict`, { method: "POST", body: formData });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResult(data);
      setScanHistory(prev => [{ ...data, imageUrl: url, timestamp: new Date().toLocaleTimeString() }, ...prev].slice(0, 10));
    } catch (err) {
      setError(`Could not connect to backend. Make sure the API is running at ${API_BASE}`);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      const data = await res.json();
      setStats(data);
    } catch { setStats(null); }
  };

  if (tab === "dashboard" && !stats) loadStats();

  const tabs = [
    { id: "scan", label: "🔬 Scan", },
    { id: "history", label: "📋 History" },
    { id: "dashboard", label: "📊 Dashboard" },
  ];

  return (
    <div style={{
      minHeight: "100vh",
      background: "#020617",
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      color: "#f1f5f9"
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: none; } }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
      `}</style>

      {/* Nav */}
      <nav style={{
        position: "sticky", top: 0, zIndex: 50,
        borderBottom: "1px solid #1e293b",
        background: "#020617ee",
        backdropFilter: "blur(20px)",
        padding: "0 32px"
      }}>
        <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", height: 64 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, flex: 1 }}>
            <span style={{ fontSize: 24 }}>🌿</span>
            <span style={{ fontWeight: 800, fontSize: 18, color: "#f1f5f9" }}>CropScan</span>
            <span style={{
              background: "#14532d", color: "#4ade80", fontSize: 11,
              padding: "2px 8px", borderRadius: 999, fontWeight: 600
            }}>AI</span>
          </div>
          <div style={{ display: "flex", gap: 4 }}>
            {tabs.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)} style={{
                background: tab === t.id ? "#1e293b" : "transparent",
                border: tab === t.id ? "1px solid #334155" : "1px solid transparent",
                color: tab === t.id ? "#f1f5f9" : "#64748b",
                padding: "8px 18px", borderRadius: 10, cursor: "pointer",
                fontSize: 14, fontWeight: 600, transition: "all 0.2s"
              }}>{t.label}</button>
            ))}
          </div>
        </div>
      </nav>

      <main style={{ maxWidth: 1200, margin: "0 auto", padding: "32px 32px 64px" }}>

        {/* ── SCAN TAB ── */}
        {tab === "scan" && (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            <div style={{ textAlign: "center", marginBottom: 40 }}>
              <h1 style={{ fontSize: 42, fontWeight: 800, lineHeight: 1.1, marginBottom: 12 }}>
                Detect Crop Diseases<br />
                <span style={{ background: "linear-gradient(90deg, #4ade80, #22d3ee)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
                  with AI Precision
                </span>
              </h1>
              <p style={{ color: "#64748b", fontSize: 16, maxWidth: 480, margin: "0 auto" }}>
                Upload a photo of any plant leaf — our model identifies diseases instantly with treatment recommendations.
              </p>
            </div>

            <div style={{ maxWidth: 760, margin: "0 auto" }}>
              <UploadZone onFile={handleFile} loading={loading} />

              {error && (
                <div style={{
                  marginTop: 20, background: "#4c0519", borderRadius: 12,
                  padding: "16px 20px", border: "1px solid #f87171"
                }}>
                  <p style={{ color: "#fca5a5", margin: 0, fontSize: 14 }}>⚠️ {error}</p>
                </div>
              )}

              {result && !loading && (
                <div style={{ marginTop: 24, animation: "fadeIn 0.5s ease" }}>
                  <ResultCard result={result} imageUrl={imageUrl} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── HISTORY TAB ── */}
        {tab === "history" && (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 24 }}>📋 Scan History</h2>
            {scanHistory.length === 0 ? (
              <div style={{ textAlign: "center", padding: "80px 0", color: "#64748b" }}>
                <p style={{ fontSize: 48, marginBottom: 16 }}>🔬</p>
                <p style={{ fontSize: 16 }}>No scans yet. Go to the Scan tab to analyze a crop!</p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
                {scanHistory.map((item, i) => (
                  <div key={i} style={{
                    background: "#0f172a", borderRadius: 16, padding: "20px 24px",
                    border: "1px solid #1e293b", display: "flex", alignItems: "center", gap: 20
                  }}>
                    {item.imageUrl && (
                      <img src={item.imageUrl} alt="" style={{ width: 72, height: 72, borderRadius: 10, objectFit: "cover" }} />
                    )}
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
                        <h3 style={{ color: "#f1f5f9", fontSize: 16, fontWeight: 700 }}>{item.display_name}</h3>
                        <SeverityBadge severity={item.severity} />
                      </div>
                      <p style={{ color: "#64748b", fontSize: 13 }}>Confidence: {item.confidence}% · {item.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── DASHBOARD TAB ── */}
        {tab === "dashboard" && (
          <div style={{ animation: "fadeIn 0.4s ease" }}>
            <h2 style={{ fontSize: 28, fontWeight: 800, marginBottom: 24 }}>📊 Analytics Dashboard</h2>
            <Dashboard stats={stats} />
          </div>
        )}
      </main>
    </div>
  );
}
