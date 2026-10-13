"""Single source of truth for AI teammate metadata.

Keeping the teammate list, descriptions and colors in one place avoids the
drift that happens when cards, selectors and history styling each keep their
own copy.
"""

AGENTS = [
    {
        "key": "Product Manager",
        "desc": "Defines requirements, features and roadmap",
        "selector_desc": "Defines requirements and roadmap",
        "color": "#238636",
        "selectable": True,
    },
    {
        "key": "Developer",
        "desc": "Writes and reviews code and architecture",
        "selector_desc": "Writes and reviews code",
        "color": "#1f6feb",
        "selectable": True,
    },
    {
        "key": "Tester",
        "desc": "Conducts automated and manual testing",
        "selector_desc": "Conducts automated and manual testing",
        "color": "#8957e5",
        "selectable": True,
    },
    {
        "key": "Code Reviewer",
        "desc": "Reviews code for bugs and best practices",
        "selector_desc": "Reviews code for bugs and best practices",
        "color": "#db6d28",
        "selectable": False,
    },
    {
        "key": "Documentation",
        "desc": "Creates user and developer documentation",
        "selector_desc": "Creates user and developer docs",
        "color": "#2aa198",
        "selectable": True,
    },
]

# Code Reviewer has its own dedicated page, so it is not offered here.
SELECTABLE_AGENTS = [agent for agent in AGENTS if agent["selectable"]]


def agent_color(key, default="#238636"):
    """Return the accent color for a teammate key."""
    for agent in AGENTS:
        if agent["key"] == key:
            return agent["color"]
    return default
