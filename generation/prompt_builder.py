"""Prompt builder for image generation.

Creates positive and negative prompts from panel text and style.
"""
from typing import Dict, List
import random


def build_prompts_for_panels(panels: List[Dict], style: str = "manga") -> List[Dict]:
    """Build image generation prompts for each panel.

    Args:
        panels: List of panel dicts containing scene text and dialogues.
        style: One of 'manga', 'american', 'webtoon'.

    Returns:
        List of dicts: {positive_prompt, negative_prompt, seed}
    """
    style_map = {
        "manga": "black and white manga panel, screentones, expressive characters",
        "american": "comic book style, bold inks, dynamic poses, vibrant colors",
        "webtoon": "vertical webtoon, clean colors, soft shading, modern style",
    }
    base_style = style_map.get(style, style_map["manga"])
    prompts = []
    for panel in panels:
        text = panel.get("scene", "")
        dialogues = panel.get("dialogues", [])
        # Incorporate first line of dialogue to focus composition
        focus = ""
        if dialogues:
            focus = dialogues[0][1]
        positive = f"{base_style}, {focus}, {text[:120]}"
        negative = "text, watermark, logo, signature, blurry, lowres, artifacts, bad quality, cropped, error, jpeg artifacts, signature, username, letters, numbers"
        prompts.append({"positive_prompt": positive, "negative_prompt": negative, "seed": random.randint(0, 2**32 - 1)})
    return prompts


