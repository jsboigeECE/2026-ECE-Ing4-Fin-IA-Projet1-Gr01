## Documentation technique

### Architecture générale
Le projet est composé de trois parties principales :
- Un solveur CSP chargé de filtrer les mots compatibles
- Un agent LLM chargé de proposer un mot parmi les solutions
- Une interface utilisateur (console et Streamlit)

### Solveur CSP
Le solveur modélise le mot secret comme une suite de lettres.
À chaque tentative, le feedback (G/Y/X) est traduit en contraintes.
Le dictionnaire est filtré pour ne conserver que les mots compatibles.

### Gestion des contraintes Wordle
- G (Green) : la lettre est imposée à la position donnée
- Y (Yellow) : la lettre est présente mais à une autre position
- X (Gray) : la lettre est absente du mot

### Agent LLM
L’agent LLM ne résout pas les contraintes.
Il reçoit la liste des mots valides fournie par le solveur CSP.
Il sélectionne un mot et fournit une explication du choix.

### Interface utilisateur
Deux interfaces sont proposées :
- Une interface console pour les tests
- Une interface web développée avec Streamlit

## Intégration d’une IA (LLM)

Le projet prévoit l’intégration d’un agent basé sur un modèle de langage (LLM).
Cet agent n’intervient pas dans la résolution des contraintes.

Le raisonnement logique du jeu Wordle est entièrement assuré par le solveur CSP.
L’agent LLM exploite uniquement les résultats fournis par le solveur
(liste des mots compatibles) afin d’aider à la prise de décision.

Cette approche permet de combiner un raisonnement symbolique explicite
avec une aide à la décision basée sur l’IA, tout en conservant un système
compréhensible et reproductible.
