import React from "react";

function StoryUpload({
  storyText,
  setStoryText,
  storyFile,
  setStoryFile,
  onSaveText,
  onUploadFile,
  loadingText,
  loadingFile,
}) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 lg:col-span-2">
      <h2 className="text-2xl font-bold mb-3">Story Script</h2>

      <p className="text-gray-400 mb-4">
        Write your story script manually or upload a PDF, TXT, or DOCX file.
      </p>

      <textarea
        value={storyText}
        onChange={(e) => setStoryText(e.target.value)}
        placeholder="Write or paste your story script here..."
        rows="8"
        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white mb-4"
      />

      <div className="flex flex-wrap gap-4 items-center">
        <button
          onClick={onSaveText}
          disabled={loadingText}
          className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-50"
        >
          {loadingText ? "Saving..." : "Save Written Story"}
        </button>

        <input
          type="file"
          accept=".pdf,.txt,.docx"
          onChange={(e) => setStoryFile(e.target.files[0])}
          className="text-gray-300"
        />

        <button
          onClick={onUploadFile}
          disabled={loadingFile}
          className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-50"
        >
          {loadingFile ? "Uploading..." : "Upload Story File"}
        </button>
      </div>

      {storyFile && (
        <p className="text-sm text-green-400 mt-4">
          Selected: {storyFile.name}
        </p>
      )}
    </div>
  );
}

export default StoryUpload;