import React from "react";
import { API_BASE_URL } from "../api/api";

function DownloadButtons({ projectId }) {
  return (
    <div className="flex flex-wrap justify-center gap-4">
      <a
        href={`${API_BASE_URL}/download/${projectId}/720p`}
        className="bg-green-600 hover:bg-green-700 px-8 py-3 rounded-xl font-semibold"
      >
        Download 720p MP4
      </a>

      <a
        href={`${API_BASE_URL}/download/${projectId}/360p`}
        className="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-xl font-semibold"
      >
        Download 360p MP4
      </a>
    </div>
  );
}

export default DownloadButtons;