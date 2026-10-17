import { useEffect } from "react";
import "../styles/pages.css";

export default function StatusMessage({ status, message, onClose }) {
  // 🔹 Auto hide after 3 sec
  useEffect(() => {
    if (!status) return;

    const timer = setTimeout(() => {
      onClose && onClose();
    }, 3000);

    return () => clearTimeout(timer);
  }, [status, onClose]);

  if (!status) return null;

  // 🔹 Icons for each state
  const icons = {
    success: "✅",
    error: "❌",
    loading: "⏳"
  };

  return (
    <div className={`status-box ${status}`}>
      <span className="status-icon">{icons[status]}</span>
      <span className="status-text">{message}</span>
    </div>
  );
}