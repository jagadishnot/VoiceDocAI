import { useState } from "react";
import API from "../api/api";
import FileUpload from "../components/FileUpload";
import ChatBox from "../components/ChatBox";
import "../styles/pages.css";

export default function DocumentQA() {
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  // 🔥 NEW STATES
  const [listening, setListening] = useState(false);
  const [soundOn, setSoundOn] = useState(true);

  // ==========================
  // 📂 Upload file
  // ==========================
  const uploadFile = async (file) => {
    try {
      setStatus("loading");
      setStatusMsg("⏳ Uploading document...");

      const formData = new FormData();
      formData.append("file", file);

      const res = await API.post("/doc/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      setSessionId(res.data.session_id);

      setMessages([
        {
          type: "system",
          text: "✅ File uploaded successfully. You can ask questions now."
        }
      ]);

      setStatus("success");
      setStatusMsg("✅ Document uploaded successfully!");
      setTimeout(() => setStatus(""), 3000);

    } catch (err) {
      console.error(err);
      setStatus("error");
      setStatusMsg("❌ Upload failed. Try again.");
    }
  };

  // ==========================
  // 🔊 TEXT TO SPEECH
  // ==========================
  const speakText = (text) => {
    if (!soundOn) return;

    speechSynthesis.cancel(); // stop previous

    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    let index = 0;

    const speakNext = () => {
      if (index >= sentences.length) return;

      const utterance = new SpeechSynthesisUtterance(sentences[index]);
      utterance.rate = 1;

      utterance.onend = () => {
        index++;
        speakNext();
      };

      speechSynthesis.speak(utterance);
    };

    speakNext();
  };

  // ==========================
  // 🎤 VOICE INPUT
  // ==========================
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition not supported");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    recognition.start();
    setListening(true);

    recognition.onresult = (event) => {
      const voiceText = event.results[0][0].transcript;

      askQuestion(voiceText); // 🔥 auto ask

      setListening(false);
    };

    recognition.onerror = () => {
      setListening(false);
    };
  };

  // ==========================
  // 💬 Ask question
  // ==========================
  const askQuestion = async (query) => {
    if (!sessionId) {
      setStatus("error");
      setStatusMsg("⚠️ Please upload a document first");
      return;
    }

    try {
      setLoading(true);

      setMessages((prev) => [...prev, { type: "user", text: query }]);

      const formData = new FormData();
      formData.append("query", query);
      formData.append("session_id", sessionId);

      const res = await API.post("/doc/ask", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const answer = res.data.answer;

      setMessages((prev) => [
        ...prev,
        { type: "bot", text: answer }
      ]);

      // 🔥 AUTO SPEAK
      speakText(answer);

    } catch (err) {
      console.error(err);
      setStatus("error");
      setStatusMsg("❌ Failed to get response");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="center-container">

        <h2>📄 Document AI Assistant</h2>

        {/* 🔔 Status */}
        {status && (
          <div className={`status ${status}`}>
            {statusMsg}
          </div>
        )}

        {/* 📂 Upload */}
        <FileUpload onUpload={uploadFile} />

        {/* 🎤 CONTROLS */}
        <div className="voice-controls">
          <button onClick={startListening}>
            {listening ? "🎙️ Listening..." : "🎤 Speak"}
          </button>

          <button onClick={() => setSoundOn(!soundOn)}>
            {soundOn ? "🔊 Sound ON" : "🔇 Sound OFF"}
          </button>
        </div>

        {/* 💬 CHAT */}
        <div className="chat-container">
          {messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.type}`}>
              {msg.text}
            </div>
          ))}

          {loading && <p className="loading">⏳ Thinking...</p>}
        </div>

        {/* ⌨️ INPUT */}
        <ChatBox onSend={askQuestion} disabled={loading} />

      </div>
    </div>
  );
}