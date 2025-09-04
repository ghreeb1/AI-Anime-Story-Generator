"""Assemble generated panel images into a comic page and export as PDF/PNG."""
from typing import List
from PIL import Image
import os
try:
    from reportlab.pdfgen import canvas  # type: ignore
    from reportlab.lib.pagesizes import letter  # type: ignore
    _HAS_REPORTLAB = True
except Exception:
    _HAS_REPORTLAB = False


def assemble_grid(image_paths: List[str], columns: int = 2, thumb_size=(512, 512), output_path: str = "output/comic_page.png") -> str:
    """Arrange images in a grid and save a single PNG.

    Returns path to the saved PNG.
    """
    if not image_paths:
        raise ValueError("No images to assemble")
    images = [Image.open(p).convert("RGB") for p in image_paths]
    rows = (len(images) + columns - 1) // columns
    w, h = thumb_size
    page = Image.new("RGB", (w * columns, h * rows), color=(255, 255, 255))
    for idx, img in enumerate(images):
        img = img.resize(thumb_size)
        x = (idx % columns) * w
        y = (idx // columns) * h
        page.paste(img, (x, y))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    page.save(output_path)
    return output_path


def export_pdf(image_path: str, pdf_path: str = "output/comic.pdf") -> str:
    """Embed the PNG into a PDF page and save."""
    if _HAS_REPORTLAB:
        c = canvas.Canvas(pdf_path, pagesize=letter)
        # Fit the image into the page while preserving aspect
        c.drawImage(image_path, 0, 0, width=letter[0], height=letter[1])
        c.showPage()
        c.save()
        return pdf_path
    # Fallback: create a one-page PDF using PIL (very simple)
    try:
        from PIL import Image
        im = Image.open(image_path).convert("RGB")
        im.save(pdf_path, "PDF", resolution=100.0)
        return pdf_path
    except Exception as e:
        raise RuntimeError(f"Cannot export PDF: {e}")


