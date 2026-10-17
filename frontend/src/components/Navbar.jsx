import { NavLink } from "react-router-dom";
import "../styles/navbar.css";

export default function Navbar() {
  return (
    <nav className="navbar">
      {/* Logo */}
      <h2 className="logo">🚀 AI Analyzer</h2>

      {/* Links */}
      <div className="nav-links">
        <NavLink to="/" className="nav-item">
          Home
        </NavLink>

        <NavLink to="/doc" className="nav-item">
          Document
        </NavLink>

        <NavLink to="/excel" className="nav-item">
          Excel
        </NavLink>

        <NavLink to="/audio" className="nav-item">
          Audio
        </NavLink>
      </div>
    </nav>
  );
}