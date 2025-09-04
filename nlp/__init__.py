"""Package initializer for `nlp` utilities.

This file makes the `nlp` directory a proper Python package so modules
like `nlp.scene_splitter` can be imported from other parts of the project.
Expose the commonly-used functions at the package level for convenience.
"""
from .scene_splitter import split_into_scenes
from .character_extractor import extract_characters
from .dialogue_detector import detect_dialogue_lines

__all__ = [
    "split_into_scenes",
    "extract_characters",
    "detect_dialogue_lines",
]


