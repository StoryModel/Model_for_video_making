import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api, { API_BASE_URL } from "../api/api";

function Editor() {
  const { projectId } = useParams();

  const [backgroundFiles, setBackgroundFiles] = useState([]);
  const [storyText, setStoryText] = useState("");
  const [storyFile, setStoryFile] = useState(null);

  const [message, setMessage] = useState("");
  const [projectTitle, setProjectTitle] = useState("");
  const [loadingStep, setLoadingStep] = useState("");

  const isBusy = loadingStep;

  const [progress, setProgress] = useState(0);

  const [scenes, setScenes] = useState([]);
  const [activeBox, setActiveBox] = useState("images");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [editingIndex, setEditingIndex] = useState(null);

  const [editedSceneText, setEditedSceneText] = useState("");
  const [editedImagePrompt, setEditedImagePrompt] = useState("");
  const [changeImageFile, setChangeImageFile] = useState(null);
  const [savingChanges, setSavingChanges] = useState(false);

  // NEW: Change All Pictures states
  const [showChangeAllPictures, setShowChangeAllPictures] = useState(false);
  const [changeAllSaving, setChangeAllSaving] = useState(false);
  const [pictureRanges, setPictureRanges] = useState([
    {
      pictureName: "",
      fromScene: "",
      toScene: "",
      imageFile: null,
    },
  ]);

  const [imagesDone, setImagesDone] = useState(false);
  const [subtitleDone, setSubtitleDone] = useState(false);
  const [voiceDone, setVoiceDone] = useState(false);
  const [videoDone, setVideoDone] = useState(false);

  const getFileName = (path) => {
    if (!path) return "";
    return path.split("\\").pop().split("/").pop();
  };

  const imageUrl = (scene) => {
    const path = scene.subtitled_image_path || scene.image_path;
    const fileName = getFileName(path);
    const normalizedPath = (path || "").replaceAll("\\", "/");

    let folder = "images";
    if (normalizedPath.includes("/subtitle_images/")) folder = "subtitle_images";
    else if (normalizedPath.includes("/backgrounds/")) folder = "backgrounds";

    return `${API_BASE_URL}/outputs/project_${projectId}/${folder}/${fileName}`;
  };

  const audioUrl = (scene) => {
    const fileName = getFileName(scene.audio_path);
    return `${API_BASE_URL}/outputs/project_${projectId}/audio/${fileName}`;
  };

  const videoUrl720 = `${API_BASE_URL}/outputs/project_${projectId}/videos/final_720p.mp4`;

  const fetchProject = async () => {
    try {
      const res = await api.get(`/projects/${projectId}`);
      if (res.data.success) {
        setProjectTitle(res.data.project.story_title);
      }
    } catch {
      setProjectTitle("");
    }
  };

  const fetchScenes = async () => {
    const res = await api.get(`/story/scenes/${projectId}`);
    if (res.data.success) {
      setScenes(res.data.scenes || []);
    }
  };

  useEffect(() => {
    fetchProject();
    fetchScenes();
  }, [projectId]);

  const fakeProgress = () => {
    setProgress(10);
    setTimeout(() => setProgress(35), 500);
    setTimeout(() => setProgress(65), 1000);
    setTimeout(() => setProgress(90), 1500);
  };

  const ProgressDisplay = () => {
    if (!loadingStep) return null;

    return (
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-300 mb-2">
          <span>Working on: {loadingStep}</span>
          <span>{progress}%</span>
        </div>

        <div className="w-full bg-white/10 h-4 rounded-full overflow-hidden">
          <div
            className="bg-purple-600 h-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    );
  };

  const startEditingCurrentScene = () => {
    if (!currentScene) return;

    setEditingIndex(currentIndex);
    setEditedSceneText(currentScene.scene_text || "");
    setEditedImagePrompt(currentScene.image_prompt || "");
    setChangeImageFile(null);
    setShowChangeAllPictures(false);
  };

  const cancelEditing = () => {
    setEditingIndex(null);
    setEditedSceneText("");
    setEditedImagePrompt("");
    setChangeImageFile(null);
    setShowChangeAllPictures(false);
  };

  const saveSceneEdit = async () => {
    if (!currentScene) return;

    try {
      setSavingChanges(true);

      const formData = new FormData();
      formData.append("scene_number", currentScene.scene_number);
      formData.append("scene_text", editedSceneText);
      formData.append("image_prompt", editedImagePrompt);

      if (changeImageFile) {
        formData.append("image", changeImageFile);
      }

      let endpoint = "";

      if (activeBox === "images") {
        endpoint = `/backgrounds/update-scene/${projectId}`;
      } else if (activeBox === "voice") {
        endpoint = `/voice/update-scene/${projectId}`;
      } else {
        endpoint = `/video/update-subtitle/${projectId}`;
      }

      const res = await api.post(endpoint, formData);

      if (!res.data.success) {
        setMessage(res.data.message || "Save changes failed.");
        return;
      }

      if (res.data.scenes && Array.isArray(res.data.scenes)) {
        setScenes(res.data.scenes);
      } else {
        await fetchScenes();
      }

      setMessage(res.data.message || "Changes saved.");
      cancelEditing();

      if (activeBox === "images") {
        setSubtitleDone(false);
        setVoiceDone(false);
        setVideoDone(false);
      }

      if (activeBox === "voice") {
        setVoiceDone(false);
        setVideoDone(false);
      }
    } catch {
      setMessage("Save changes failed.");
    } finally {
      setSavingChanges(false);
    }
  };

  // NEW: Change All Pictures helpers
  const openChangeAllPictures = () => {
    setShowChangeAllPictures(true);
  };

  const closeChangeAllPictures = () => {
    setShowChangeAllPictures(false);
  };

  const addPictureRange = () => {
    setPictureRanges((prev) => [
      ...prev,
      {
        pictureName: "",
        fromScene: "",
        toScene: "",
        imageFile: null,
      },
    ]);
  };

  const removePictureRange = (index) => {
    setPictureRanges((prev) => {
      if (prev.length === 1) {
        return [
          {
            pictureName: "",
            fromScene: "",
            toScene: "",
            imageFile: null,
          },
        ];
      }

      return prev.filter((_, itemIndex) => itemIndex !== index);
    });
  };

  const updatePictureRange = (index, field, value) => {
    setPictureRanges((prev) =>
      prev.map((item, itemIndex) =>
        itemIndex === index ? { ...item, [field]: value } : item
      )
    );
  };

  const validatePictureRanges = () => {
    if (!pictureRanges.length) {
      return "Add at least one picture range.";
    }

    for (let i = 0; i < pictureRanges.length; i += 1) {
      const range = pictureRanges[i];
      const fromScene = Number(range.fromScene);
      const toScene = Number(range.toScene);

      if (!range.imageFile) {
        return `Select image for Picture No.${i + 1}.`;
      }

      if (!fromScene || !toScene) {
        return `Enter From Scene and To Scene for Picture No.${i + 1}.`;
      }

      if (fromScene < 1 || toScene < 1) {
        return `Scene numbers must start from 1 for Picture No.${i + 1}.`;
      }

      if (fromScene > toScene) {
        return `From Scene cannot be greater than To Scene for Picture No.${i + 1}.`;
      }

      if (scenes.length && toScene > scenes.length) {
        return `To Scene for Picture No.${i + 1} cannot be greater than total scenes (${scenes.length}).`;
      }
    }

    return "";
  };

  const saveChangeAllPictures = async () => {
    const validationMessage = validatePictureRanges();

    if (validationMessage) {
      setMessage(validationMessage);
      return;
    }

    try {
      setChangeAllSaving(true);

      const formData = new FormData();

      const rangesPayload = pictureRanges.map((range, index) => {
        formData.append("images", range.imageFile);

        return {
          picture_name: range.pictureName || range.imageFile.name,
          from_scene: Number(range.fromScene),
          to_scene: Number(range.toScene),
          file_index: index,
        };
      });

      formData.append("ranges", JSON.stringify(rangesPayload));

      /*
        Backend route needed:
        POST /backgrounds/update-many-scenes/:projectId

        Expected FormData:
        - images: multiple image files
        - ranges: JSON string like:
          [
            {
              picture_name: "Picture 1",
              from_scene: 1,
              to_scene: 20,
              file_index: 0
            }
          ]
      */
      const res = await api.post(
        `/backgrounds/update-many-scenes/${projectId}`,
        formData
      );

      if (!res.data.success) {
        setMessage(res.data.message || "Change All Pictures failed.");
        return;
      }

      if (res.data.scenes && Array.isArray(res.data.scenes)) {
        setScenes(res.data.scenes);
      } else {
        await fetchScenes();
      }

      setSubtitleDone(false);
      setVoiceDone(false);
      setVideoDone(false);
      setMessage(res.data.message || "All pictures changed successfully.");
      setShowChangeAllPictures(false);
    } catch {
      setMessage(
        "Change All Pictures failed. Make sure backend route /backgrounds/update-many-scenes/" + projectId + " exists."
      );
    } finally {
      setChangeAllSaving(false);
    }
  };

  const uploadBackgrounds = async () => {
    if (!backgroundFiles.length) {
      setMessage("Upload at least two background images.");
      return;
    }

    if (backgroundFiles.length < 2 || backgroundFiles.length > 5) {
      setMessage("Please select 2 to 5 background images.");
      return;
    }

    const formData = new FormData();
    backgroundFiles.forEach((file) => formData.append("files", file));

    try {
      setLoadingStep("backgrounds");
      fakeProgress();

      const res = await api.post(`/backgrounds/upload/${projectId}`, formData);

      setProgress(100);
      setImagesDone(false);
      setSubtitleDone(false);
      setVoiceDone(false);
      setVideoDone(false);
      setMessage(res.data.message);
    } catch {
      setMessage("Background image upload failed.");
    } finally {
      setLoadingStep("");
    }
  };

  const saveWrittenStory = async () => {
    if (!storyText.trim()) {
      setMessage("Write story text first.");
      return;
    }

    try {
      setLoadingStep("storyText");
      fakeProgress();

      const res = await api.post(`/story/write/${projectId}`, {
        story_text: storyText,
      });

      setProgress(100);
      setMessage(`${res.data.message} Total scenes: ${res.data.total_scenes}`);
      await fetchScenes();

      setImagesDone(false);
      setSubtitleDone(false);
      setVoiceDone(false);
      setVideoDone(false);
    } catch {
      setMessage("Story save failed.");
    } finally {
      setLoadingStep("");
    }
  };

  const uploadStoryFile = async () => {
    if (!storyFile) {
      setMessage("Select PDF, TXT, or DOCX file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", storyFile);

    try {
      setLoadingStep("storyFile");
      fakeProgress();

      const res = await api.post(`/story/upload/${projectId}`, formData);

      setProgress(100);
      setMessage(`${res.data.message} Total scenes: ${res.data.total_scenes}`);
      await fetchScenes();

      setImagesDone(false);
      setSubtitleDone(false);
      setVoiceDone(false);
      setVideoDone(false);
    } catch {
      setMessage("Story file upload failed.");
    } finally {
      setLoadingStep("");
    }
  };

  const generateImages = async () => {
    try {
      setActiveBox("images");
      setLoadingStep("backgroundAssignment");
      fakeProgress();

      const res = await api.post(`/images/generate/${projectId}`);

      setProgress(100);

      if (!res.data.success) {
        setMessage(res.data.message || "Background image assignment failed.");
        return;
      }

      setImagesDone(true);
      setSubtitleDone(false);
      setVoiceDone(false);
      setVideoDone(false);
      setMessage(res.data.message);
      await fetchScenes();
    } catch {
      setMessage("Background image assignment failed.");
    } finally {
      setLoadingStep("");
    }
  };

  const addSubtitlesToImages = async () => {
    try {
      setActiveBox("images");
      setLoadingStep("subtitleImages");
      fakeProgress();

      const res = await api.post(`/video/add-subtitles/${projectId}`);

      setProgress(100);

      if (!res.data.success) {
        setMessage(res.data.message || "Failed to add subtitles to images.");
        return;
      }

      setSubtitleDone(true);
      setVoiceDone(false);
      setVideoDone(false);
      setMessage(res.data.message);
      await fetchScenes();
    } catch {
      setMessage("Failed to add subtitles to images.");
    } finally {
      setLoadingStep("");
    }
  };

  const generateVoice = async () => {
    try {
      setActiveBox("voice");
      setLoadingStep("voice");
      fakeProgress();

      const res = await api.post(`/voice/generate/${projectId}`);

      setProgress(100);

      if (!res.data.success) {
        setMessage(res.data.message || "Voice generation failed.");
        return;
      }

      if (res.data.scenes && Array.isArray(res.data.scenes)) {
        setScenes(res.data.scenes);
      }

      setVoiceDone(true);
      setVideoDone(false);
      setMessage(res.data.message);
      await fetchScenes();
    } catch {
      setMessage("Voice generation failed.");
    } finally {
      setLoadingStep("");
    }
  };

  const buildVideo = async () => {
    try {
      setActiveBox("video");
      setLoadingStep("video");
      fakeProgress();

      const res = await api.post(`/video/build/${projectId}`);

      setProgress(100);

      if (!res.data.success) {
        setVideoDone(false);
        setMessage(
          res.data.error
            ? `${res.data.message} ${res.data.error}`
            : res.data.message
        );
        return;
      }

      setVideoDone(true);
      setMessage(res.data.message);
    } catch {
      setMessage("Video build failed. Make sure FFmpeg is installed.");
    } finally {
      setLoadingStep("");
    }
  };

  const nextItem = () => {
    if (currentIndex < scenes.length - 1) {
      setCurrentIndex(currentIndex + 1);
      cancelEditing();
    }
  };

  const prevItem = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      cancelEditing();
    }
  };

  const currentScene = scenes[currentIndex];
  const isEditingCurrent = editingIndex === currentIndex;

  return (
    <main className="px-8 py-10 text-white">
      <section className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold">Project Editor</h1>
          <p className="text-gray-400">{projectTitle || "Untitled Story"}</p>
        </div>

        {message && (
          <div className="mb-6 bg-purple-500/10 border border-purple-500/30 rounded-xl p-4 text-purple-200">
            {message}
          </div>
        )}

        <ProgressDisplay />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="lg:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6">
            <h2 className="text-2xl font-bold mb-4">1. Put Background Image</h2>

            <p className="text-gray-400 mb-4">
              Upload 2 to 5 background images. They will be assigned in blocks
              across scenes.
            </p>

            <input
              type="file"
              accept="image/*"
              multiple
              onChange={(e) =>
                setBackgroundFiles(Array.from(e.target.files || []))
              }
              className="w-full mb-4"
            />

            {backgroundFiles.length > 0 && (
              <p className="text-sm text-green-400 mb-4">
                Selected {backgroundFiles.length} background image(s)
              </p>
            )}

            <button
              onClick={uploadBackgrounds}
              disabled={isBusy}
              className="bg-purple-600 hover:bg-purple-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
            >
              {loadingStep === "backgrounds"
                ? "Uploading..."
                : "Upload Background Images"}
            </button>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 lg:col-span-2">
            <h2 className="text-2xl font-bold mb-4">2. Story Script</h2>

            <textarea
              value={storyText}
              onChange={(e) => setStoryText(e.target.value)}
              placeholder="Write or paste your story script here..."
              rows="8"
              className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 mb-4"
            />

            <div className="flex flex-wrap gap-4">
              <button
                onClick={saveWrittenStory}
                disabled={isBusy}
                className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
              >
                Save Written Story
              </button>

              <input
                type="file"
                accept=".pdf,.txt,.docx"
                onChange={(e) => setStoryFile(e.target.files[0])}
              />

              <button
                onClick={uploadStoryFile}
                disabled={isBusy}
                className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
              >
                Upload Story File
              </button>
            </div>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 lg:col-span-2">
            <h2 className="text-2xl font-bold mb-4">3. Generate Video</h2>

            <div className="flex flex-wrap gap-4">
              <button
                onClick={generateImages}
                disabled={isBusy || scenes.length === 0}
                className="bg-orange-600 hover:bg-orange-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
              >
                Use Background Images
              </button>

              <button
                onClick={addSubtitlesToImages}
                disabled={!imagesDone || isBusy}
                className="bg-cyan-600 hover:bg-cyan-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
              >
                Add Subtitle to image
              </button>

              <button
                onClick={generateVoice}
                disabled={!subtitleDone || isBusy}
                className="bg-pink-600 hover:bg-pink-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
              >
                Generate Voice
              </button>

              <button
                onClick={buildVideo}
                disabled={!voiceDone || isBusy}
                className="bg-green-600 hover:bg-green-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
              >
                Build MP4
              </button>

              <Link
                to={`/download/${projectId}`}
                className={`px-5 py-3 rounded-xl font-semibold ${
                  videoDone
                    ? "bg-blue-600 hover:bg-blue-700"
                    : "bg-gray-700 pointer-events-none opacity-40"
                }`}
              >
                Go to Download
              </Link>
            </div>
          </div>

          <div className="lg:col-span-2">
            <ProgressDisplay />
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 lg:col-span-2">
            <h2 className="text-2xl font-bold mb-4">Generated Output</h2>

            {!currentScene && activeBox !== "video" && (
              <p className="text-gray-400">Nothing generated yet.</p>
            )}

            {activeBox === "images" && currentScene && (
              <div>
                <div className="flex justify-between mb-4">
                  <button
                    onClick={prevItem}
                    className="bg-white/10 px-4 py-2 rounded-lg"
                  >
                    ← Previous
                  </button>

                  <span>
                    {currentScene.subtitled_image_path
                      ? "Subtitle Image"
                      : "Background"}{" "}
                    {currentIndex + 1} / {scenes.length}
                  </span>

                  <button
                    onClick={nextItem}
                    className="bg-white/10 px-4 py-2 rounded-lg"
                  >
                    Next →
                  </button>
                </div>

                {(currentScene.subtitled_image_path || currentScene.image_path) && (
                  <img
                    src={imageUrl(currentScene)}
                    alt="Scene background"
                    className="w-full max-h-[500px] object-contain bg-black rounded-xl mb-4"
                  />
                )}

                {isEditingCurrent ? (
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-3 items-center">
                      <button
                        type="button"
                        disabled
                        className="bg-yellow-600 px-5 py-3 rounded-xl font-semibold opacity-80"
                      >
                        Edit
                      </button>

                      <label className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-semibold cursor-pointer">
                        Change Image
                        <input
                          type="file"
                          accept="image/*"
                          hidden
                          onChange={(e) =>
                            setChangeImageFile(e.target.files?.[0] || null)
                          }
                        />
                      </label>

                      {/* NEW BUTTON */}
                      <button
                        type="button"
                        onClick={openChangeAllPictures}
                        disabled={savingChanges || changeAllSaving}
                        className="bg-purple-600 hover:bg-purple-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                      >
                        Change All Pictures
                      </button>

                      <button
                        onClick={saveSceneEdit}
                        disabled={savingChanges || changeAllSaving}
                        className="bg-green-600 hover:bg-green-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                      >
                        {savingChanges ? "Saving..." : "Save Changes"}
                      </button>

                      <button
                        onClick={cancelEditing}
                        disabled={savingChanges || changeAllSaving}
                        className="bg-gray-600 hover:bg-gray-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                      >
                        Cancel
                      </button>
                    </div>

                    {changeImageFile && (
                      <p className="text-sm text-green-400">
                        Selected new image: {changeImageFile.name}
                      </p>
                    )}

                    {/* NEW: Change All Pictures panel */}
                    {showChangeAllPictures && (
                      <div className="bg-black/40 border border-white/10 rounded-2xl p-5 space-y-5">
                        <div>
                          <h3 className="text-xl font-bold">
                            Change All Pictures
                          </h3>
                          <p className="text-sm text-gray-400 mt-1">
                            Select each picture and enter which scene range it
                            should be used for.
                          </p>
                        </div>

                        <div className="space-y-4">
                          {pictureRanges.map((range, index) => (
                            <div
                              key={index}
                              className="bg-white/5 border border-white/10 rounded-xl p-4"
                            >
                              <div className="flex justify-between items-center mb-3">
                                <h4 className="font-semibold">
                                  Picture No.{index + 1}
                                  {range.pictureName
                                    ? ` (${range.pictureName})`
                                    : ""}
                                </h4>

                                <button
                                  type="button"
                                  onClick={() => removePictureRange(index)}
                                  className="bg-red-600 hover:bg-red-700 px-3 py-2 rounded-lg text-sm font-semibold"
                                >
                                  Remove
                                </button>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                                <input
                                  type="text"
                                  value={range.pictureName}
                                  onChange={(e) =>
                                    updatePictureRange(
                                      index,
                                      "pictureName",
                                      e.target.value
                                    )
                                  }
                                  placeholder="Name of picture"
                                  className="bg-black/40 border border-white/10 rounded-xl px-4 py-3"
                                />

                                <input
                                  type="number"
                                  min="1"
                                  max={scenes.length || undefined}
                                  value={range.fromScene}
                                  onChange={(e) =>
                                    updatePictureRange(
                                      index,
                                      "fromScene",
                                      e.target.value
                                    )
                                  }
                                  placeholder="From scene"
                                  className="bg-black/40 border border-white/10 rounded-xl px-4 py-3"
                                />

                                <input
                                  type="number"
                                  min="1"
                                  max={scenes.length || undefined}
                                  value={range.toScene}
                                  onChange={(e) =>
                                    updatePictureRange(
                                      index,
                                      "toScene",
                                      e.target.value
                                    )
                                  }
                                  placeholder="To scene"
                                  className="bg-black/40 border border-white/10 rounded-xl px-4 py-3"
                                />

                                <label className="bg-blue-600 hover:bg-blue-700 px-4 py-3 rounded-xl font-semibold cursor-pointer text-center">
                                  Choose Picture
                                  <input
                                    type="file"
                                    accept="image/*"
                                    hidden
                                    onChange={(e) =>
                                      updatePictureRange(
                                        index,
                                        "imageFile",
                                        e.target.files?.[0] || null
                                      )
                                    }
                                  />
                                </label>
                              </div>

                              {range.imageFile && (
                                <p className="text-sm text-green-400 mt-3">
                                  Selected: {range.imageFile.name}
                                </p>
                              )}

                              <p className="text-xs text-gray-400 mt-2">
                                Example: From scene 1 to scene 25 means this
                                picture will be used from Subtitle Image 1 to 25.
                              </p>
                            </div>
                          ))}
                        </div>

                        <div className="flex flex-wrap gap-3">
                          <button
                            type="button"
                            onClick={addPictureRange}
                            disabled={changeAllSaving}
                            className="bg-blue-600 hover:bg-blue-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                          >
                            Add More Picture
                          </button>

                          <button
                            type="button"
                            onClick={saveChangeAllPictures}
                            disabled={changeAllSaving}
                            className="bg-green-600 hover:bg-green-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                          >
                            {changeAllSaving
                              ? "Saving All Pictures..."
                              : "Save All Pictures"}
                          </button>

                          <button
                            type="button"
                            onClick={closeChangeAllPictures}
                            disabled={changeAllSaving}
                            className="bg-gray-600 hover:bg-gray-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                          >
                            Close
                          </button>
                        </div>
                      </div>
                    )}

                    <textarea
                      value={editedSceneText}
                      onChange={(e) => setEditedSceneText(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded-xl p-4"
                      rows="4"
                      placeholder="Scene text"
                    />

                    <textarea
                      value={editedImagePrompt}
                      onChange={(e) => setEditedImagePrompt(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded-xl p-4"
                      rows="4"
                      placeholder="Image prompt"
                    />
                  </div>
                ) : (
                  <button
                    onClick={startEditingCurrentScene}
                    className="bg-yellow-600 px-5 py-3 rounded-xl font-semibold"
                  >
                    Edit
                  </button>
                )}
              </div>
            )}

            {activeBox === "voice" && currentScene && (
              <div>
                <div className="flex justify-between mb-4">
                  <button
                    onClick={prevItem}
                    className="bg-white/10 px-4 py-2 rounded-lg"
                  >
                    ← Previous
                  </button>

                  <span>
                    Voice {currentIndex + 1} / {scenes.length}
                  </span>

                  <button
                    onClick={nextItem}
                    className="bg-white/10 px-4 py-2 rounded-lg"
                  >
                    Next →
                  </button>
                </div>

                {currentScene.audio_path && (
                  <audio
                    controls
                    src={audioUrl(currentScene)}
                    className="w-full mb-4"
                  />
                )}

                {isEditingCurrent ? (
                  <div className="space-y-4">
                    <div className="flex flex-wrap gap-3 items-center">
                      <button
                        type="button"
                        disabled
                        className="bg-yellow-600 px-5 py-3 rounded-xl font-semibold opacity-80"
                      >
                        Edit
                      </button>

                      <button
                        onClick={saveSceneEdit}
                        disabled={savingChanges}
                        className="bg-green-600 hover:bg-green-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                      >
                        {savingChanges ? "Saving..." : "Save Changes"}
                      </button>

                      <button
                        onClick={cancelEditing}
                        disabled={savingChanges}
                        className="bg-gray-600 hover:bg-gray-700 px-5 py-3 rounded-xl font-semibold disabled:opacity-40"
                      >
                        Cancel
                      </button>
                    </div>

                    <textarea
                      value={editedSceneText}
                      onChange={(e) => setEditedSceneText(e.target.value)}
                      className="w-full bg-black/40 border border-white/10 rounded-xl p-4"
                      rows="4"
                      placeholder="Voice text"
                    />
                  </div>
                ) : (
                  <>
                    <p className="text-gray-300 mb-4">
                      {currentScene.scene_text}
                    </p>

                    <div className="flex gap-4">
                      <button
                        onClick={startEditingCurrentScene}
                        className="bg-yellow-600 px-5 py-3 rounded-xl font-semibold"
                      >
                        Edit
                      </button>

                      <button
                        onClick={() => setActiveBox("images")}
                        className="bg-gray-600 px-5 py-3 rounded-xl font-semibold"
                      >
                        Go Back
                      </button>
                    </div>
                  </>
                )}
              </div>
            )}

            {activeBox === "video" && (
              <div>
                {videoDone ? (
                  <video
                    src={videoUrl720}
                    controls
                    className="w-full rounded-xl bg-black mb-4"
                  />
                ) : (
                  <p className="text-gray-400">Video not built yet.</p>
                )}

                <div className="flex gap-4">
                  <button
                    disabled
                    className="bg-gray-700 px-5 py-3 rounded-xl font-semibold opacity-40"
                  >
                    Edit Disabled
                  </button>

                  <button
                    onClick={() => setActiveBox("voice")}
                    className="bg-gray-600 px-5 py-3 rounded-xl font-semibold"
                  >
                    Go Back
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  );
}

export default Editor;
