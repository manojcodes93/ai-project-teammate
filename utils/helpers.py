import os
import streamlit as st
from groq import Groq
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

os.makedirs("data", exist_ok=True)

def get_client():
    api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
    
    if not api_key:
        raise ValueError("GROQ_API_KEY not found. Please add it in Streamlit Secrets.")
    
    return Groq(api_key=api_key)

def get_ai_response(system_prompt, user_input, model="llama-3.3-70b-versatile"):
    try:
        client = get_client()

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": f"{system_prompt}\n\n{user_input}"}
            ],
            model=model,
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
    local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect("data/history.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO history (project_idea, teammate, output, created_at)
            VALUES (?, ?, ?, ?)
        """, (project_idea, teammate, output, local_time))
        conn.commit()

def get_history():
    with sqlite3.connect("data/history.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, project_idea, teammate, output, created_at
            FROM history
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()

def delete_history_item(item_id):
    with sqlite3.connect("data/history.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE id = ?", (item_id,))
        conn.commit()

def clear_all_history():
    with sqlite3.connect("data/history.db", timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")
        conn.commit()
