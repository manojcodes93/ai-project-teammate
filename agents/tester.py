from utils.helpers import get_ai_response
from utils.prompts import TESTER_PROMPT


def run_tester(project_idea, code=None):
    """Produce a testing strategy and edge-case review for a project."""
    user_input = f"Project Idea: {project_idea}"
    if code:
        user_input += "\n\nGenerated code:\n" + code

    return get_ai_response(
        system_prompt=TESTER_PROMPT,
        user_input=user_input,
    )
