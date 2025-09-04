# AI Story-to-Comic Generator

Prototype full-stack project to transform short stories into comic pages.

Components:
- FastAPI backend with endpoints for parsing, prompt generation, image generation, and assembly.
- Streamlit frontend prototype at `frontend/streamlit_app.py`.
- NLP utilities in `nlp/` and generation utilities in `generation/`.

Quickstart (dev):
1. pip install -r requirements.txt
2. Start backend: `uvicorn backend.main:app --reload --port 8000`
3. Start frontend: `streamlit run frontend/streamlit_app.py`

Stable Diffusion configuration
- To enable GPU generation with Hugging Face `diffusers`, set environment variables:
  - `SD_MODEL_ID` - model id (default: `runwayml/stable-diffusion-v1-5`)
  - `HF_TOKEN` - (optional) Hugging Face access token for private models
  - `SD_OUTPUT_DIR` - output directory for generated images (default: `output/images`)

If `diffusers` or CUDA are unavailable, the app will fall back to placeholder images so the UI remains functional.


