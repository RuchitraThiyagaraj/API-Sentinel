/**
 * pages/Dashboard.jsx
 * --------------------
 * Fetches the user's APIs on mount (useEffect), then supports
 * client-side search + status filter (filter() + map(), kept inline
 * per the spec -- no separate SearchBar/StatusFilter components).
 */

import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import ApiCard from "../components/ApiCard.jsx";
import { useAuth } from "../context/AuthContext.jsx";

const FILTERS = ["All", "Online", "Offline", "Slow"];

export default function Dashboard() {
  const { user } = useAuth();

  const [apis, setApis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("All");

  useEffect(() => {
    fetchApis();
  }, []);

  async function fetchApis() {
    setLoading(true);
    setError(false);
    try {
      const res = await api.get("/apis");
      setApis(res.data);
    } catch (err) {
      setError(true);
    } finally {
      setLoading(false);
    }
  }

  // search + status filter, done inline with plain JS array methods
  const filteredApis = apis
    .filter((a) => a.name.toLowerCase().includes(search.toLowerCase()))
    .filter((a) => {
      if (activeFilter === "All") return true;
      return a.status === activeFilter.toLowerCase();
    });

  return (
    <main className="page">
      <h1>Welcome, {user?.name}!</h1>

      <input
        className="search-input"
        placeholder="Search APIs..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="filter-row">
        {FILTERS.map((f) => (
          <button
            key={f}
            className={`filter-btn ${activeFilter === f ? "active" : ""}`}
            onClick={() => setActiveFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {loading && <p>⏳ Loading APIs...</p>}

      {!loading && error && (
        <div>
          <p>❌ Unable to load APIs.</p>
          <button className="btn-secondary" onClick={fetchApis}>
            Try Again
          </button>
        </div>
      )}

      {!loading && !error && apis.length === 0 && (
        <div>
          <p>No APIs found.</p>
          <Link to="/add-api" className="btn-primary">
            Add API
          </Link>
        </div>
      )}

      {!loading && !error && apis.length > 0 && (
        <div className="api-list">
          {filteredApis.map((a) => (
            <ApiCard key={a.id} api={a} />
          ))}
        </div>
      )}

      {!loading && !error && apis.length > 0 && (
        <Link to="/add-api" className="btn-primary add-api-btn">
          + Add API
        </Link>
      )}
    </main>
  );
}
