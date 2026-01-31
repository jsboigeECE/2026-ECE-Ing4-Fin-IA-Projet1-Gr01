import ollama
from csp_solver import solve_wordle_csp
from collections import Counter

# ----------------------------
# Chargement du dictionnaire
# ----------------------------
def charger_dictionnaire(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            return [ligne.strip().upper() for ligne in f if len(ligne.strip()) == 5]
    except FileNotFoundError:
        print(f"Erreur : Le fichier {nom_fichier} est introuvable.")
        return []

DICTIONNAIRE = charger_dictionnaire("wordle.txt")

# ----------------------------
# Interface CSP
# ----------------------------
def solveur_csp_local(lettres_vertes="", lettres_jaunes="", lettres_grises=""):
    contraintes = []

    if lettres_vertes:
        for item in lettres_vertes.split(','):
            lettre = item[0].upper()
            pos = int(item[1])
            contraintes.append((lettre, pos, 'green'))

    if lettres_jaunes:
        for item in lettres_jaunes.split(','):
            lettre = item[0].upper()
            pos = int(item[1])
            contraintes.append((lettre, pos, 'yellow'))

    if lettres_grises:
        for lettre in lettres_grises.split(','):
            lettre = lettre.strip().upper()
            for i in range(5):
                contraintes.append((lettre, i, 'gray'))

    return solve_wordle_csp(DICTIONNAIRE, contraintes)

# ----------------------------
# Agent Wordle (LLM + CSP)
# ----------------------------
def interroger_agent_wordle(prompt_utilisateur):

    # LLM : extraction des contraintes
    response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt_utilisateur}],
        tools=[{
            "type": "function",
            "function": {
                "name": "solveur_csp_local",
                "description": "Filtre les mots Wordle selon les contraintes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lettres_vertes": {
                            "type": "string",
                            "description": "Format LettrePosition, ex: P0,R3"
                        },
                        "lettres_jaunes": {
                            "type": "string",
                            "description": "Format LettrePosition"
                        },
                        "lettres_grises": {
                            "type": "string",
                            "description": "Format A,B,C"
                        },
                    },
                    "required": ["lettres_grises"],
                },
            },
        }],
    )

    # Vérification de l'appel d'outil
    if not response["message"].get("tool_calls"):
        return response["message"]["content"]

    tool_call = response["message"]["tool_calls"][0]
    args = tool_call["function"]["arguments"]

    # CSP exact
    mots_possibles = solveur_csp_local(**args)

    if not mots_possibles:
        return "Aucun mot valide ne correspond aux contraintes."

    # PROMPT STRICT POUR LE LLM
    prompt_final = f"""
Tu es un expert du jeu Wordle.

Tu dois choisir UN SEUL mot exactement présent dans la liste ci-dessous.
Il est STRICTEMENT INTERDIT de proposer un mot qui ny figure pas.

Critères de choix :
1. lettres fréquentes en français
2. diversité des lettres
3. mot linguistiquement courant

Liste des mots possibles :
{mots_possibles}

Réponds exactement sous la forme :
Mot choisi : <MOT>
Justification : <2 phrases maximum>
"""

    final_response = ollama.chat(
        model="llama3.1",
        messages=[{"role": "user", "content": prompt_final}]
    )

    # Sécurité anti-hallucination
    contenu = final_response["message"]["content"]
    lignes = contenu.splitlines()

    mot_choisi = None
    for ligne in lignes:
        if ligne.lower().startswith("mot choisi"):
            mot_choisi = ligne.split(":")[1].strip().upper()

    if mot_choisi not in mots_possibles:
        return f" Erreur LLM : mot invalide proposé.\n{contenu}"

    return (
        f" Mots possibles : {', '.join(mots_possibles)}\n\n"
        f" Analyse du LLM :\n{contenu}"
    )
