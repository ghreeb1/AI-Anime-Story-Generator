# AI Story-to-Comic Generator 📖🎨

Prototype full-stack project that transforms **short stories** into **comic pages** using NLP and image generation.  

---

## 🚀 Features
- **FastAPI Backend**  
  Endpoints for:
  - Story parsing  
  - Prompt generation  
  - Image generation (Stable Diffusion)  
  - Comic assembly  

- **Streamlit Frontend**  
  Prototype UI for entering a story and viewing generated comics.  

- **NLP Utilities** (`nlp/`)  
  For text parsing, scene extraction, and dialogue handling.  

- **Generation Utilities** (`generation/`)  
  For prompt formatting and Stable Diffusion integration.  

---

## ⚡ Quickstart (Development)

1. Clone the repo & install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

2. Start the backend (FastAPI):  
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

3. Start the frontend (Streamlit):  
   ```bash
   streamlit run frontend/streamlit_app.py
   ```

---

## 🎨 Stable Diffusion Configuration

To enable **GPU image generation** with Hugging Face `diffusers`, set the following environment variables:

- `SD_MODEL_ID` → Model ID (default: `runwayml/stable-diffusion-v1-5`)  
- `HF_TOKEN` → (optional) Hugging Face access token (for private models)  
- `SD_OUTPUT_DIR` → Output directory for generated images (default: `output/images`)  

👉 If `diffusers` or CUDA are not available, the app will **fall back to placeholder images** so the UI remains functional.  

Example (Linux/Mac):
```bash
export SD_MODEL_ID="runwayml/stable-diffusion-v1-5"
export HF_TOKEN="your_hf_token_here"
export SD_OUTPUT_DIR="./output/images"
```

---

## 📂 Project Structure
```
AI-Story-to-Comic-Generator/
│── backend/              # FastAPI backend
│   └── main.py
│── frontend/             # Streamlit frontend prototype
│   └── streamlit_app.py
│── nlp/                  # NLP utilities (story parsing, dialogues, etc.)
│── generation/           # Prompt + image generation utils
│── output/               # Generated images & comics
│── requirements.txt
│── README.md
```

---

## 🛠 Tech Stack
- **Backend** → FastAPI  
- **Frontend** → Streamlit  
- **Image Generation** → Stable Diffusion (`diffusers`)  
- **NLP** → spaCy / custom utilities  
- **Assembly** → PIL / custom scripts  

---

## 📌 Notes
- This is a **prototype**, not production-ready.  
- Works even without GPU (uses placeholder images).  

---

## 🔮 Future Work / Roadmap
- [ ] Add **automatic speech bubbles** with text overlay.  
- [ ] Support for **multi-panel comic pages**.  
- [ ] Improve **text clarity inside images**.  
- [ ] Fine-tuned Stable Diffusion models for **comic / manga style**.  
- [ ] Export final comics as **PDF / CBZ formats**.  
- [ ] Enhance frontend with **drag-and-drop editing**.  
- [ ] Multi-language story input support.  

## 📧 Contact

**Developer:**  
Mohamed Khaled

**Email:**  
qq11gharipqq11@gmail.com

**Project Link:**  
[https://github.com/ghreeb1/Eye_Disease.Classification](https://github.com/ghreeb1/Eye_Disease.Classification)

**LinkedIn:**  
[https://linkedin.com/in/mohamed-khaled-3a9021263](https://linkedin.com/in/mohamed-khaled-3a9021263)
