from generation.prompt_builder import build_prompts_for_panels


def test_build_prompts_for_panels():
    panels = [{"scene": "A quiet room", "dialogues": [("", "Hello")]}]
    prompts = build_prompts_for_panels(panels, style="manga")
    assert isinstance(prompts, list)
    assert "positive_prompt" in prompts[0]


