import streamlit as st
import requests
import sys
from pathlib import Path

# Ensure project root is on sys.path so sibling packages (like `nlp`) are
# importable when running `streamlit run frontend/streamlit_app.py`.
project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from nlp.scene_splitter import split_into_scenes
from nlp.character_extractor import extract_characters
from nlp.dialogue_detector import detect_dialogue_lines


st.title("AI Story-to-Comic Generator (Prototype)")

with st.form("story_form"):
    title = st.text_input("Title")
    story = st.text_area("Story", height=300)
    style = st.selectbox("Style", ["manga", "american", "webtoon"])
    submitted = st.form_submit_button("Generate Comic")

if submitted and story.strip():
    with st.spinner("Parsing story..."):
        try:
            resp = requests.post("http://localhost:8000/parse", json={"title": title, "text": story}, timeout=3.0)
            data = resp.json()
        except Exception:
            # Fallback to local parsing if backend is unreachable
            scenes = split_into_scenes(story)
            characters = extract_characters(story)
            panels = []
            for idx, scene in enumerate(scenes):
                dialogues = detect_dialogue_lines(scene)
                panels.append({"id": idx, "scene": scene, "dialogues": dialogues})
            data = {"language": "en", "characters": characters, "panels": panels}

        st.write("**Detected characters:**")
        st.write(data.get("characters", []))
        st.write("**Panels preview:**")
        # Build prompts for the panels and request generated images from backend
        from generation.prompt_builder import build_prompts_for_panels

        prompts = build_prompts_for_panels(data.get("panels", []), style)
        # Ensure each prompt contains a `positive_prompt` key expected by backend
        normalized_prompts = []
        for p in prompts:
            if isinstance(p, dict):
                if "positive_prompt" not in p and "prompt" in p:
                    p["positive_prompt"] = p.pop("prompt")
                elif "positive_prompt" not in p:
                    p["positive_prompt"] = str(p)
                normalized_prompts.append(p)
            else:
                normalized_prompts.append({"positive_prompt": str(p)})
        try:
            gen_resp = requests.post("http://localhost:8000/generate", json={"prompts": normalized_prompts}, timeout=30.0)
            gen_data = gen_resp.json()
            images = gen_data.get("images", [])

            for img_obj, panel in zip(images, data.get("panels", [])):
                b64 = img_obj.get("b64")
                if not b64:
                    st.write(panel.get("scene")[:300])
                    continue
                try:
                    import base64

                    img_bytes = base64.b64decode(b64)
                    st.image(img_bytes, caption=panel.get("scene")[:120])
                except Exception:
                    st.write(panel.get("scene")[:300])
        except Exception:
            # Fallback: display panel text if backend generate failed
            for p in data.get("panels", []):
                st.write(p.get("scene")[:300])


