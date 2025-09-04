from pydantic import BaseModel
from typing import List


class ParseRequest(BaseModel):
    title: str
    text: str


class ParseResponse(BaseModel):
    language: str
    characters: List[str]
    panels: List[dict]


