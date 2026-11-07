import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/api";


function ResumeProject() {
  const [projects, setProjects] = useState([]);
  const [message, setMessage] = useState("");

  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects/");
      setProjects(res.data.projects || []);
    } catch {
      setMessage("Failed to load projects. Make sure backend is running.");
    }
  };

  const deleteProject = async (projectId) => {
    const confirmDelete = window.confirm(
      "Delete this project and all generated files?"
    );

    if (!confirmDelete) return;

    try {
      const res = await api.delete(`/projects/${projectId}`);
      setMessage(res.data.message);
      fetchProjects();
    } catch {
      setMessage("Delete failed.");
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  return (
    <main className="px-8 py-10 text-white">
      <section className="max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold mb-3">Resume Project</h1>

        <p className="text-gray-400 mb-8">
          Continue an existing story or delete it after your work is done.
        </p>

        {message && (
          <div className="mb-6 bg-purple-500/10 border border-purple-500/30 rounded-xl p-4">
            {message}
          </div>
        )}

        <div className="space-y-4">
          {projects.length === 0 ? (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              No projects found.
            </div>
          ) : (
            projects.map((project) => (
              <div
                key={project.project_id}
                className="bg-white/5 border border-white/10 rounded-2xl p-6 flex justify-between items-center"
              >
                <div>
                  <h2 className="text-2xl font-bold">
                    {project.story_title}
                  </h2>

                  <p className="text-gray-400">
                    Project ID: {project.project_id}
                  </p>

                  <p className="text-gray-400">
                    Last Scene: {project.last_scene_number}
                  </p>
                </div>

                <div className="flex gap-3">
                  <Link
                    to={`/editor/${project.project_id}`}
                    className="bg-purple-600 hover:bg-purple-700 px-5 py-3 rounded-xl font-semibold"
                  >
                    Resume
                  </Link>

                  <button
                    onClick={() => deleteProject(project.project_id)}
                    className="bg-red-600 hover:bg-red-700 px-5 py-3 rounded-xl font-semibold"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

export default ResumeProject;