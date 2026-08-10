/**
 * pages/ApiDetails.jsx
 * ----------------------
 * On mount: fetch API details + monitoring history (two useEffect-driven
 * requests). Renders:
 *   - status summary
 *   - total/successful/failed counts
 *   - Recharts response-time graph
 *   - check history table (kept inline, no separate CheckHistory.jsx)
 */

import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../services/api";

const STATUS_ICON = { online: "🟢", offline: "🔴", slow: "🟡" };

export default function ApiDetails() {
  const { id } = useParams();

  const [details, setDetails] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  async function fetchData() {
    setLoading(true);
    setError(false);
    try {
      const [detailsRes, historyRes] = await Promise.all([
        api.get(`/apis/${id}`),
        api.get(`/apis/${id}/history`),
      ]);
      setDetails(detailsRes.data);
      setHistory(historyRes.data);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <main className="page"><p>⏳ Loading API details...</p></main>;

  if (error || !details) {
    return (
      <main className="page">
        <p>❌ Unable to load API details.</p>
        <button className="btn-secondary" onClick={fetchData}>Try Again</button>
      </main>
    );
  }

  const chartData = history.map((h) => ({
    time: new Date(h.checked_at).toLocaleTimeString(),
    responseTime: h.response_time ?? 0,
  }));

  return (
    <main className="page">
      <Link to="/dashboard" className="back-link">← Back</Link>

      <h1>{details.name}</h1>
      <p className="api-card-url">{details.url}</p>

      <h2>{STATUS_ICON[details.status] || "⚪"} {(details.status || "unknown").toUpperCase()}</h2>

      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-label">Response Time</span>
          <span className="stat-value">
            {details.response_time ? `${Math.round(details.response_time)} ms` : "—"}
          </span>
        </div>
        <div className="stat-box">
          <span className="stat-label">HTTP Status</span>
          <span className="stat-value">{details.http_status_code ?? "—"}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Uptime</span>
          <span className="stat-value">{details.uptime != null ? `${details.uptime}%` : "—"}</span>
        </div>
        <div className="stat-box">
          <span className="stat-label">Last Checked</span>
          <span className="stat-value">
            {details.last_checked ? new Date(details.last_checked).toLocaleTimeString() : "—"}
          </span>
        </div>
      </div>

      <p>
        Total Checks: {details.total_checks} &nbsp;|&nbsp;
        Successful: {details.successful_checks} &nbsp;|&nbsp;
        Failed: {details.failed_checks}
      </p>

      <h3>Response-Time History</h3>
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis label={{ value: "ms", angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Line type="monotone" dataKey="responseTime" stroke="#2563eb" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p>No monitoring data yet.</p>
      )}

      <h3>Check History</h3>
      {history.length === 0 ? (
        <p>No checks recorded yet.</p>
      ) : (
        <table className="history-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Status</th>
              <th>HTTP</th>
              <th>Response</th>
            </tr>
          </thead>
          <tbody>
            {[...history].reverse().slice(0, 20).map((h) => (
              <tr key={h.id}>
                <td>{new Date(h.checked_at).toLocaleTimeString()}</td>
                <td>{STATUS_ICON[h.status] || "⚪"} {h.status}</td>
                <td>{h.http_status_code ?? "—"}</td>
                <td>{h.response_time ? `${Math.round(h.response_time)} ms` : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
