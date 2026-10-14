from utils.helpers import get_ai_response
from utils.prompts import PRODUCT_MANAGER_PROMPT


def run_product_manager(project_idea, context=None):
    """Produce product requirements for a project request.

    ``context`` is optional extra information (for example resumption notes).
    The original single-argument call signature remains supported.
    """
    user_input = f"Project Idea: {project_idea}"
    if context:
        user_input += f"\n\nAdditional context:\n{context}"

    return get_ai_response(
        system_prompt=PRODUCT_MANAGER_PROMPT,
        user_input=user_input,
    )
