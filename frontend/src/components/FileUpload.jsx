import { useState } from "react";
import "../styles/pages.css";

export default function FileUpload({ onUpload, disabled = false }) {
  const [file, setFile] = useState(null);

  const handleFileChange = (f) => {
    if (!f) return;
    setFile(f);
  };

  const handleUpload = () => {
    if (!file) return;
    onUpload(file);
    setFile(null);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (disabled) return;

    const droppedFile = e.dataTransfer.files[0];
    handleFileChange(droppedFile);
  };

  return (
    <div
      className="upload-box"
      onDragOver={(e) => e.preventDefault()}
      onDrop={handleDrop}
    >
      {/* 📂 Input */}
      <input
        type="file"
        onChange={(e) => handleFileChange(e.target.files[0])}
        disabled={disabled}
      />

      {/* 📄 File Name */}
      {file && <p className="file-name">📄 {file.name}</p>}

      {/* 🚀 Upload Button */}
      <button
        onClick={handleUpload}
        disabled={!file || disabled}
        className="upload-btn"
      >
        Upload File
      </button>
    </div>
  );
}