import requests
import json
import random

OLLAMA_URL = "http://localhost:11434/api/chat"


def generate_bracket_prompt(teams):
    return f"""
You are a strict JSON generator.

Rules:
- Output ONLY valid JSON
- No explanations
- No markdown
- No extra text
- Use ALL teams exactly once
- Randomize match pairings
- If odd number of teams, one gets a bye (team2 = null)
- Each match should contain the full list of players for each team.
- Do NOT split players across matches.

Format:
{{
  "matches": [
    {{
      "match_id": "match_1",
      "team1": {{...}},
      "team2": {{...}}
    }}
  ]
}}

Teams:
{json.dumps(teams, indent=2)}
"""


def clean_ai_response(result: str):
    if "```" in result:
        parts = result.split("```")
        for part in parts:
            if "{" in part:
                result = part
                break

    start = result.find("{")
    end = result.rfind("}") + 1

    if start != -1 and end != -1:
        return result[start:end]

    return result


def call_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral",
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a strict JSON generator. Output ONLY valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            "options": {
                "temperature": 0.2
            }
        }
    )

    data = response.json()
    return data["message"]["content"]


def generate_bracket_with_ai(teams):
    random.shuffle(teams)

    prompt = generate_bracket_prompt(teams)
    result = call_ollama(prompt)

    result = clean_ai_response(result)

    try:
        return json.loads(result)
    except Exception:
        return {
            "error": "Invalid JSON from model",
            "raw": result
        }
