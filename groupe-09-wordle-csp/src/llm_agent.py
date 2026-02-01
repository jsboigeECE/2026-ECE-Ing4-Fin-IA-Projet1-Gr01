import json
import re
from typing import Optional

import ollama

from csp_solver import solve_wordle_csp


# ----------------------------
# Dictionary loader
# ----------------------------
def load_dictionary(filename: str):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip().upper() for line in f if len(line.strip()) == 5]
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return []


# ----------------------------
# Normalization
# ----------------------------
def _normalize_guess(s: str) -> Optional[str]:
    if not isinstance(s, str):
        return None
    s = s.strip().upper()
    if len(s) != 5:
        return None
    if any(not ("A" <= ch <= "Z") for ch in s):
        return None
    return s


def _normalize_feedback(s: str) -> Optional[str]:
    if not isinstance(s, str):
        return None
    s = s.strip().upper()
    if len(s) != 5:
        return None
    if any(c not in "VJG" for c in s):
        return None
    return s


# Direct input accepted: "ORATE GVVJG" or "ORATE->GVVJG" or "ORATE -> GVVJG"
_DIRECT = re.compile(r"^\s*([A-Za-z]{5})\s*(?:->\s*)?([VvJjGg]{5})\s*$")


# ----------------------------
# LLM extraction (fallback)
# ----------------------------
def extract_attempt_from_text(user_text: str) -> Optional[dict]:
    """
    Ask the LLM to extract ONE Wordle attempt (guess + V/J/G feedback) from free text.
    Returns {"guess": "...", "feedback": "..."} or None if extraction fails.
    """
    response = ollama.chat(
        model="llama3.1",
        messages=[{
            "role": "user",
            "content": (
                "You are a Wordle assistant.\n"
                "Task: extract EXACTLY ONE Wordle attempt from the user's text.\n\n"
                "You MUST return ONLY a tool call to extract_wordle_attempt.\n"
                "Rules:\n"
                "- guess: a 5-letter ENGLISH word (A-Z)\n"
                "- feedback: a 5-character string using ONLY V, J, G\n"
                "  V=green, J=yellow, G=gray\n"
                "- Do NOT invent data: if guess or feedback is missing/unclear, return guess=\"\" and feedback=\"\".\n\n"
                f"USER TEXT:\n{user_text}"
            )
        }],
        tools=[{
            "type": "function",
            "function": {
                "name": "extract_wordle_attempt",
                "description": "Extract one Wordle attempt (guess + V/J/G feedback)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "guess": {"type": "string"},
                        "feedback": {"type": "string"}
                    },
                    "required": ["guess", "feedback"],
                    "additionalProperties": False
                }
            }
        }],
    )

    msg = response.get("message", {}) or {}
    tool_calls = msg.get("tool_calls") or []
    if not tool_calls:
        return None

    args = tool_calls[0]["function"]["arguments"]
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            return None

    if not isinstance(args, dict):
        return None

    guess = _normalize_guess(args.get("guess", ""))
    feedback = _normalize_feedback(args.get("feedback", ""))

    if not guess or not feedback:
        return None

    return {"guess": guess, "feedback": feedback}


# ----------------------------
# Full agent
# ----------------------------
MAX_CANDIDATES_TO_LLM = 40


def interroger_agent_wordle(prompt_utilisateur: str, dictionary_words, attempts: list):
    """
    prompt_utilisateur: raw user input
    dictionary_words: DICTIONARY (list of 5-letter words)
    attempts: mutable list [(guess, feedback), ...] kept across turns
    """

    # 1) Direct parsing (no LLM needed)
    m = _DIRECT.match(prompt_utilisateur or "")
    if m:
        guess = m.group(1).upper()
        feedback = m.group(2).upper()
    else:
        # 2) LLM fallback for free-text inputs
        extracted = extract_attempt_from_text(prompt_utilisateur)
        if not extracted:
            return (
                "Could not extract a valid attempt.\n"
                "Expected format: 'ORATE GVVJG' or 'ORATE -> GVVJG' (V=green, J=yellow, G=gray)."
            )
        guess = extracted["guess"]
        feedback = extracted["feedback"]

    # 3) Update history
    attempts.append((guess, feedback))

    # 4) CSP solve (attempts-based)
    possible = solve_wordle_csp(dictionary_words, attempts)
    if not possible:
        return (
            "No solution matches the current constraints.\n"
            f"Last attempt: {guess} -> {feedback}\n"
            f"History: {attempts}"
        )

    # 5) Limit candidates sent to the LLM
    candidates_for_llm = possible[:]
    if len(candidates_for_llm) > MAX_CANDIDATES_TO_LLM:
        candidates_for_llm = sorted(candidates_for_llm, key=lambda w: len(set(w)), reverse=True)[:MAX_CANDIDATES_TO_LLM]

    # 6) LLM ranking
    prompt_final = f"""
You are an expert Wordle solver.

You are given a list of valid 5-letter ENGLISH words.
You MUST choose words ONLY from this list.
It is strictly forbidden to invent or modify any word.

List of possible words:
{candidates_for_llm}

Return STRICTLY:
Chosen word: <WORD>
Priority ranking:
1. <WORD>
2. <WORD>
3. <WORD>
"""

    final_response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt_final}],
    )
    content = final_response["message"]["content"]

    shown = ", ".join(possible[:30]) + ("..." if len(possible) > 30 else "")
    note = ""
    if len(possible) > MAX_CANDIDATES_TO_LLM:
        note = f"\n(Note: CSP found {len(possible)} words; only {MAX_CANDIDATES_TO_LLM} were sent to the LLM.)\n"

    return (
        f"ADDED ATTEMPT: {guess} -> {feedback}\n"
        f"POSSIBLE WORDS ({len(possible)}):\n{shown}\n"
        f"{note}\n"
        f"LLM DECISION:\n{content}"
    )