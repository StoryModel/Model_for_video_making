export async function generateStableDiffusionImage(prompt, seed) {
  const response = await fetch(
    "http://127.0.0.1:7860/sdapi/v1/txt2img",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        prompt,
        negative_prompt:
          "blurry, ugly, low quality, bad anatomy",

        steps: 20,
        width: 512,
        height: 768,
        cfg_scale: 7,
        sampler_name: "DPM++ 2M",
        seed,
      }),
    }
  );

  return await response.json();
}