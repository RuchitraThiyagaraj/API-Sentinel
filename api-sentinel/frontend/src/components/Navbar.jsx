/**
 * components/Navbar.jsx
 * ----------------------
 * Simple top navigation. Demonstrates NavLink + logout via AuthContext.
 */

import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <nav>
        <NavLink to="/dashboard" className="brand">
          🛡️ API Sentinel
        </NavLink>

        <div className="navbar-right">
          {user && <span className="navbar-user">Hi, {user.name}</span>}
          <button className="btn-secondary" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </nav>
    </header>
  );
}
