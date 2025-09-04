from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from backend.routers import parse as parse_router
from backend.routers import prompts as prompts_router
from backend.routers import generate as generate_router
from backend.routers import assemble as assemble_router


app = FastAPI(title="AI Story-to-Comic Generator API")

# Enable CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (CSS/JS)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    html_path = os.path.join(frontend_dir, "comic_generator.html")
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    # Patch static file paths
    html = html.replace('href="comic_generator.css"', 'href="/static/comic_generator.css"')
    html = html.replace('src="comic_generator.js"', 'src="/static/comic_generator.js"')
    return HTMLResponse(content=html)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(parse_router.router)
app.include_router(prompts_router.router)
app.include_router(generate_router.router)
app.include_router(assemble_router.router)


@app.on_event("startup")
def prewarm_sd_pipeline():
    """Attempt to initialize the Stable Diffusion pipeline in a background
    thread on server startup so the first request is fast and any errors are
    logged at startup.
    """
    try:
        import threading
        from generation.sd_generator import _init_pipeline

        def _worker():
            # Call with environment defaults; this will log success/failure.
            _init_pipeline()

        t = threading.Thread(target=_worker, name="sd_prewarm", daemon=True)
        t.start()
    except Exception:
        # Don't fail startup if pre-warm can't be scheduled
        pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="localhost", port=8000, reload=True)


