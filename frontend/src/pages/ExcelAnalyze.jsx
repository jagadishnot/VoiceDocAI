import { useState } from "react";
import API from "../api/api";
import "../styles/pages.css";

export default function ExcelAnalyze() {
  const [fileName, setFileName] = useState("");
  const [charts, setCharts] = useState([]);
  const [insights, setInsights] = useState([]);
  const [stats, setStats] = useState({});

  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  const uploadExcel = async (file) => {
    if (!file) {
      setStatus("error");
      setStatusMsg("⚠️ Please select an Excel file");
      return;
    }

    setFileName(file.name);

    try {
      setLoading(true);
      setStatus("loading");
      setStatusMsg("⏳ Analyzing Excel file...");

      const formData = new FormData();
      formData.append("file", file);

      const res = await API.post("/excel/upload", formData);

      setCharts(res.data.charts || []);
      setInsights(res.data.insights || []);

      setStats({
        rows: res.data.total_rows,
        cols: res.data.total_cols
      });

      setStatus("success");
      setStatusMsg("✅ Excel analyzed successfully!");
      setTimeout(() => setStatus(""), 3000);

      window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });

    } catch (err) {
      console.error(err);
      setStatus("error");
      setStatusMsg("❌ Failed to analyze Excel file");
    } finally {
      setLoading(false);
    }
  };

  const downloadZIP = async () => {
    try {
      const res = await API.get("/excel/download-zip");
      window.open(`http://127.0.0.1:8000${res.data.url}`);
    } catch {
      setStatus("error");
      setStatusMsg("❌ ZIP download failed");
    }
  };

  const downloadPDF = async () => {
    try {
      const res = await API.get("/excel/download-pdf");
      window.open(`http://127.0.0.1:8000${res.data.url}`);
    } catch {
      setStatus("error");
      setStatusMsg("❌ PDF download failed");
    }
  };

  return (
    <div className="page">
      {/* 🔥 CENTER FIX */}
      <div className="center-container">

        <h2>📊 Excel Analyzer Dashboard</h2>

        {status && <div className={`status ${status}`}>{statusMsg}</div>}

        <div className="upload-section">
          <input
            type="file"
            accept=".xlsx,.xls"
            disabled={loading}
            onChange={(e) => uploadExcel(e.target.files[0])}
          />
          {fileName && <p className="file-name">📁 {fileName}</p>}
        </div>

        {loading && <p className="loading">⏳ Processing...</p>}

        {stats.rows && (
          <div className="stats-card">
            <h3>📋 Dataset Overview</h3>
            <div className="stats-grid">
              <div className="stat-box">
                <h4>Rows</h4>
                <p>{stats.rows}</p>
              </div>
              <div className="stat-box">
                <h4>Columns</h4>
                <p>{stats.cols}</p>
              </div>
            </div>
          </div>
        )}

        {charts.length > 0 && (
          <div className="download-section">
            <button onClick={downloadZIP} className="download-btn">
              ⬇️ Download ZIP
            </button>
            <button onClick={downloadPDF} className="download-btn pdf">
              📄 Download PDF
            </button>
          </div>
        )}

        {insights.length > 0 && (
          <div className="insights">
            <h3>📈 Column Insights</h3>
            <div className="insight-grid">
              {insights.map((item, index) => (
                <div key={index} className="insight-card">
                  <h4>{item.column}</h4>
                  <p><strong>Mean:</strong> {item.mean}</p>
                  <p><strong>Max:</strong> {item.max}</p>
                  <p><strong>Min:</strong> {item.min}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {charts.length > 0 ? (
          <div className="charts">
            <h3>📊 Visualizations</h3>
            
            <div className="chart-grid">
              {charts.map((c, i) => (
                <div key={i} className="chart-card">
                  <img
                    src={`http://127.0.0.1:8000${c}`}
                    alt={`chart-${i}`}
                    className="chart-img"
                  />
                </div>
              ))}
            </div>
          </div>
        ) : (
          !loading && (
            <div className="empty-state">
              📊 Upload an Excel file to see visualizations
            </div>
          )
        )}

      </div>
    </div>
  );
}