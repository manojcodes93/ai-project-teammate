# BuildWithCrew

> Your AI-powered software development team — from planning to deployment.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red)
![Groq](https://img.shields.io/badge/Groq-LLaMA3-green)

---

## Problem Statement

Students, solo developers, and early-stage startup founders face a common challenge — they must simultaneously handle multiple critical roles when building a software project:

- **Product Manager** — deciding what to build and why
- **Developer** — writing and architecting the code
- **Tester** — finding bugs and edge cases
- **Code Reviewer** — improving code quality
- **Technical Writer** — creating documentation

This leads to:
- Poor project planning and unclear requirements
- Weak or missing documentation
- Missed edge cases and untested code
- Poor code quality and technical debt
- Longer development cycles

**There is no single AI system that simulates an entire software development team.**

---

## Solution

**BuildWithCrew** is a multi-agent AI system that simulates a full software development team. Each AI agent is trained with role-specific prompts to behave like a real senior team member — giving production-grade outputs for any project idea.

---

## Features

### AI Teammates
| Agent | Role | Output |
|-------|------|--------|
| Product Manager | Strategic planning | Features, roadmap, user stories, KPIs |
| Developer | Technical architecture | Tech stack, folder structure, API endpoints, code |
| Tester | Quality assurance | Test cases, edge cases, security tests |
| Code Reviewer | Code quality | Bugs, optimizations, best practices, corrected code |
| Documentation | Technical writing | README, installation guide, API docs |

### Project History
- Save every AI generation automatically
- View past outputs anytime
- Delete individual entries or clear all history
- Persistent storage using SQLite

### Code Reviewer
- Paste any code for instant AI review
- 4 structured output sections: Bugs Found, Optimizations, Best Practices, Corrected Code
- Supports Python, JavaScript and any language

### Professional UI
- Dark theme inspired by GitHub
- Clean sidebar navigation
- Responsive layout
- Markdown rendering for formatted outputs

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| AI Model | LLaMA 3.3 70B via Groq API |
| Database | SQLite |
| Styling | Custom CSS |
| Deployment | Streamlit Cloud |

---

## Project Structure
```
ai-project-teammate/
│
├── app.py                          # Main entry point
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not committed)
├── .gitignore                      # Git ignore rules
│
├── agents/
│   ├── product_manager.py          # Product Manager AI agent
│   ├── developer.py                # Developer AI agent
│   ├── tester.py                   # Tester AI agent
│   ├── reviewer.py                 # Code Reviewer AI agent
│   └── documentation.py           # Documentation AI agent
│
├── ui/
│   └── dashboard.py                # All UI components and CSS
│
├── utils/
│   ├── prompts.py                  # All AI system prompts
│   └── helpers.py                  # Groq API helper and database functions
│
├── assets/
│   └── logo.png                    # Application logo
│
├── data/
│   └── history.db                  # SQLite database (auto-created)
│
└── .streamlit/
    └── config.toml                 # Streamlit configuration
```

---

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Git

### Step 1 — Clone the repository
```bash
git clone https://github.com/manojcodes93/ai-project-teammate.git
cd ai-project-teammate
```

### Step 2 — Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Set up environment variables

Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 5 — Run the application
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com | Yes |

---

## Dependencies
```
streamlit
groq
python-dotenv
streamlit-lottie
requests
```

Install all with:
```bash
pip install -r requirements.txt
```

---

## Usage Guide

### AI Teammates Page
1. Enter your project idea in the text input
2. Select an AI teammate from the selector
3. Click **Generate**
4. View the structured AI output
5. All generations are automatically saved to history

### Code Reviewer Page
1. Paste your code in the text area
2. Click **Review Code**
3. View 4 structured sections:
   - **Bugs Found** — identified issues
   - **Optimizations** — performance improvements
   - **Best Practices** — code quality suggestions
   - **Corrected Code** — fixed version of your code

### Project History Page
1. View all past AI generations
2. Click **View Output** to expand any entry
3. Click **Delete** to remove individual entries
4. Click **Clear All History** to reset

---

## AI Agent Details

### Product Manager Agent
Generates enterprise-grade product strategy including:
- Project overview and vision
- Core features with priorities
- Technical and non-functional requirements
- 4-phase development roadmap
- User stories in standard format
- Success metrics and KPIs

### Developer Agent
Generates production-ready technical blueprints including:
- Recommended tech stack with justification
- Complete folder structure
- REST API endpoints with request/response formats
- Database schema design
- Step-by-step implementation guide
- Key code snippets

### Tester Agent
Generates comprehensive testing strategy including:
- Test plan overview
- Functional test cases with steps
- Edge cases and boundary conditions
- Performance and load testing scenarios
- Security testing checklist
- Common bug scenarios

### Code Reviewer Agent
Reviews code and provides:
- Bug detection with line references
- Optimization suggestions
- Best practice violations
- Complete corrected code

### Documentation Agent
Generates complete project documentation including:
- Project overview and badges
- Installation and setup guide
- Environment variables reference
- Usage guide with examples
- API documentation
- Contributing guidelines

---

## Database Schema
```sql
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_idea TEXT NOT NULL,
    teammate TEXT NOT NULL,
    output TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## UI Architecture

The UI is built with Streamlit and custom CSS:

- **Dark theme** — `#0e1117` background, `#161b22` cards
- **Green accent** — `#238636` (GitHub-inspired)
- **Inter font** — clean, professional typography
- **Responsive sidebar** — collapsible navigation
- **Markdown rendering** — formatted AI outputs

---

## Future Enhancements

| Feature | Description | Priority |
|---------|-------------|----------|
| Multi-agent collaboration | PM output feeds into Developer, Developer feeds into Tester | High |
| User Authentication | Login / Signup for users (Google, GitHub, Email) | High |
| Project Dashboard | Users can create and manage multiple projects | High |
| Agent Memory | Agents remember previous decisions in project | High |
| Export to PDF | Download AI outputs as formatted PDF | Medium |
| GitHub integration | Push generated code directly to GitHub repos | Medium |
| Voice interaction | Speak your project idea, hear the output | Low |
| Custom agents | Create your own AI agent with custom prompts | Low |
| Model selection | Switch between different LLM providers | Medium |
| Project templates | Pre-built templates for common project types | Medium |
| Dark / Light Mode | UI personalization | Low |

---

## Author

Built with ❤️ by Manoj Royal

- GitHub: https://github.com/manojcodes93
- LinkedIn: https://www.linkedin.com/in/manoj-royal/

---

## Acknowledgements

- [Groq](https://groq.com) — for the blazing fast LLM inference
- [Meta LLaMA](https://llama.meta.com) — for the open source LLM
- [Streamlit](https://streamlit.io) — for the amazing Python web framework
- [GitHub](https://github.com) — for design inspiration

---

⭐ **Star this repo if you found it helpful!**
