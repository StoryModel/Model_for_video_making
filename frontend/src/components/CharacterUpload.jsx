import React from "react";

function BackgroundUpload({
  backgroundFiles,
  setBackgroundFiles,
  onUpload,
  loading,
}) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
      <h2 className="text-2xl font-bold mb-3">Put Background Image</h2>

      <p className="text-gray-400 mb-4">
        Upload one or more background images. Each image will be reused evenly
        across the scenes and animated with gentle camera zoom movement.
      </p>

      <input
        type="file"
        accept="image/*"
        multiple
        onChange={(e) => setBackgroundFiles(Array.from(e.target.files || []))}
        className="w-full text-gray-300 mb-4"
      />

      {backgroundFiles?.length > 0 && (
        <p className="text-sm text-green-400 mb-4">
          Selected {backgroundFiles.length} background image(s)
        </p>
      )}

      <button
        onClick={onUpload}
        disabled={loading}
        className="bg-purple-600 hover:bg-purple-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-50"
      >
        {loading ? "Uploading..." : "Upload Background Images"}
      </button>
    </div>
  );
}

export default BackgroundUpload;
