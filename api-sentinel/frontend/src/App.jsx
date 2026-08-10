/**
 * App.jsx
 * -------
 * Top-level route table. No separate ProtectedRoute component (per the
 * spec) -- the redirect-if-not-logged-in check is done inline here.
 */

import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./context/AuthContext.jsx";

import Navbar from "./components/Navbar.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import AddApi from "./pages/AddApi.jsx";
import ApiDetails from "./pages/ApiDetails.jsx";

export default function App() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <p style={{ textAlign: "center", marginTop: "4rem" }}>Loading...</p>;
  }

  return (
    <>
      {isAuthenticated && <Navbar />}
      <Routes>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />}
        />
        <Route
          path="/register"
          element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />}
        />
        <Route
          path="/dashboard"
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
        />
        <Route
          path="/add-api"
          element={isAuthenticated ? <AddApi /> : <Navigate to="/login" />}
        />
        <Route
          path="/apis/:id"
          element={isAuthenticated ? <ApiDetails /> : <Navigate to="/login" />}
        />
        <Route
          path="*"
          element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />}
        />
      </Routes>
    </>
  );
}
