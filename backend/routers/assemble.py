from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from generation.assembler import assemble_grid, export_pdf

router = APIRouter()


class AssembleRequest(BaseModel):
    images: List[str]
    columns: int = 2


@router.post("/assemble")
def assemble(request: AssembleRequest):
    png = assemble_grid(request.images, columns=request.columns)
    pdf = export_pdf(png)
    return {"png": png, "pdf": pdf}


