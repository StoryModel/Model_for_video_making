import React from "react";

function VideoPreview({ videoUrl }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <h2 className="text-2xl font-bold mb-4">Video Preview</h2>

      {videoUrl ? (
        <video
          src={videoUrl}
          controls
          className="w-full rounded-xl bg-black"
        />
      ) : (
        <div className="w-full h-64 bg-black/50 rounded-xl flex items-center justify-center text-gray-400">
          No preview available yet.
        </div>
      )}
    </div>
  );
}

export default VideoPreview;