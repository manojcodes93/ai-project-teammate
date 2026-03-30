import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(system_prompt, user_input, model = "llama3-8b-8192"):
    try:
        chat_completion = client.chat.completions.create(
            messages = [
                {"role": "System", "content": system_prompt},
                {"role": "User", "content": user_input}
            ],
            model = model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"