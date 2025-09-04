"""Character extraction utilities.

This module provides a simple rule-based extractor. For production,
replace or augment with an NER model (spaCy, transformers).
"""
from typing import List
import re


def extract_characters(text: str, max_characters: int = 8) -> List[str]:
    """Extract character names by looking for Titlecase words and simple patterns.

    Args:
        text: The story text.
        max_characters: Max number of characters to return.

    Returns:
        List of unique character name guesses.
    """
    if not text:
        return []
    # Simple heuristic: look for capitalized words (including multi-word names)
    candidates = re.findall(r"\b([A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20})?)\b", text)
    unique = []
    for name in candidates:
        if name.lower() in (n.lower() for n in unique):
            continue
        # filter out common sentence-start words
        if len(name) <= 2:
            continue
        unique.append(name)
        if len(unique) >= max_characters:
            break
    return unique


