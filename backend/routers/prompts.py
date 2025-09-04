from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict

from generation.prompt_builder import build_prompts_for_panels

router = APIRouter()


class PromptsRequest(BaseModel):
    panels: List[Dict]
    style: str = "manga"


@router.post("/prompts")
def prompts(request: PromptsRequest):
    prompts = build_prompts_for_panels(request.panels, request.style)
    return prompts


