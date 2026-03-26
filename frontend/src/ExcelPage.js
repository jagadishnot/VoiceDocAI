import React, { useState } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  LineChart, Line, CartesianGrid,
  ResponsiveContainer, PieChart, Pie, Cell,
  Legend
} from "recharts";

const COLORS = ["#4CAF50","#2196F3","#FF9800","#E91E63","#9C27B0","#00BCD4"];

function ExcelPage() {

  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");

  const uploadExcel = async () => {
    if (!file) return alert("Upload .xlsx file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const res = await axios.post(
        "http://127.0.0.1:8000/upload-excel",
        formData
      );
      setData(res.data);
    } catch (err) {
      alert("Backend error ❌");
    }
    setLoading(false);
  };

  const downloadPDF = async () => {
    if (!data) return;

    const res = await axios.post(
      "http://127.0.0.1:8000/export-pdf",
      data,
      { responseType: "blob" }
    );

    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "analytics_report.pdf");
    document.body.appendChild(link);
    link.click();
  };

  const renderCharts = () =>
    data?.charts?.map((chart, index) => (
      <div key={index} style={styles.chartCard}>
        <h3>{chart.title}</h3>
        <p style={styles.axisLabel}>
          X: {chart.x_label} | Y: {chart.y_label}
        </p>

        <ResponsiveContainer width="100%" height={320}>
          {chart.type === "bar" && (
            <BarChart data={chart.x.map((v,i)=>({name:v,value:chart.y[i]}))}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#00c6ff" radius={[8,8,0,0]} />
            </BarChart>
          )}

          {chart.type === "line" && (
            <LineChart data={chart.x.map((v,i)=>({name:v,value:chart.y[i]}))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#4CAF50" strokeWidth={3}/>
            </LineChart>
          )}

          {chart.type === "pie" && (
            <PieChart>
              <Pie
                data={chart.x.map((v,i)=>({name:v,value:chart.y[i]}))}
                dataKey="value"
                outerRadius={110}
                label
              >
                {chart.x.map((_,i)=>(
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
    ));

  return (
    <div style={styles.mainContainer}>

      {/* Sidebar */}
      <div style={styles.sidebar}>
        <h2 style={{marginBottom:"30px"}}>📊 VoiceDocAI</h2>

        {["overview","charts","correlation"].map(tab=>(
          <button
            key={tab}
            style={activeTab===tab ? styles.activeBtn : styles.sideBtn}
            onClick={()=>setActiveTab(tab)}
          >
            {tab.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Main Content */}
      <div style={styles.content}>

        <div style={styles.topBar}>
          <input
            type="file"
            accept=".xlsx"
            onChange={(e)=>setFile(e.target.files[0])}
          />
          <button style={styles.primaryBtn} onClick={uploadExcel}>
            {loading ? "Analyzing..." : "Analyze Excel"}
          </button>

          {data && (
            <button style={styles.secondaryBtn} onClick={downloadPDF}>
              📄 Export PDF
            </button>
          )}
        </div>

        {!data && <h2 style={{marginTop:"60px"}}>Upload Excel to Start Analysis</h2>}

        {data && activeTab==="overview" && (
          <>
            {/* KPI CARDS */}
            <div style={styles.kpiGrid}>
              <div style={styles.kpiCard}>
                <h4>Total Rows</h4>
                <h2>{data.dataset_info?.rows}</h2>
              </div>
              <div style={styles.kpiCard}>
                <h4>Total Columns</h4>
                <h2>{data.dataset_info?.columns}</h2>
              </div>
              <div style={styles.kpiCard}>
                <h4>Numeric Columns</h4>
                <h2>{data.numeric_columns?.length}</h2>
              </div>
              <div style={styles.kpiCard}>
                <h4>Categorical Columns</h4>
                <h2>{data.categorical_columns?.length}</h2>
              </div>
            </div>

            {/* Summary */}
            <div style={styles.summarySection}>
              {Object.keys(data.summary || {}).map(col=>(
                <div key={col} style={styles.summaryCard}>
                  <h3>{col}</h3>
                  <p>Mean: {data.summary[col]?.mean}</p>
                  <p>Total: {data.summary[col]?.sum}</p>
                  <p>Std Dev: {data.summary[col]?.std}</p>
                </div>
              ))}
            </div>
          </>
        )}

        {data && activeTab==="charts" && (
          <div style={styles.chartGrid}>
            {renderCharts()}
          </div>
        )}

        {data && activeTab==="correlation" && (
          <div style={styles.corrBox}>
            <h2>Correlation Matrix</h2>
            <pre style={{whiteSpace:"pre-wrap"}}>
              {JSON.stringify(data.correlation_matrix, null, 2)}
            </pre>
          </div>
        )}

      </div>
    </div>
  );
}

const styles = {

  mainContainer:{
    display:"flex",
    height:"100vh",
    fontFamily:"Segoe UI"
  },

  sidebar:{
    width:"250px",
    background:"linear-gradient(180deg,#0f2027,#203a43,#2c5364)",
    color:"white",
    padding:"25px",
    display:"flex",
    flexDirection:"column"
  },

  sideBtn:{
    background:"transparent",
    color:"white",
    border:"none",
    padding:"12px",
    textAlign:"left",
    cursor:"pointer",
    fontSize:"14px",
    marginBottom:"10px",
    borderRadius:"8px",
    transition:"0.3s"
  },

  activeBtn:{
    background:"#00c6ff",
    color:"white",
    border:"none",
    padding:"12px",
    textAlign:"left",
    cursor:"pointer",
    fontSize:"14px",
    marginBottom:"10px",
    borderRadius:"8px"
  },

  content:{
    flex:1,
    padding:"35px",
    background:"linear-gradient(135deg,#1e3c72,#2a5298)",
    color:"white",
    overflowY:"auto"
  },

  topBar:{
    display:"flex",
    gap:"15px",
    marginBottom:"30px"
  },

  primaryBtn:{
    padding:"10px 20px",
    background:"linear-gradient(90deg,#00c6ff,#0072ff)",
    border:"none",
    borderRadius:"8px",
    color:"white",
    fontWeight:"bold",
    cursor:"pointer"
  },

  secondaryBtn:{
    padding:"10px 20px",
    background:"#ff9800",
    border:"none",
    borderRadius:"8px",
    color:"white",
    fontWeight:"bold",
    cursor:"pointer"
  },

  kpiGrid:{
    display:"grid",
    gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",
    gap:"20px",
    marginBottom:"35px"
  },

  kpiCard:{
    background:"rgba(255,255,255,0.15)",
    padding:"25px",
    borderRadius:"14px",
    backdropFilter:"blur(12px)",
    textAlign:"center",
    boxShadow:"0 6px 20px rgba(0,0,0,0.3)"
  },

  summarySection:{
    display:"grid",
    gridTemplateColumns:"repeat(auto-fit,minmax(260px,1fr))",
    gap:"20px"
  },

  summaryCard:{
    background:"rgba(255,255,255,0.12)",
    padding:"20px",
    borderRadius:"14px",
    backdropFilter:"blur(8px)"
  },

  chartGrid:{
    display:"grid",
    gridTemplateColumns:"repeat(auto-fit,minmax(450px,1fr))",
    gap:"30px"
  },

  chartCard:{
    background:"white",
    color:"black",
    padding:"25px",
    borderRadius:"18px",
    boxShadow:"0 10px 25px rgba(0,0,0,0.35)"
  },

  axisLabel:{
    fontSize:"13px",
    color:"#666"
  },

  corrBox:{
    background:"white",
    color:"black",
    padding:"25px",
    borderRadius:"16px",
    boxShadow:"0 8px 20px rgba(0,0,0,0.4)"
  }
};

export default ExcelPage;