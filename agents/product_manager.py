from utils.prompts import PRODUCT_MANAGER_PROMPT
from utils.helpers import get_ai_response

def run_product_manager(project_idea):
    response = get_ai_response(
        system_prompt = PRODUCT_MANAGER_PROMPT,
        user_input = f"Project Idea: {project_idea}"
    )
    return response
