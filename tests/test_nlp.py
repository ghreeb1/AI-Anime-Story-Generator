from nlp.scene_splitter import split_into_scenes
from nlp.character_extractor import extract_characters


def test_split_into_scenes():
    text = """Scene one.

Scene two has more text.
"""
    scenes = split_into_scenes(text)
    assert len(scenes) == 2


def test_extract_characters():
    text = "Alice went to see Bob. Then Charlie arrived."
    chars = extract_characters(text)
    assert "Alice" in chars
    assert "Bob" in chars or "Charlie" in chars


