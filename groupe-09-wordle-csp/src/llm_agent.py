import ollama
import json
from csp_solver import solve_wordle_csp

def charger_dictionnaire(nom_fichier):
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            return [ligne.strip().upper() for ligne in f if len(ligne.strip()) == 5]
    except FileNotFoundError:
        print(f"Erreur : Le fichier {nom_fichier} est introuvable.")
        return []

DICTIONNAIRE = charger_dictionnaire('wordle.txt')

def solveur_csp_local(lettres_vertes="", lettres_jaunes="", lettres_grises=""):
    """Appelle la logique CSP réelle avec les mots du fichier txt"""
    contraintes = []
    
    if lettres_vertes:
        for item in lettres_vertes.split(','):
            if len(item) >= 2:
                lettre = item[0].upper()
                pos = int(item[1:])
                contraintes.append((lettre, pos, 'green'))

    if lettres_jaunes:
        for item in lettres_jaunes.split(','):
            if len(item) >= 2:
                lettre = item[0].upper()
                pos = int(item[1:])
                contraintes.append((lettre, pos, 'yellow'))

    if lettres_grises:
        for lettre in lettres_grises.split(','):
            lettre = lettre.strip().upper()
            for i in range(5):
                contraintes.append((lettre, i, 'gray'))

    # Utilise le dictionnaire chargé et la fonction importée
    return solve_wordle_csp(DICTIONNAIRE, contraintes)

def interroger_agent_wordle(prompt_utilisateur):
    # PREMIER PASSAGE : Le LLM décide d'appeler le CSP
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': prompt_utilisateur}],
        tools=[{
            'type': 'function',
            'function': {
                'name': 'solveur_csp_local',
                'description': 'Filtre les mots du dictionnaire selon les contraintes',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'lettres_vertes': {'type': 'string', 'description': 'Lettres bien placées, format: LettrePosition (ex: P0,R1)'},
                        'lettres_jaunes': {'type': 'string', 'description': 'Lettres mal placées, format: LettrePosition'},
                        'lettres_grises': {'type': 'string', 'description': 'Lettres absentes, format: A,B,C'},
                    },
                    'required': ['lettres_grises'],
                },
            },
        }],
    )

    # Vérification de l'appel d'outil
    if response['message'].get('tool_calls'):
        tool_call = response['message']['tool_calls'][0]
        args = tool_call['function']['arguments']
        
        # Exécution du CSP
        mots_possibles = solveur_csp_local(**args)
        
        # AFFICHAGE ÉTAPE 1 : On montre les résultats bruts
        if not mots_possibles:
            return "Le solveur CSP n'a trouvé aucun mot correspondant dans le dictionnaire."
        
        resultat_str = f"Après l'application des contraintes, les mots possibles sont : {', '.join(mots_possibles[:15])}"
        if len(mots_possibles) > 15: resultat_str += "..."

        # DEUXIÈME PASSAGE : On redonne ces mots à l'IA pour qu'elle choisisse le meilleur
        prompt_final = f"""Voici les mots trouvés par le solveur : {mots_possibles}. 
        En fonction de la langue et de la fréquence d'usage, quel est le mot 'optimal' à tenter ? 
        Réponds brièvement en expliquant pourquoi."""
        
        final_response = ollama.chat(
            model='llama3.1',
            messages=[
                {'role': 'user', 'content': prompt_utilisateur},
                response['message'],
                {'role': 'tool', 'content': str(mots_possibles), 'tool_call_id': '1'}, # On simule l'ID
                {'role': 'user', 'content': prompt_final}
            ]
        )
        
        return f"{resultat_str}\n\nL'analyse de l'IA : {final_response['message']['content']}"
   
    return response['message']['content']


