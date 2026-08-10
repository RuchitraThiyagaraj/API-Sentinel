/**
 * components/ApiCard.jsx
 * ------------------------
 * Presentational component. Dashboard.jsx passes one `api` object down
 * as a prop (Parent -> Child communication / props destructuring).
 */

import { Link } from "react-router-dom";

const STATUS_ICON = {
  online: "🟢",
  offline: "🔴",
  slow: "🟡",
};

export default function ApiCard({ api }) {
  const icon = STATUS_ICON[api.status] || "⚪";

  return (
    <div className="api-card">
      <div className="api-card-header">
        <span>{icon} {api.name}</span>
      </div>

      <p className="api-card-url">{api.url}</p>

      {api.status === "offline" ? (
        <p className="api-card-line">
          Status: Offline{api.http_status_code ? ` — HTTP: ${api.http_status_code}` : ""}
        </p>
      ) : (
        <>
          <p className="api-card-line">
            Response: {api.response_time ? `${Math.round(api.response_time)} ms` : "—"}
          </p>
          <p className="api-card-line">HTTP: {api.http_status_code ?? "—"}</p>
          <p className="api-card-line">Uptime: {api.uptime != null ? `${api.uptime}%` : "—"}</p>
          <p className="api-card-line">
            Last checked: {api.last_checked ? new Date(api.last_checked).toLocaleTimeString() : "never"}
          </p>
        </>
      )}

      <Link to={`/apis/${api.id}`} className="btn-link">
        View Details
      </Link>
    </div>
  );
}
