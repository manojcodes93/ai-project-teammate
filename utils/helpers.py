import os
from groq import Groq
import sqlite3
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_ai_response(system_prompt, user_input, model = "llama-3.3-70b-versatile"):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\n{user_input}"}
            ],
            model = model,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"
    

## Database

def init_db():
    conn = sqlite3.connect("data/history.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_idea TEXT NOT NULL,
            teammate TEXT NOT NULL,
            output TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_to_history(project_idea, teammate, output):
    conn = sqlite3.connect("data/history.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (project_idea, teammate, output)
        VALUES (?, ?, ?)
    """, (project_idea, teammate, output))

    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect("data/history.db")
    cursor = conn.cursor()
    cursor.execute("""
        select id, project_idea, teammate, output, created_at
        from history
        order by created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_history_item(item_id):
    conn = sqlite3.connect("data/history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def clear_all_history():
    conn = sqlite3.connect("data/history.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()