/**
 * components/ApiForm.jsx
 * ------------------------
 * Reusable controlled form for adding an API manually.
 * Used directly by AddApi.jsx, and also reused to let the user
 * edit LLM-extracted fields before confirming.
 *
 * Props:
 *   initialValues (optional)  - pre-fill the form (used after LLM extraction)
 *   onSubmit(values)          - called with the form data on submit
 *   submitLabel (default "Add API")
 */

import { useState } from "react";

const DEFAULT_VALUES = { name: "", url: "", method: "GET", auth_token: "" };

export default function ApiForm({ initialValues, onSubmit, submitLabel = "Add API" }) {
  const [values, setValues] = useState({ ...DEFAULT_VALUES, ...initialValues });
  const [error, setError] = useState("");

  function handleChange(e) {
    const { name, value } = e.target;
    setValues((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!values.name || !values.url) {
      setError("API Name and API URL are required.");
      return;
    }

    onSubmit(values);
  }

  return (
    <form onSubmit={handleSubmit} className="card-form">
      {error && <p className="error-text">{error}</p>}

      <label>
        API Name
        <input name="name" value={values.name} onChange={handleChange} placeholder="Payment API" />
      </label>

      <label>
        API URL
        <input
          name="url"
          value={values.url}
          onChange={handleChange}
          placeholder="https://api.example.com/payments"
        />
      </label>

      <label>
        HTTP Method
        <select name="method" value={values.method} onChange={handleChange}>
          <option value="GET">GET</option>
          <option value="POST">POST</option>
          <option value="PUT">PUT</option>
          <option value="DELETE">DELETE</option>
        </select>
      </label>

      <label>
        Authorization Token (optional)
        <input
          name="auth_token"
          type="password"
          value={values.auth_token}
          onChange={handleChange}
          placeholder="Bearer token"
        />
      </label>

      <button type="submit" className="btn-primary">
        {submitLabel}
      </button>
    </form>
  );
}
