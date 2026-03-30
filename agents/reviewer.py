from utils.prompts import REVIEWER_PROMPT
from utils.helpers import get_ai_response

def run_reviewer(project_idea):
    response = get_ai_response(
        system_prompt = REVIEWER_PROMPT,
        user_input = f"Project Idea: {project_idea}"
    )
    return response
