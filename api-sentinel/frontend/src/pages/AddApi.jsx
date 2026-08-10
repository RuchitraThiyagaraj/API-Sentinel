/**
 * pages/AddApi.jsx
 * ------------------
 * Two ways to add an API:
 *   1. Manual (ApiForm directly)
 *   2. Import from Documentation -> paste text -> LLM extracts fields
 *      -> shown to user -> user can [Edit] or [Add API] to confirm.
 *
 * If the LLM import fails, the user can always switch back to Manual.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import ApiForm from "../components/ApiForm.jsx";

export default function AddApi() {
  const navigate = useNavigate();

  const [mode, setMode] = useState("manual"); // "manual" | "import"
  const [docText, setDocText] = useState("");
  const [extracted, setExtracted] = useState(null); // result from LLM
  const [importError, setImportError] = useState("");
  const [importing, setImporting] = useState(false);
  const [saving, setSaving] = useState(false);

  async function handleManualSubmit(values) {
    setSaving(true);
    try {
      await api.post("/apis", values);
      navigate("/dashboard");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to add API.");
    } finally {
      setSaving(false);
    }
  }

  async function handleExtract() {
    if (!docText.trim()) return;
    setImportError("");
    setImporting(true);
    setExtracted(null);
    try {
      const res = await api.post("/apis/import-documentation", {
        documentation_text: docText,
      });
      setExtracted(res.data);
    } catch (err) {
      setImportError(
        err.response?.data?.detail ||
          "Could not extract API info. Please add the API manually instead."
      );
    } finally {
      setImporting(false);
    }
  }

  return (
    <main className="page">
      <h1>Add New API</h1>

      <div className="filter-row">
        <button
          className={`filter-btn ${mode === "manual" ? "active" : ""}`}
          onClick={() => setMode("manual")}
        >
          Add API Manually
        </button>
        <button
          className={`filter-btn ${mode === "import" ? "active" : ""}`}
          onClick={() => setMode("import")}
        >
          Import from Documentation
        </button>
      </div>

      {mode === "manual" && (
        <ApiForm onSubmit={handleManualSubmit} submitLabel={saving ? "Adding..." : "Add API"} />
      )}

      {mode === "import" && !extracted && (
        <div className="card-form">
          {importError && <p className="error-text">{importError}</p>}

          <label>
            Paste API Documentation
            <textarea
              rows={10}
              value={docText}
              onChange={(e) => setDocText(e.target.value)}
              placeholder="Payment API&#10;GET https://api.example.com/payments&#10;Returns payment information.&#10;Authorization: Bearer token"
            />
          </label>

          <button className="btn-primary" onClick={handleExtract} disabled={importing}>
            {importing ? "Extracting..." : "Extract API Info"}
          </button>
        </div>
      )}

      {mode === "import" && extracted && (
        <div className="card-form">
          <h3>API Information Found</h3>
          <p><strong>Name:</strong> {extracted.name}</p>
          <p><strong>URL:</strong> {extracted.url}</p>
          <p><strong>Method:</strong> {extracted.method}</p>

          <div className="filter-row">
            <button className="btn-secondary" onClick={() => setExtracted(null)}>
              Edit
            </button>
            <button
              className="btn-primary"
              onClick={() => handleManualSubmit(extracted)}
              disabled={saving}
            >
              {saving ? "Adding..." : "Add API"}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
