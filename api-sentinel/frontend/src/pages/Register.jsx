/**
 * pages/Register.jsx
 * -------------------
 * Controlled form with client-side validation:
 *   - name required
 *   - email required
 *   - password required
 *   - passwords must match
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function validate() {
    if (!form.name) return "Name is required.";
    if (!form.email) return "Email is required.";
    if (!form.password) return "Password is required.";
    if (form.password !== form.confirm_password) return "Passwords must match.";
    return "";
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setError("");
    setLoading(true);
    try {
      await api.post("/auth/register", form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Registration failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>API Sentinel</h1>
        <h2>Create Account</h2>

        {error && <p className="error-text">{error}</p>}

        <form onSubmit={handleSubmit}>
          <label>
            Name
            <input name="name" value={form.name} onChange={handleChange} />
          </label>

          <label>
            Email
            <input name="email" type="email" value={form.email} onChange={handleChange} />
          </label>

          <label>
            Password
            <input name="password" type="password" value={form.password} onChange={handleChange} />
          </label>

          <label>
            Confirm Password
            <input
              name="confirm_password"
              type="password"
              value={form.confirm_password}
              onChange={handleChange}
            />
          </label>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Creating..." : "Create Account"}
          </button>
        </form>

        <p>
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </div>
    </div>
  );
}
