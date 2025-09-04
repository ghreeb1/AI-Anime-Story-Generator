"""Detect dialogue lines in a scene."""
from typing import List, Tuple


def detect_dialogue_lines(scene: str) -> List[Tuple[str, str]]:
    """Detect dialogue in a scene and return tuples of (speaker, line).

    This is a heuristic-based detector: looks for lines in quotes and
    optional "Name: speech" formats.
    """
    if not scene:
        return []
    lines = [line.strip() for line in scene.splitlines() if line.strip()]
    dialogues = []
    for line in lines:
        # Name: speech
        if ":" in line and len(line.split(":", 1)[0].split()) <= 3:
            speaker, speech = line.split(":", 1)
            dialogues.append((speaker.strip(), speech.strip().strip('"')))
            continue
        # "speech"
        if line.startswith('"') and '"' in line[1:]:
            end = line.find('"', 1)
            speech = line[1:end]
            dialogues.append(("", speech.strip()))
            continue
    return dialogues


