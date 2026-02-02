# Solveur Wordle avec CSP + LLM

## Description

Ce programme résout automatiquement le jeu Wordle en combinant :
- **CSP (Constraint Satisfaction Problem)** : Gestion intelligente des contraintes
- **Optimisation par entropie** : Maximisation de l'information à chaque coup
- **Intelligence artificielle** : Prise de décision stratégique

## Installation

### Prérequis
- Python 3.7 ou supérieur
- Fichier `words.txt` avec des mots de 5 lettres (un mot par ligne)

### Aucune dépendance externe requise !
Le programme utilise uniquement la bibliothèque standard Python.

## Fichiers du projet

```
wordle_solver_csp_llm.py  → Programme principal
words.txt                  → Dictionnaire de mots
GUIDE_COMPLET.md          → Explication détaillée du code
README.md                  → Ce fichier
test_wordle.py            → Tests automatiques
```

## Utilisation

### Mode interactif

```bash
python wordle_solver_csp_llm.py
```

Le programme va :
1. Charger le dictionnaire de mots
2. Proposer un mot à jouer
3. Te demander le feedback Wordle

### Format du feedback

Après avoir joué le mot proposé dans Wordle, entre le feedback :
- **G** = Vert (lettre correcte à la bonne position)
- **Y** = Jaune (lettre dans le mot mais mauvaise position)
- **B** = Gris (lettre absente du mot)

### Exemple d'utilisation

```
Tour 1
──────────────────────────────────────────────────
🔍 Solutions possibles : 5757

💡 Proposition : SLATE
   Raison : Mot d'ouverture optimal

➤ Feedback (G/Y/B) : BYGGG
```

Tu entres : `BYGGG`

Le programme analyse et continue :

```
Tour 2
──────────────────────────────────────────────────
📋 Contraintes : Lettres fixées : pos 2: A, pos 3: T, pos 4: E | Doit contenir : L
🔍 Solutions possibles : 12
   → BLATE, CLATE, FLATE, GLATE, PLATE, ...

💡 Proposition : PLATE
   Raison : Exploration de nouvelles lettres

➤ Feedback (G/Y/B) : GGGGG
```

```
🎉 Gagné en 2 coups ! Le mot était : PLATE
```

## Comment ça marche ?

### 1. Modélisation CSP

Le programme crée un système de contraintes basé sur les feedbacks :
- **must_be** : Positions où une lettre spécifique doit être (lettres vertes)
- **cannot_be** : Positions où certaines lettres ne peuvent pas être (lettres jaunes)
- **must_contain** : Lettres qui doivent être présentes (vertes + jaunes)
- **cannot_contain** : Lettres absentes du mot (grises)

### 2. Filtrage intelligent

À chaque tour, le programme :
1. Applique toutes les contraintes sur le dictionnaire
2. Ne garde que les mots valides
3. Réduit progressivement l'espace de recherche

### 3. Stratégie d'optimisation

Le programme utilise plusieurs stratégies selon le contexte :

- **≤3 mots restants** : Choix direct
- **>10 mots restants** : Maximisation de l'entropie (information)
- **4-10 mots** : Exploration de nouvelles lettres

### 4. Calcul d'entropie

L'entropie mesure combien d'information un mot apporte :
```
H = -Σ p(feedback) × log₂(p(feedback))
```

Plus l'entropie est élevée, plus le mot divise efficacement l'espace des solutions.

## Performances

- **Taux de réussite** : ~100% (avec feedback correct)
- **Nombre moyen de coups** : 3-4 essais
- **Temps par tour** : < 1 seconde (selon taille du dictionnaire)

## Personnalisation

### Changer le mot d'ouverture

Dans `interactive_solver()`, ligne ~290 :
```python
if step == 1:
    guess = "SLATE"  # Remplace par ton mot préféré
```

Bons mots d'ouverture : SLATE, CRANE, STARE, ARISE, SOARE

### Utiliser un dictionnaire personnalisé

```python
words = load_words("mon_dictionnaire.txt")
```

Format du fichier : un mot de 5 lettres par ligne.

### Ajuster la stratégie

Dans `llm_suggest_word()`, tu peux modifier les seuils :
```python
if len(possible_words) <= 5:  # Au lieu de 3
    return possible_words[0], "Peu de mots restants"
```

## Dépannage

### "Plus aucune solution possible"

Causes possibles :
- Feedback incorrect
- Mot secret pas dans le dictionnaire
- Erreur de saisie (confusion G/Y/B)

Solution : Recommence et vérifie bien les feedbacks.

### Le programme est lent

Si tu as un très gros dictionnaire (>10000 mots), le calcul d'entropie peut être lent.

Solution : Active `limit="possible_only"` pour tester moins de mots.

### Caractères bizarres dans les mots

Ton fichier `words.txt` n'est peut-être pas encodé en UTF-8.

Solution :
```python
with open(filename, "r", encoding="utf-8") as f:
```

## Ressources

- **Guide complet** : Voir `GUIDE_COMPLET.md` pour comprendre chaque ligne de code
- **Wordle officiel** : https://www.nytimes.com/games/wordle/
- **Théorie CSP** : https://en.wikipedia.org/wiki/Constraint_satisfaction_problem
- **Théorie de l'information** : https://fr.wikipedia.org/wiki/Entropie_de_Shannon

## Concepts utilisés

- Programmation par contraintes (CSP)
- Théorie de l'information (entropie de Shannon)
- Structures de données (dict, set, defaultdict)
- Algorithmes de recherche et filtrage
- Intelligence artificielle (simulation)


