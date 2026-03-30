from utils.helpers import get_ai_response
from utils.prompts import DEVELOPER_PROMPT

def run_developer(project_idea):
    response = get_ai_response(
        system_prompt = DEVELOPER_PROMPT,
        user_input = f"Project Idea: {project_idea}" 
    )
    return response