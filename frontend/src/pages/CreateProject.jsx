import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";


function CreateProject() {
  const navigate = useNavigate();

  const [storyTitle, setStoryTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const createProject = async (e) => {
    e.preventDefault();

    if (!storyTitle.trim()) {
      setMessage("Story title is required.");
      return;
    }

    try {
      setLoading(true);
      setMessage("");

      const response = await api.post("/projects/create", {
        story_title: storyTitle,
      });

      if (response.data.success) {
        navigate(`/editor/${response.data.project_id}`);
      } else {
        setMessage(response.data.message || "Project creation failed.");
      }
    } catch (error) {
      setMessage("Backend connection failed. Make sure FastAPI is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="px-8 py-12 text-white">
      <section className="max-w-3xl mx-auto bg-white/5 border border-white/10 rounded-2xl p-8">
        <h1 className="text-4xl font-bold mb-3">Create New Project</h1>

        <p className="text-gray-300 mb-8">
          Start by creating a local project. Your files will be saved inside the
          backend outputs folder.
        </p>

        <form onSubmit={createProject} className="space-y-5">
          <div>
            <label className="block mb-2 font-semibold">Story Title *</label>
            <input
              type="text"
              value={storyTitle}
              onChange={(e) => setStoryTitle(e.target.value)}
              placeholder="Example: Weakest Boy Becomes Monster Emperor"
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white"
            />
          </div>

          {message && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 rounded-xl p-3">
              {message}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-purple-600 hover:bg-purple-700 rounded-xl py-3 font-bold disabled:opacity-50"
          >
            {loading ? "Creating..." : "Create Project"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default CreateProject;