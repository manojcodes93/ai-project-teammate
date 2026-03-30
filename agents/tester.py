from utils.prompts import TESTER_PROMPT
from utils.helpers import get_ai_response

def run_product_manager(project_idea):
    response = get_ai_response(
        system_prompt = TESTER_PROMPT,
        user_input = f"Project Idea: {project_idea}"
    )
    return response
