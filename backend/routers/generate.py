from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

from generation.sd_generator import generate_images
import base64
from fastapi import BackgroundTasks

from nlp.scene_splitter import split_into_scenes
from nlp.dialogue_detector import detect_dialogue_lines
from nlp.character_extractor import extract_characters
from generation.prompt_builder import build_prompts_for_panels

# We keep the expensive pipeline load inside generation.sd_generator which
# will attempt to create a diffusers pipeline on first use. To avoid blocking
# the request loop for long loads, in production you might pre-warm the
# pipeline on startup. For this prototype we call generate_images directly.

router = APIRouter()


class GenerateRequest(BaseModel):
    prompts: List[Dict]
    negative_prompt: str = None


@router.post("/generate")
def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    # Generate image files (or fallback placeholders)
    prompts = request.prompts
    # If a global negative_prompt is provided, apply it to all prompts
    if request.negative_prompt:
        for p in prompts:
            p["negative_prompt"] = request.negative_prompt
    # Allow frontend to suggest width/height/steps/guidance; otherwise use defaults
    # (These will be honored by generation.sd_generator)
    paths = generate_images(prompts)

    # Read files and return base64-encoded PNGs so clients don't need file access
    encoded_images = []
    for p in paths:
        try:
            with open(p, "rb") as f:
                b = f.read()
            encoded = base64.b64encode(b).decode("utf-8")
            encoded_images.append({"b64": encoded, "filename": p})
        except Exception:
            # If a file can't be read, skip it
            continue

    return {"images": encoded_images}


@router.post("/generate/prewarm")
def prewarm():
    """Trigger pipeline initialization and return status so clients can
    explicitly pre-warm the Stable Diffusion pipeline.
    """
    from generation.sd_generator import _init_pipeline

    pipe = _init_pipeline()
    if pipe is None:
        return {"status": "failed", "message": "Pipeline not available (check server logs)."}
    return {"status": "ok", "message": "Pipeline initialized"}


class ComicRequest(BaseModel):
    story: str
    style: str = "manga"  # manga, american, webtoon
    negative_prompt: str = None
    generation: dict = None
    overlay_bubbles: bool = True


@router.post("/generate/comic")
def generate_comic(request: ComicRequest):
    # 1. Split story into scenes/panels
    scenes = split_into_scenes(request.story)
    # 2. Extract characters for consistency
    characters = extract_characters(request.story)
    # 3. For each scene, extract dialogue
    panels = []
    for scene in scenes:
        dialogues = detect_dialogue_lines(scene)
        panels.append({
            "scene": scene,
            "dialogues": dialogues,
            "characters": characters
        })
    # 4. Build prompts for each panel
    prompts = build_prompts_for_panels(panels, style=request.style)
    # If a global negative_prompt is provided, apply it to all prompts
    if request.negative_prompt:
        for p in prompts:
            p["negative_prompt"] = request.negative_prompt

    # If generation parameters are provided (width/height/steps/guidance), attach to each prompt
    gen = request.generation or {}
    if gen:
        for p in prompts:
            # Only copy allowed keys
            for k in ("width", "height", "steps", "guidance_scale", "seed"):
                if k in gen:
                    p[k] = gen[k]
    # 5. Generate images
    image_paths = generate_images(prompts)
    # 6. Optionally overlay speech bubbles with all dialogue lines

    def draw_speech_bubbles(image_path, dialogues):
        from PIL import Image, ImageDraw, ImageFont

        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except Exception:
            font = ImageFont.load_default()
        # Bubble layout: stack from bottom, one per dialogue
        margin = 10
        bubble_height = 50
        width, height = img.size
        y = height - margin - bubble_height * len(dialogues)
        for speaker, line in dialogues:
            bubble_w = width - 2 * margin
            bubble_h = bubble_height - 10
            x = margin
            # Draw rounded rectangle (bubble)
            draw.rounded_rectangle([x, y, x + bubble_w, y + bubble_h], radius=20, fill=(255, 255, 255, 220), outline=(0, 0, 0, 255), width=2)  # noqa: E501
            # Draw tail (simple triangle)
            tail_x = x + bubble_w // 2
            tail_y = y + bubble_h
            draw.polygon([(tail_x - 10, tail_y), (tail_x + 10, tail_y), (tail_x, tail_y + 15)], fill=(255, 255, 255, 220), outline=(0, 0, 0, 255))
            # Draw speaker name
            if speaker:
                draw.text((x + 15, y + 5), f"{speaker}: ", font=font, fill=(0, 0, 0, 255))
                text_x = x + 15 + draw.textlength(f"{speaker}: ", font=font)
            else:
                text_x = x + 15
            # Draw dialogue line
            draw.text((text_x, y + 5), line, font=font, fill=(0, 0, 0, 255))
            y += bubble_height
        # Save as PNG (overwrite original)
        img = img.convert("RGB")
        img.save(image_path)
    # Overlay bubbles for each panel only if requested (overlay_bubbles True)
    if request.overlay_bubbles:
        for idx, (path, panel) in enumerate(zip(image_paths, panels)):
            if panel.get("dialogues"):
                draw_speech_bubbles(path, panel["dialogues"])
    # 7. Encode images for response
    output_images = []
    for idx, path in enumerate(image_paths):
        with open(path, "rb") as f:
            b = f.read()
        b64 = base64.b64encode(b).decode("utf-8")
        output_images.append({"b64": b64, "filename": f"panel_{idx}.png"})
    # 8. Collect dialogues for each panel
    dialogues = [panel.get("dialogues", []) for panel in panels]
    return {"images": output_images, "dialogues": dialogues}


