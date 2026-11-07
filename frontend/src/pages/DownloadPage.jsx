import React from "react";
import { useParams, Link } from "react-router-dom";
import { API_BASE_URL } from "../api/api";

function DownloadPage() {
  const { projectId } = useParams();

  const download720 = `${API_BASE_URL}/download/${projectId}/720p`;
  const download360 = `${API_BASE_URL}/download/${projectId}/360p`;

  return (
    <main className="px-8 py-16 text-white">
      <section className="max-w-3xl mx-auto bg-white/5 border border-white/10 rounded-2xl p-8 text-center">
        <h1 className="text-4xl font-bold mb-4">Download Video</h1>

        <p className="text-gray-300 mb-8">
          Download your generated MP4 video in 720p or 360p.
        </p>

        <div className="flex justify-center gap-4 mb-8">
          <a
            href={download720}
            className="bg-green-600 hover:bg-green-700 px-8 py-3 rounded-xl font-semibold"
          >
            Download 720p MP4
          </a>

          <a
            href={download360}
            className="bg-blue-600 hover:bg-blue-700 px-8 py-3 rounded-xl font-semibold"
          >
            Download 360p MP4
          </a>
        </div>

        <Link
          to={`/editor/${projectId}`}
          className="text-purple-400 hover:text-purple-300"
        >
          Back to Editor
        </Link>
      </section>
    </main>
  );
}

export default DownloadPage;