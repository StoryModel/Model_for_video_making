import re


def clean_story_text(text):
    text = text.replace("\r", "\n")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_into_sentences(text):
    text = clean_story_text(text)

    sentences = re.split(r"(?<=[.!?])\s+", text)

    cleaned = []

    for sentence in sentences:
        sentence = sentence.strip()

        if sentence:
            cleaned.append(sentence)

    return cleaned


def split_long_sentence(sentence, max_words=10):
    words = sentence.split()
    chunks = []

    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i + max_words]).strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def create_scenes_from_story(story_text, max_words_per_scene=10):
    sentences = split_into_sentences(story_text)

    scenes = []
    scene_number = 1

    for sentence in sentences:
        words = sentence.split()

        if len(words) <= max_words_per_scene:
            scene_texts = [sentence]
        else:
            scene_texts = split_long_sentence(
                sentence,
                max_words=max_words_per_scene
            )

        for scene_text in scene_texts:
            scenes.append({
                "scene_number": scene_number,
                "scene_text": scene_text,
                "image_prompt": "",
                "image_path": "",
                "audio_path": "",
                "subtitle_path": "",
                "duration_seconds": 0
            })

            scene_number += 1

    return scenes