from langchain_core.tools import tool

@tool
def filtrer_mots_wordle(lettres_vertes, lettres_jaunes, lettres_grises):
    """
    Cette fonction doit être appelée dès que l'utilisateur donne de nouveaux indices.
    Elle utilise un solveur CSP pour retourner les mots possibles.
    
    Arguments:
    - lettres_vertes : Un dictionnaire des lettres bien placées (ex: {0: 'A'} pour A en 1ère position)
    - lettres_jaunes : Une liste de lettres présentes mais mal placées
    - lettres_grises : Une liste de lettres totalement absentes du mot
    """
    # Ici, on simulera le retour du dictionnaire filtré
    # Plus tard, tu y mettras ton code python-constraint
    return ["ARBRE", "ALBUM"]

from langchain_ollama import ChatOllama

# Initialisation du modèle (Llama 3.1 est excellent pour ça)
llm = ChatOllama(model="llama3.1", temperature=0)

# On lie l'outil au modèle
llm_avec_outils = llm.bind_tools([filtrer_mots_wordle])

question = "J'ai testé le mot 'AVION'. Le A est vert, le V est gris, le I est jaune."
reponse = llm_avec_outils.invoke(question)

# On vérifie si le LLM veut appeler une fonction
if reponse.tool_calls:
    for call in reponse.tool_calls:
        print(f"Le LLM appelle la fonction : {call['name']}")
        print(f"Avec les arguments : {call['args']}")
else:
    print("Le LLM a répondu sans outil :", reponse.content)