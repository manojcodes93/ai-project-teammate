from utils.prompts import REVIEWER_PROMPT
from utils.helpers import get_ai_response


def run_reviewer(code):
    response = get_ai_response(
        system_prompt=REVIEWER_PROMPT,
        user_input=f"Review the following code:\n\n{code}",
    )
    return response
