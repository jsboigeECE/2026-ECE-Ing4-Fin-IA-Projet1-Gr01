import json
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from constraint import Problem

# --- 1. LE SOLVEUR CSP ---
def logique_csp(lettres_vertes, lettres_jaunes, lettres_grises):
    # Chargement du dictionnaire depuis le fichier
    with open("words.txt", "r", encoding="utf-8") as f:
        # On lit chaque ligne, on enlève les espaces et on met en majuscules
        dictionnaire = [ligne.strip().upper() for ligne in f if len(ligne.strip()) == 5]
    
    problem = Problem()
    indices = range(5)
    
    # On définit 5 variables (positions 0 à 4)
    problem.addVariables(indices, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    # Contrainte : Le mot doit être dans le dictionnaire
    def mot_valide(*lettres):
        return "".join(lettres) in dictionnaire
    problem.addConstraint(mot_valide, indices)

    # Contraintes VERTES (Position exacte)
    # Note : Le LLM envoie souvent les clés en string "0", on convertit en int
    for pos, lettre in lettres_vertes.items():
        p = int(pos)
        problem.addConstraint(lambda x, l=lettre: x == l, [p])


    # Contraintes GRISES (Lettre absente partout)
    # On gère si c'est une liste ['V'] ou un dictionnaire {'0': 'V'}
    lettres_grises_liste = lettres_grises.values() if isinstance(lettres_grises, dict) else lettres_grises
    
    for lettre in lettres_grises_liste:
        for p in indices:
            problem.addConstraint(lambda x, l=lettre: x != l, [p])

    # Contraintes GRISES (Lettre absente partout)
    #for lettre in lettres_grises:
    #    for p in indices:
    #        problem.addConstraint(lambda x, l=lettre: x != l, [p])

    # Contraintes JAUNES (Lettre présente mais PAS à cette position)
    # (Pour simplifier ici, on dit juste qu'elle ne doit pas être à sa position actuelle)
    # On pourra affiner cette logique plus tard
    for lettre in lettres_jaunes:
        # La lettre doit être quelque part ailleurs
        def contient_lettre(*lettres, char=lettre):
            return char in lettres
        problem.addConstraint(contient_lettre, indices)

    solutions = problem.getSolutions()
    return ["".join([s[i] for i in indices]) for s in solutions]

# --- 2. L'OUTIL POUR LE LLM ---
@tool
def filtrer_mots_wordle(lettres_vertes, lettres_jaunes, lettres_grises):
    """
    Appelle le solveur CSP pour filtrer les mots.
    lettres_vertes: dict des positions et lettres correctes (ex: {"0": "A"})
    lettres_jaunes: liste des lettres mal placées
    lettres_grises: liste des lettres absentes
    """
    print(f"\n[INFO] Exécution du solveur CSP avec : Vert={lettres_vertes}, Jaune={lettres_jaunes}, Gris={lettres_grises}")
    resultats = logique_csp(lettres_vertes, lettres_jaunes, lettres_grises)
    return resultats

# --- 3. INITIALISATION DU LLM ---
llm = ChatOllama(model="llama3.1", temperature=0).bind_tools([filtrer_mots_wordle])

# --- 4. EXECUTION ---
question = "J'ai testé le mot 'AVION'. Le A est vert, le V est gris, le I est jaune."
print(f"Question : {question}")

reponse = llm.invoke(question)

# On force l'exécution de la fonction si le LLM l'a demandée
if reponse.tool_calls:
    for call in reponse.tool_calls:
        args = call['args']
        mots_trouves = filtrer_mots_wordle.invoke(args)
        print(f"Mots possibles trouvés par le CSP : {mots_trouves}")
        
        if mots_trouves:
            # On crée un message très clair pour le LLM
            prompt_conseil = (
                f"L'utilisateur cherche un mot de 5 lettres. "
                f"Le solveur CSP a trouvé ces solutions possibles : {mots_trouves}. "
                f"En tant qu'expert du jeu Wordle, quel mot conseilles-tu d'essayer parmi cette liste et pourquoi ? "
                f"Réponds de manière courte et efficace."
            )
            phrase_finale = llm.invoke(prompt_conseil)
            print(f"\nConseil de l'IA : {phrase_finale.content}")
        else:
            print("\nConseil de l'IA : Aucun mot ne correspond dans le dictionnaire.")