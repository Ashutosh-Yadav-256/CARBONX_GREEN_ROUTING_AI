"""
Image generation using Stable Diffusion.
Includes a fallback placeholder mode for systems without GPU / model.
"""

import logging
import uuid
import json
from pathlib import Path
from config import (
    IMAGE_MODEL_ID,
    IMAGE_INFERENCE_STEPS,
    IMAGE_USE_GPU,
    IMAGE_FALLBACK_MODE,
    GENERATED_IMAGES_DIR,
)

logger = logging.getLogger(__name__)

# ─── Globals ──────────────────────────────────────────────────────────────────
_pipeline = None
_sd_available = False


def _init_pipeline():
    """Try to initialize the Stable Diffusion pipeline."""
    global _pipeline, _sd_available

    if IMAGE_FALLBACK_MODE.lower() == "true":
        logger.info("🎨 Image generator in FALLBACK mode (placeholder images).")
        _sd_available = False
        return

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        device = "cpu"
        dtype = torch.float32

        if IMAGE_USE_GPU != "false":
            if torch.cuda.is_available():
                device = "cuda"
                dtype = torch.float16
                logger.info("🎮 Using CUDA GPU for image generation.")
            elif IMAGE_USE_GPU == "true":
                logger.warning("GPU requested but not available. Using CPU.")

        _pipeline = StableDiffusionPipeline.from_pretrained(
            IMAGE_MODEL_ID,
            torch_dtype=dtype,
        ).to(device)

        _sd_available = True
        logger.info(f"✅ Stable Diffusion loaded — model: {IMAGE_MODEL_ID}")

    except Exception as e:
        _sd_available = False
        logger.warning(f"⚠️  Stable Diffusion not available ({e}). Using fallback.")


def generate_image(prompt: str) -> dict:
    """
    Generate an image from a text prompt.

    Returns:
        dict with 'image_url', 'prompt', and 'method' keys
    """
    global _pipeline, _sd_available

    if _pipeline is None and not _sd_available:
        _init_pipeline()

    image_id = uuid.uuid4().hex[:12]
    filename = f"{image_id}.png"
    filepath = GENERATED_IMAGES_DIR / filename
    image_url = f"/static/generated/{filename}"

    if _sd_available and _pipeline is not None:
        return _generate_with_sd(prompt, filepath, image_url)
    else:
        return _generate_placeholder(prompt, filepath, image_url)


def _generate_with_sd(prompt: str, filepath: Path, image_url: str) -> dict:
    """Generate image using Stable Diffusion."""
    try:
        result = _pipeline(
            prompt,
            num_inference_steps=IMAGE_INFERENCE_STEPS,
            guidance_scale=7.5,
        )
        image = result.images[0]
        image.save(str(filepath))

        logger.info(f"🖼️  Image generated: {filepath}")
        return {
            "image_url": image_url,
            "prompt": prompt,
            "method": "stable_diffusion",
            "message": f"🎨 Image generated using Stable Diffusion!",
        }
    except Exception as e:
        logger.error(f"SD generation failed: {e}")
        return _generate_placeholder(prompt, filepath, image_url)


def _generate_placeholder(prompt: str, filepath: Path, image_url: str) -> dict:
    """Generate a styled placeholder SVG image."""
    # Create a nice SVG placeholder
    svg_content = _create_placeholder_svg(prompt)
    
    # Save as SVG instead
    svg_filename = filepath.stem + ".svg"
    svg_filepath = filepath.parent / svg_filename
    svg_url = f"/static/generated/{svg_filename}"
    
    with open(svg_filepath, "w", encoding="utf-8") as f:
        f.write(svg_content)

    # Also save metadata
    meta_path = filepath.parent / f"{filepath.stem}.json"
    with open(meta_path, "w") as f:
        json.dump({"prompt": prompt, "method": "placeholder"}, f)

    logger.info(f"🖼️  Placeholder image created: {svg_filepath}")
    return {
        "image_url": svg_url,
        "prompt": prompt,
        "method": "placeholder",
        "message": (
            f"🎨 **[Placeholder Mode]** — Stable Diffusion is not loaded.\n\n"
            f"To enable real image generation:\n"
            f"1. Set `IMAGE_FALLBACK_MODE=false` in your environment\n"
            f"2. Ensure you have ~4GB+ disk space for the model\n"
            f"3. A GPU is recommended but not required\n\n"
            f"Prompt: *\"{prompt}\"*"
        ),
    }


def _create_placeholder_svg(prompt: str) -> str:
    """Create a visually appealing placeholder SVG."""
    # Truncate prompt for display
    display_prompt = prompt[:60] + "..." if len(prompt) > 60 else prompt

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0c29"/>
      <stop offset="50%" style="stop-color:#302b63"/>
      <stop offset="100%" style="stop-color:#24243e"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#a855f7"/>
      <stop offset="100%" style="stop-color:#6366f1"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" fill="url(#bg)" rx="16"/>
  <rect x="20" y="20" width="472" height="472" fill="none" stroke="url(#accent)"
        stroke-width="2" stroke-dasharray="8 4" rx="12" opacity="0.5"/>
  <text x="256" y="200" text-anchor="middle" fill="#a855f7"
        font-family="system-ui, sans-serif" font-size="64" opacity="0.8">🎨</text>
  <text x="256" y="260" text-anchor="middle" fill="#e2e8f0"
        font-family="system-ui, sans-serif" font-size="18" font-weight="bold">
    AI Image Generation
  </text>
  <text x="256" y="290" text-anchor="middle" fill="#94a3b8"
        font-family="system-ui, sans-serif" font-size="13">
    Placeholder Mode
  </text>
  <foreignObject x="56" y="320" width="400" height="80">
    <div xmlns="http://www.w3.org/1999/xhtml"
         style="color:#cbd5e1; font-family:system-ui,sans-serif; font-size:12px;
                text-align:center; padding:8px; word-wrap:break-word;">
      "{display_prompt}"
    </div>
  </foreignObject>
</svg>'''
