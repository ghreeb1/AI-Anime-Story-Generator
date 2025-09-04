from fastapi import APIRouter
from pydantic import BaseModel

from nlp.scene_splitter import split_into_scenes
from nlp.character_extractor import extract_characters
from nlp.dialogue_detector import detect_dialogue_lines

router = APIRouter()


class ParseRequest(BaseModel):
    title: str
    text: str


@router.post("/parse")
def parse(request: ParseRequest):
    scenes = split_into_scenes(request.text)
    characters = extract_characters(request.text)
    panels = []
    for idx, scene in enumerate(scenes):
        dialogues = detect_dialogue_lines(scene)
        panels.append({"id": idx, "scene": scene, "dialogues": dialogues})
    return {"language": "en", "characters": characters, "panels": panels}
