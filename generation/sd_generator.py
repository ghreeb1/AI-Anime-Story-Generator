"""Stable Diffusion generator.

This module attempts to use Hugging Face `diffusers` with a CUDA GPU when
available. It lazily initializes a pipeline on first use and supports
configuration via environment variables:

- `SD_MODEL_ID` (default: "runwayml/stable-diffusion-v1-5")
- `HF_TOKEN` (optional Hugging Face token for private models)
- `SD_OUTPUT_DIR` (default: "output/images")

If the heavy dependencies or GPU are unavailable, it falls back to the
lightweight placeholder generator that writes a simple illustrative PNG so the
rest of the app can continue working in constrained environments.
"""
from typing import List, Dict, Optional
import os
import logging
from PIL import Image, ImageDraw, ImageFont

_LOGGER = logging.getLogger(__name__)

# Lazy-loaded pipeline stored here after successful initialization
_PIPE = None


def _placeholder_generate(prompts: List[Dict], output_dir: str) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)
    paths: List[str] = []
    for i, p in enumerate(prompts):
        img = Image.new("RGB", (512, 512), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        text = f"Panel{i}\n{p.get('positive_prompt', '')[:150]}"
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None
        draw.multiline_text((10, 10), text, fill=(10, 10, 10), font=font)
        path = os.path.join(output_dir, f"panel_{i}.png")
        img.save(path)
        paths.append(path)
    return paths


def _init_pipeline(model_id: Optional[str] = None, hf_token: Optional[str] = None):
    """Attempt to initialize and return a Stable Diffusion pipeline.

    Returns None on any import/runtime failure (caller should fallback).
    """
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    try:
        import torch
        from diffusers import StableDiffusionPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model_id = model_id or os.environ.get("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")

        pipeline_kwargs = {}
        if device == "cuda":
            # Use fp16 for faster inference on CUDA if available
            from torch import float16

            pipeline_kwargs["torch_dtype"] = float16

        # Support passing an auth token for private models
        if hf_token:
            try:
                # newer diffusers versions accept "use_auth_token" or "token"
                _PIPE = StableDiffusionPipeline.from_pretrained(model_id, use_auth_token=hf_token, **pipeline_kwargs)
            except TypeError:
                _PIPE = StableDiffusionPipeline.from_pretrained(model_id, token=hf_token, **pipeline_kwargs)
        else:
            _PIPE = StableDiffusionPipeline.from_pretrained(model_id, **pipeline_kwargs)

        _PIPE = _PIPE.to(device)
        _LOGGER.info("Initialized Stable Diffusion pipeline on %s using model %s", device, model_id)
        return _PIPE
    except Exception as exc:  # noqa: BLE001 - broad fallback for optional dependency
        _LOGGER.warning("Could not initialize Stable Diffusion pipeline: %s", exc)
        _PIPE = None
        return None


def generate_images(prompts: List[Dict], output_dir: str = None) -> List[str]:
    """Generate images using Stable Diffusion when available.

    Falls back to `_placeholder_generate` on any error so callers always get
    a set of image paths to work with.
    """
    output_dir = output_dir or os.environ.get("SD_OUTPUT_DIR", "output/images")
    os.makedirs(output_dir, exist_ok=True)

    # Try to initialize pipeline lazily using environment configuration
    hf_token = os.environ.get("HF_TOKEN")
    model_id = os.environ.get("SD_MODEL_ID")
    pipe = _init_pipeline(model_id=model_id, hf_token=hf_token)

    if pipe is None:
        return _placeholder_generate(prompts, output_dir)

    try:
        import torch

        # Determine device from the loaded pipeline
        device = next(pipe.parameters()).device if hasattr(pipe, "parameters") else ("cuda" if torch.cuda.is_available() else "cpu")

        paths: List[str] = []
        for i, p in enumerate(prompts):
            prompt_text = p.get("positive_prompt", "")
            negative_prompt = p.get("negative_prompt", "")

            # Use generator for deterministic seeds when provided
            seed = p.get("seed")
            generator = None
            if seed is not None:
                generator = torch.Generator(device=device).manual_seed(int(seed))

            # Respect caller-provided parameters but fall back to sane defaults
            steps = int(p.get("steps", os.environ.get("SD_STEPS", 28)))
            guidance_scale = float(p.get("guidance_scale", os.environ.get("SD_GUIDANCE", 7.5)))
            width = int(p.get("width", os.environ.get("SD_WIDTH", 512)))
            height = int(p.get("height", os.environ.get("SD_HEIGHT", 512)))

            # Enforce common model-friendly constraints: multiples of 8
            def _round_multiple(value, base=8):
                return max(base, int(round(value / base) * base))

            width = _round_multiple(width, 8)
            height = _round_multiple(height, 8)

            # Call pipeline with explicit parameters where supported
            # Use autocast on CUDA for fp16 pipelines
            try:
                from torch import autocast
                if device == "cuda":
                    with autocast(device_type="cuda"):
                        result = pipe(prompt_text, negative_prompt=negative_prompt, height=height, width=width, num_inference_steps=steps, guidance_scale=guidance_scale, generator=generator)
                else:
                    result = pipe(prompt_text, negative_prompt=negative_prompt, height=height, width=width, num_inference_steps=steps, guidance_scale=guidance_scale, generator=generator)
            except Exception:
                # Fallback to a simpler call if the pipeline has different signature
                result = pipe(prompt_text, negative_prompt=negative_prompt, num_inference_steps=steps, generator=generator)

            image = result.images[0]
            path = os.path.join(output_dir, f"panel_{i}.png")
            image.save(path)
            paths.append(path)
        return paths
    except Exception as exc:
        _LOGGER.exception("Stable Diffusion generation failed, falling back to placeholder: %s", exc)
        return _placeholder_generate(prompts, output_dir)
