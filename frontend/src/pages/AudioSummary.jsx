import { useState } from "react";
import API from "../api/api";
import "../styles/pages.css";

export default function Audio() {
  const [file, setFile] = useState(null);
  const [audioURL, setAudioURL] = useState(null);

  const [transcript, setTranscript] = useState("");
  const [output, setOutput] = useState("");
  const [language, setLanguage] = useState("English");

  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  // 📥 Upload Audio
  const uploadAudio = async () => {
    if (!file) {
      setStatus("error");
      setStatusMsg("⚠️ Please select an audio file first");
      return;
    }

    try {
      setLoading(true);
      setStatus("loading");
      setStatusMsg("⏳ Processing audio...");

      const formData = new FormData();
      formData.append("file", file);

      const res = await API.post("/audio/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setTranscript(res.data.transcript);
      setOutput("");
      setAudioURL(URL.createObjectURL(file));

      setStatus("success");
      setStatusMsg("✅ Audio uploaded successfully!");
      setTimeout(() => setStatus(""), 3000);

    } catch (err) {
      console.error(err);
      setStatus("error");
      setStatusMsg("❌ Audio upload failed");
    } finally {
      setLoading(false);
    }
  };

  // 🔥 Process Audio
  const processAudio = async (mode) => {
    if (!transcript) {
      setStatus("error");
      setStatusMsg("⚠️ Upload audio first");
      return;
    }

    try {
      setLoading(true);
      setStatus("loading");

      const messages = {
        summary: "⏳ Generating summary...",
        translate: `⏳ Translating to ${language}...`,
        notes: "⏳ Generating notes...",
        conversation: "⏳ Extracting key points..."
      };

      setStatusMsg(messages[mode] || "Processing...");

      const res = await API.post("/audio/process", {
        transcript,
        mode,
        language
      });

      setOutput(res.data.output);

      setStatus("success");
      setStatusMsg(`✅ ${mode.toUpperCase()} completed!`);
      setTimeout(() => setStatus(""), 3000);

    } catch (err) {
      console.error(err);
      setStatus("error");
      setStatusMsg(`❌ ${mode} failed`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="center-container">

        {/* 🔥 TITLE */}
        <h2 className="page-title">🎧 Audio AI Analyzer</h2>

        {/* 🔔 STATUS */}
        {status && <div className={`status ${status}`}>{statusMsg}</div>}

        {/* 🎵 MAIN CARD */}
        <div className="audio-card glass">

          {/* FILE INPUT */}
          <input
            type="file"
            accept="audio/*"
            onChange={(e) => setFile(e.target.files[0])}
          />

          {/* AUDIO PREVIEW */}
          {audioURL && (
            <audio controls className="audio-player">
              <source src={audioURL} type="audio/mpeg" />
            </audio>
          )}

          {/* CONTROLS */}
          <div className="audio-controls">
            <button onClick={uploadAudio} disabled={loading}>
              ⬆ Upload
            </button>

            <select onChange={(e) => setLanguage(e.target.value)}>
              <option>English</option>
              <option>Tamil</option>
              <option>Hindi</option>
              <option>French</option>
            </select>
          </div>

          {/* ACTION BUTTONS */}
          <div className="audio-actions">
            <button onClick={() => processAudio("summary")} disabled={loading}>
              📄 Summary
            </button>

            <button onClick={() => processAudio("translate")} disabled={loading}>
              🌍 Translate
            </button>

            <button onClick={() => processAudio("notes")} disabled={loading}>
              🧠 Notes
            </button>

            <button onClick={() => processAudio("conversation")} disabled={loading}>
              💬 Key Points
            </button>
          </div>

          {/* LOADING */}
          {loading && <p className="loading">⏳ Processing...</p>}
        </div>

        {/* 📜 TRANSCRIPT */}
        {transcript && (
          <div className="result-card glass">
            <h3>📜 Transcript</h3>
            <p>{transcript}</p>
          </div>
        )}

        {/* 🤖 OUTPUT */}
        {output && (
          <div className="result-card glass">
            <h3>🤖 Result</h3>
            <p>{output}</p>
          </div>
        )}

      </div>
    </div>
  );
}