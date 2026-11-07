import React from "react";

function ProgressBar({ label = "Progress", progress = 0 }) {
  const safeProgress = Math.min(100, Math.max(0, progress));

  return (
    <div className="w-full">
      <div className="flex justify-between mb-2 text-sm text-gray-300">
        <span>{label}</span>
        <span>{safeProgress}%</span>
      </div>

      <div className="w-full bg-white/10 rounded-full h-3 overflow-hidden">
        <div
          className="bg-purple-600 h-3 rounded-full transition-all"
          style={{ width: `${safeProgress}%` }}
        />
      </div>
    </div>
  );
}

export default ProgressBar;