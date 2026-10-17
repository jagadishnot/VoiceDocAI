import { useState } from "react";
import "../styles/pages.css";

export default function ChatBox({ onSend, disabled = false }) {
  const [query, setQuery] = useState("");
  const [listening, setListening] = useState(false);

  // ==========================
  // 🚀 SEND MESSAGE
  // ==========================
  const handleSend = () => {
    if (!query.trim() || disabled) return;

    onSend(query);
    setQuery("");
  };

  // ==========================
  // ⌨️ ENTER KEY
  // ==========================
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  // ==========================
  // 🎤 VOICE INPUT
  // ==========================
  const startListening = () => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Speech recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";

    recognition.start();
    setListening(true);

    recognition.onresult = (event) => {
      const voiceText = event.results[0][0].transcript;

      setQuery(voiceText);     // 🔥 put text in input
      setListening(false);
    };

    recognition.onerror = () => {
      setListening(false);
    };
  };

  return (
    <div className="chatbox glass">

      {/* 🎤 MIC BUTTON */}
      <button
        onClick={startListening}
        disabled={disabled}
        className={`mic-btn ${listening ? "listening" : ""}`}
        title="Speak"
      >
        {listening ? "🎙️" : "🎤"}
      </button>

      {/* ⌨️ INPUT */}
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="💬 Ask something..."
        disabled={disabled}
        className="chat-input"
      />

      {/* 🚀 SEND */}
      <button
        onClick={handleSend}
        disabled={disabled || !query.trim()}
        className="send-btn"
      >
        🚀
      </button>

    </div>
  );
}