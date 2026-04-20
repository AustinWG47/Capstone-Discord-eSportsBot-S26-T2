import requests
import json
import random

OLLAMA_URL = "http://localhost:11434/api/chat"


# -------------------------------------
# PROMPT
# -------------------------------------

def generate_shuffle_prompt(team_names):
    return f"""
You are a strict JSON generator.

Return ONLY a shuffled version of this list.

Rules:
- Output valid JSON only
- No explanations
- No markdown
- No comments
- No extra text
- Do NOT modify any team names
- Do NOT add or remove teams
- Return the same teams in a different order

Example format:
["team1","team3","team2"]

Teams:
{json.dumps(team_names)}
"""


# -------------------------------------
# CLEAN MODEL OUTPUT
# -------------------------------------

def clean_ai_response(result: str):

    # remove markdown blocks
    if "```" in result:
        parts = result.split("```")
        for part in parts:
            if "[" in part:
                result = part
                break

    start = result.find("[")
    end = result.rfind("]") + 1

    if start != -1 and end != -1:
        return result[start:end]

    return result.strip()


# -------------------------------------
# CALL OLLAMA
# -------------------------------------

def call_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral",
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": "Return ONLY valid JSON arrays."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "options": {
                "temperature": 0
            }
        }
    )

    data = response.json()
    return data["message"]["content"]


# -------------------------------------
# SAFE AI SHUFFLE
# -------------------------------------

def shuffle_teams_with_ai(team_names):

    prompt = generate_shuffle_prompt(team_names)
    result = call_ollama(prompt)

    result = clean_ai_response(result)

    try:

        shuffled = json.loads(result)

        # validation checks
        if (
            isinstance(shuffled, list)
            and len(shuffled) == len(team_names)
            and set(shuffled) == set(team_names)
        ):
            return shuffled

    except Exception:
        pass

    # fallback if AI fails
    random.shuffle(team_names)
    return team_names


# -------------------------------------
# BUILD BRACKET (DETERMINISTIC)
# -------------------------------------

def build_bracket(team_objects, ordered_team_names):

    team_lookup = {t["team_name"]: t for t in team_objects}

    matches = []
    match_id = 1

    for i in range(0, len(ordered_team_names), 2):

        team1_name = ordered_team_names[i]
        team2_name = None

        if i + 1 < len(ordered_team_names):
            team2_name = ordered_team_names[i + 1]

        matches.append({
            "match_id": f"match_{match_id}",
            "team1": team_lookup[team1_name],
            "team2": team_lookup[team2_name] if team2_name else None
        })

        match_id += 1

    return {"matches": matches}


# -------------------------------------
# MAIN FUNCTION
# -------------------------------------

def generate_bracket_with_ai(teams):

    if not teams or len(teams) < 2:
        return {"error": "Not enough teams"}

    # extract names
    team_names = [t["team_name"] for t in teams]

    # AI shuffle
    shuffled_names = shuffle_teams_with_ai(team_names)

    # deterministic bracket build
    bracket = build_bracket(teams, shuffled_names)

    return bracket