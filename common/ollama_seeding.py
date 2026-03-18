import requests
import json
import random

OLLAMA_URL = "http://localhost:11434/api/chat"


def generate_prompt(players, team_size):
    return f"""
You are generating randomized tournament teams.

Rules:
- Create balanced teams as best as possible
- Each team must have {team_size} players
- Use each player exactly once
- Return ONLY valid JSON

Format:
{{
  "teams": [
    {{
      "team_name": "Team 1",
      "players": ["player1", "player2"]
    }}
  ]
}}

Players:
{players}
"""


def call_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral",
            "messages": [
                {"role": "system", "content": "You generate tournament teams."},
                {"role": "user", "content": prompt}
            ],
            "options": {
                "temperature": 0.7  # slightly random for demo
            },
            "stream": False
        }
    )

    data = response.json()
    return data["message"]["content"]


def generate_random_seed(players, team_size):

    # Shuffle first for randomness (important for demo)
    random.shuffle(players)

    prompt = generate_prompt(players, team_size)

    result = call_ollama(prompt)

    try:
        return json.loads(result)
    except:
        return {
            "error": "Invalid JSON from model",
            "raw": result
        }


# Quick test (run this file directly)
if __name__ == "__main__":

    players = [
        "Alice", "Bob", "Charlie", "David",
        "Eve", "Frank", "Grace", "Hannah"
    ]

    teams = generate_random_seed(players, 2)

    print(json.dumps(teams, indent=2))