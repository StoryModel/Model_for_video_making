import React from "react";
import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar.jsx";
import Home from "./pages/Home.jsx";
import CreateProject from "./pages/CreateProject.jsx";
import Editor from "./pages/Editor.jsx";
import ResumeProject from "./pages/ResumeProject.jsx";
import DownloadPage from "./pages/DownloadPage.jsx";

function App() {
  return (
    <div className="min-h-screen bg-[#070711] text-white">
      <Navbar />

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/create" element={<CreateProject />} />
        <Route path="/editor/:projectId" element={<Editor />} />
        <Route path="/resume" element={<ResumeProject />} />
        <Route path="/download/:projectId" element={<DownloadPage />} />
      </Routes>
    </div>
  );
}

export default App;