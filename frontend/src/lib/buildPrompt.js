import { CHARACTERS } from "./characters";

export function buildPrompt(sceneText, characterKey) {
  const character = CHARACTERS[characterKey];

  return `
${character.prompt},

Scene:
${sceneText},

anime webtoon panel,
cinematic composition,
dramatic shadows,
high detail
`;
}