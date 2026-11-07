import React from "react";
import { Link } from "react-router-dom";

function Home() {
  return (
    <main className="px-8 py-20 text-white">
      <section className="max-w-5xl mx-auto text-center">
        <p className="text-purple-400 font-semibold mb-4">
          Local AI Manhwa Video Generator
        </p>

        <h1 className="text-5xl font-bold mb-6 leading-tight">
          Create Long Manhwa Recap Videos With AI
        </h1>

        <p className="text-gray-300 text-lg mb-10 max-w-3xl mx-auto">
          Upload background images, add your story script or PDF, generate images, voice, subtitles,
          and export MP4 videos in 720p or 360p.
        </p>

        <div className="flex justify-center gap-4">
          <Link
            to="/create"
            className="bg-purple-600 hover:bg-purple-700 px-8 py-3 rounded-xl font-semibold"
          >
            Create New Project
          </Link>

          <Link
            to="/resume"
            className="bg-white/10 hover:bg-white/20 px-8 py-3 rounded-xl font-semibold"
          >
            Resume Project
          </Link>
        </div>
      </section>
    </main>
  );
}

export default Home;