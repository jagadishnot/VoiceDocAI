import { Link } from "react-router-dom";
import "../styles/pages.css";

export default function Dashboard() {
  return (
    <div className="page">
      <div className="center-container">

        {/* 🔥 HERO SECTION */}
        <div className="dashboard-hero">
          <h1 className="dashboard-title">🚀 AI Agent Analyzer</h1>
          <p className="dashboard-sub">
            Smart AI platform to analyze Documents, Excel data, and Audio with powerful insights
          </p>

          {/* ✨ FLOATING ORBS */}
          <div className="orb orb1"></div>
          <div className="orb orb2"></div>
          <div className="orb orb3"></div>
        </div>

        {/* 🧊 FEATURE CARDS */}
        <div className="dashboard-grid">

          <Link to="/document" className="dashboard-card">
            <div className="card-icon">📄</div>
            <h2>Document AI</h2>
            <p>Upload PDF/DOC → Ask questions using RAG</p>

            <ul>
              <li>✔ Smart Q&A</li>
              <li>✔ Context-based answers</li>
              <li>✔ AI-powered retrieval</li>
            </ul>
          </Link>

          <Link to="/excel" className="dashboard-card">
            <div className="card-icon">📊</div>
            <h2>Excel Analyzer</h2>
            <p>Upload Excel → Get charts, stats & insights</p>

            <ul>
              <li>✔ Auto visualizations</li>
              <li>✔ Data insights</li>
              <li>✔ PDF/ZIP export</li>
            </ul>
          </Link>

          <Link to="/audio" className="dashboard-card">
            <div className="card-icon">🎧</div>
            <h2>Audio AI</h2>
            <p>Upload audio → Transcript, Summary, Translation</p>

            <ul>
              <li>✔ Speech-to-text</li>
              <li>✔ Multi-language</li>
              <li>✔ Smart notes</li>
            </ul>
          </Link>

        </div>

        {/* 🔥 EXTRA INFO SECTION */}
        <div className="dashboard-info glass">
          <h2>⚡ Why AI Analyzer?</h2>
          <p>
            AI Analyzer combines Natural Language Processing, Data Analytics, and Speech AI
            into a single powerful platform. Designed for students, developers, and businesses.
          </p>

          <div className="info-grid">
            <div className="info-box">⚡ Fast Processing</div>
            <div className="info-box">🧠 AI Powered</div>
            <div className="info-box">🌍 Multi-language</div>
            <div className="info-box">📊 Visual Insights</div>
          </div>
        </div>

      </div>
    </div>
  );
}