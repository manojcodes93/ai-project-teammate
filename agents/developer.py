from utils.helpers import get_ai_response
from utils.prompts import DEVELOPER_PROMPT


def run_developer(project_idea, feedback=None, existing_code=None):
    """Generate or repair project code.

    Backwards compatible: callers may still call ``run_developer(project_idea)``.
    """
    user_input = f"Project Idea / Requirements: {project_idea}"

    if existing_code:
        user_input += (
            "\n\nExisting generated files:\n"
            + "\n".join(
                f"--- {name} ---\n{content}" for name, content in existing_code.items()
            )
        )

    if feedback:
        user_input += (
            "\n\nCorrection feedback (you must modify the code, not just explain):\n"
            + feedback
        )

    return get_ai_response(
        system_prompt=DEVELOPER_PROMPT,
        user_input=user_input,
    )
