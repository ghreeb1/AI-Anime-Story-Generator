"""Test script to run image generation locally.

Usage:
    python scripts/test_generate.py

This will call `generation.sd_generator.generate_images` with a sample prompt
and write the output image paths and base64 blobs to stdout.
"""
import sys
from pathlib import Path
import json
import base64

# Ensure project root is importable when running from the repo root
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from generation.sd_generator import generate_images


def main():
    prompts = [
        {
            "positive_prompt": "black and white manga panel, screentones, expressive characters, In a quiet futuristic city, a little robot wakes up in a junkyard",
            "negative_prompt": "blurry, lowres, watermark, text",
            "seed": 12345,
        }
    ]

    out_dir = "output/test_images"
    paths = generate_images(prompts, output_dir=out_dir)

    results = []
    for p in paths:
        try:
            with open(p, "rb") as f:
                b = f.read()
            results.append({"filename": p, "b64": base64.b64encode(b).decode("utf-8")})
        except Exception as e:
            results.append({"filename": p, "error": str(e)})

    print(json.dumps(results))


if __name__ == "__main__":
    main()


