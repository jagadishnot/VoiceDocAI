import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import DocumentQA from "./pages/DocumentQA";
import ExcelAnalyze from "./pages/ExcelAnalyze";
import AudioSummary from "./pages/AudioSummary";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/doc" element={<DocumentQA />} />
        <Route path="/excel" element={<ExcelAnalyze />} />
        <Route path="/audio" element={<AudioSummary />} />
      </Routes>
    </BrowserRouter>
  );
}