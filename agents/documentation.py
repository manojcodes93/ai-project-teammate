from utils.helpers import get_ai_response
from utils.prompts import DOCUMENTATION_PROMPT


def run_documentation(project_idea, files=None):
    """Generate documentation for the completed project."""
    user_input = f"Project Idea: {project_idea}"
    if files:
        user_input += "\n\nGenerated files:\n" + "\n".join(
            f"--- {name} ---\n{content[:2000]}" for name, content in files.items()
        )

    return get_ai_response(
        system_prompt=DOCUMENTATION_PROMPT,
        user_input=user_input,
    )
