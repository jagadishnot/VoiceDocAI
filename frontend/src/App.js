import React, { useState, useRef, useEffect } from "react";
import ExcelPage from "./ExcelPage";
import "./App.css";

function App() {
  const [page, setPage] = useState("chat");
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);

  const recognitionRef = useRef(null);
  const chatEndRef = useRef(null);
  const currentAudioRef = useRef(null);

  // =============================
  // Auto Scroll
  // =============================
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // =============================
  // Speech Recognition
  // =============================
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      setQuestion(event.results[0][0].transcript);
    };

    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
  }, []);

  const startListening = () => {
    const recognition = recognitionRef.current;
    if (!recognition) return alert("Speech not supported");

    if (listening) {
      recognition.stop();
      setListening(false);
    } else {
      recognition.start();
      setListening(true);
    }
  };

  // =============================
  // Upload Document
  // =============================
  const uploadFile = async () => {
    if (!file) return alert("Select file first");

    const formData = new FormData();
    formData.append("file", file);

    await fetch("http://127.0.0.1:8000/upload", {
      method: "POST",
      body: formData,
    });

    alert("Document uploaded 🚀");
  };

  // =============================
  // Stop Audio
  // =============================
  const stopAudio = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
  };

  // =============================
  // Play Audio with Smart Retry
  // =============================
  const playAudioWithRetry = (url) => {
    if (!soundEnabled) return;

    let attempts = 0;
    const maxAttempts = 20;

    const tryPlay = async () => {
      try {
        const res = await fetch(url);

        if (res.status === 200) {
          stopAudio();
          const audio = new Audio(url);
          currentAudioRef.current = audio;
          await audio.play();
        } else {
          throw new Error();
        }
      } catch {
        if (attempts < maxAttempts) {
          attempts++;
          setTimeout(tryPlay, 1000);
        }
      }
    };

    tryPlay();
  };

  // =============================
  // STREAM MESSAGE (PRO VERSION)
  // =============================
  const sendMessage = async () => {
    if (!question.trim()) return;

    stopAudio();

    const userText = question;
    setQuestion("");
    setLoading(true);

    setMessages((prev) => [...prev, { sender: "user", text: userText }]);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userText }),
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let fullText = "";
      let audioFile = null;

      // Add empty bot message first
      setMessages((prev) => [...prev, { sender: "bot", text: "" }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });

        if (chunk.includes("[AUDIO_FILE]")) {
          const parts = chunk.split("[AUDIO_FILE]");
          fullText += parts[0];
          audioFile = parts[1]?.trim();
        } else {
          fullText += chunk;
        }

        // SAFE state update (no ESLint warning)
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;

          updated[lastIndex] = {
            ...updated[lastIndex],
            text: fullText,
          };

          return updated;
        });
      }

      setLoading(false);

      // Play audio after streaming complete
      if (soundEnabled && audioFile) {
        const audioUrl = `http://127.0.0.1:8000/audio/${audioFile}`;
        playAudioWithRetry(audioUrl);
      }

    } catch (err) {
      console.error(err);
      alert("Backend error ❌");
      setLoading(false);
    }
  };

  // =============================
  // Sound Toggle
  // =============================
  const toggleSound = () => {
    if (soundEnabled) stopAudio();
    setSoundEnabled(!soundEnabled);
  };

  // =============================
  // Excel Page Switch
  // =============================
  if (page === "excel") {
    return (
      <>
        <button className="nav-btn" onClick={() => setPage("chat")}>
          ← Back to Chat
        </button>
        <ExcelPage />
      </>
    );
  }

  return (
    <div className="app">
      <div className="header">
        🤖 VoiceDoc AI
        <div>
          <button className="sound-btn" onClick={toggleSound}>
            {soundEnabled ? "🔊 Sound ON" : "🔇 Sound OFF"}
          </button>
          <button className="nav-btn" onClick={() => setPage("excel")}>
            Excel Analytics
          </button>
        </div>
      </div>

      <div className="upload-section">
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button className="btn" onClick={uploadFile}>
          Upload Document
        </button>
      </div>

      <div className="chat-container">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}

        {loading && <div className="typing">AI is typing...</div>}
        <div ref={chatEndRef}></div>
      </div>

      <div className="input-container">
        <textarea
          placeholder="Ask anything..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              sendMessage();
            }
          }}
        />

        <button
          className={`mic-btn ${listening ? "listening" : ""}`}
          onClick={startListening}
        >
          {listening ? "⏹" : "🎤"}
        </button>

        <button className="btn send-btn" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

export default App;