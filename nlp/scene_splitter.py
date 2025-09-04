"""Scene splitting utilities for breaking a story into scenes.

This is a lightweight placeholder implementation using simple
heuristics. Replace with a model-based approach for production.
"""
from typing import List


def split_into_scenes(text: str) -> List[str]:
    """Split text into scenes using paragraph breaks and simple heuristics.

    Args:
        text: Full story text.

    Returns:
        List of scene strings.
    """
    if not text:
        return []
    # Normalize newlines to '\n' and split on one or more blank lines as scene separators
    normalized = text.replace('\r\n', '\n').replace('\r', '\n')
    # Use double-newline groups as separators: join lines with '\n' then split on two or more newlines
    import re
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", normalized) if p.strip()]
    # Merge very short paragraphs (empty or single-word) with previous scene
    scenes: List[str] = []
    for p in paragraphs:
        word_count = len(p.split())
        if scenes and word_count <= 1:
            scenes[-1] = scenes[-1] + " " + p
        else:
            scenes.append(p)
    return scenes


