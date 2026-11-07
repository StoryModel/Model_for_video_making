import React from "react";

function SceneCard({ scene }) {
  return (
    <div className="bg-black/30 border border-white/10 rounded-xl p-4">
      <h3 className="font-bold mb-2">
        Scene {scene?.scene_number || "?"}
      </h3>

      <p className="text-gray-300 text-sm mb-3">
        {scene?.scene_text || "No scene text available."}
      </p>

      {scene?.image_prompt && (
        <p className="text-purple-300 text-xs">
          Prompt: {scene.image_prompt}
        </p>
      )}
    </div>
  );
}

export default SceneCard;