# 📚 GUIDE COMPLET : Comprendre le Solveur Wordle CSP + LLM

## 🎯 Vue d'ensemble

Ce programme résout automatiquement le jeu Wordle en combinant :
1. **CSP (Constraint Satisfaction Problem)** : Un système de contraintes logiques
2. **Stratégie d'entropie** : Pour maximiser l'information obtenue
3. **LLM simulé** : Pour prendre des décisions intelligentes

---

## 📦 Structure du code

Le code est divisé en 7 parties :

### PARTIE 1 : Chargement des mots
### PARTIE 2 : Feedback Wordle
### PARTIE 3 : CSP (le cœur du projet !)
### PARTIE 4 : Stratégie d'entropie
### PARTIE 5 : Intégration LLM
### PARTIE 6 : Mode interactif
### PARTIE 7 : Fonction principale

---

## 🔍 PARTIE 1 : Chargement des mots

```python
def load_words(filename="words.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        return [w.strip().upper() for w in f if len(w.strip()) == 5]
```

**Ce que ça fait :**
- Ouvre le fichier `words.txt`
- Lit chaque ligne
- Garde seulement les mots de 5 lettres
- Met tout en MAJUSCULES pour éviter les problèmes

**Exemple :**
```
words.txt contient :
APPLE
cat
PLANE
hi

Résultat : ['APPLE', 'PLANE']  (seulement les mots de 5 lettres)
```

---

## 🎨 PARTIE 2 : Feedback Wordle

```python
def build_feedback(secret: str, guess: str) -> str:
```

**Ce que ça fait :**
Compare ton mot deviné avec le mot secret et génère un code :
- **G** (Green/Vert) : Lettre correcte à la bonne place
- **Y** (Yellow/Jaune) : Lettre dans le mot mais mauvaise place
- **B** (Black/Gris) : Lettre pas dans le mot

**Exemple :**
```python
secret = "PLANE"
guess = "SLATE"

Comparaison :
S - pas dans PLANE → B
L - dans PLANE mais pas à cette place → Y
A - bonne place ! → G
T - pas dans PLANE → B
E - bonne place ! → G

Résultat : "BYAGB"
```

**Comment ça marche :**

1. **Étape 1 : Marquer les verts**
```python
for i in range(5):
    if guess[i] == secret[i]:
        fb[i] = "G"
```
On regarde position par position. Si la lettre est identique : c'est vert !

2. **Étape 2 : Marquer les jaunes**
```python
for i in range(5):
    if fb[i] == "B":  # Si pas encore vert
        if secret_count[guess[i]] > 0:  # Et que la lettre existe ailleurs
            fb[i] = "Y"
```
On regarde les cases qui ne sont pas vertes et on check si la lettre existe ailleurs.

**Gestion des lettres répétées :**
```python
secret_count = Counter(secret)
```
Le `Counter` compte combien de fois chaque lettre apparaît. Ça évite de mettre "Y" plusieurs fois pour une même lettre qui n'apparaît qu'une fois.

---

## 🧩 PARTIE 3 : CSP (LA PARTIE IMPORTANTE !)

### Qu'est-ce qu'un CSP ?

**CSP = Constraint Satisfaction Problem**

C'est comme un puzzle avec des règles :
- Tu as des **variables** (les 5 positions du mot)
- Tu as des **domaines** (les lettres possibles pour chaque position)
- Tu as des **contraintes** (les règles à respecter)

**Exemple concret :**
```
Tu cherches un mot de 5 lettres avec ces règles :
- Position 2 DOIT être un "A"
- Le mot DOIT contenir "R"
- Le mot NE DOIT PAS contenir "S"
- Position 4 NE PEUT PAS être "T"

→ Mots valides : CRANE, BRAKE, FRAME...
→ Mots invalides : SLATE (contient S), GRANT (pas de A en position 2)
```

### La classe WordleCSP

```python
class WordleCSP:
    def __init__(self):
        self.must_be = {}                    # Position → Lettre obligatoire
        self.cannot_be = defaultdict(set)    # Position → Lettres interdites
        self.must_contain = set()            # Lettres qui doivent être dans le mot
        self.cannot_contain = set()          # Lettres interdites partout
```

**Les 4 types de contraintes :**

1. **must_be** : Lettres vertes
```python
self.must_be = {2: 'A', 4: 'E'}  # Position 2 = A, Position 4 = E
```

2. **cannot_be** : Lettres jaunes (dans le mot mais pas ici)
```python
self.cannot_be = {0: {'R'}, 1: {'T'}}  # R pas en position 0, T pas en position 1
```

3. **must_contain** : Lettres qu'on sait être dans le mot
```python
self.must_contain = {'A', 'R', 'E'}  # Le mot contient A, R et E
```

4. **cannot_contain** : Lettres grises (absentes du mot)
```python
self.cannot_contain = {'S', 'T', 'Q'}  # Ces lettres ne sont PAS dans le mot
```

### Ajouter des contraintes depuis un feedback

```python
def add_constraint_from_feedback(self, guess: str, feedback: str):
```

**Exemple pas à pas :**

```
Guess : SLATE
Feedback : BYGGG

Traduction :
S → B (gris)  : S n'est PAS dans le mot → cannot_contain.add('S')
L → Y (jaune) : L est dans le mot mais pas ici → must_contain.add('L') + cannot_be[1].add('L')
A → G (vert)  : A est à la bonne place → must_be[2] = 'A'
T → G (vert)  : T est à la bonne place → must_be[3] = 'T'
E → G (vert)  : E est à la bonne place → must_be[4] = 'E'
```

**Code détaillé :**
```python
for i in range(5):
    letter = guess[i]
    
    if feedback[i] == 'G':
        # Vert : cette lettre DOIT être ici
        self.must_be[i] = letter
        self.must_contain.add(letter)
    
    elif feedback[i] == 'Y':
        # Jaune : cette lettre est dans le mot mais PAS ici
        self.must_contain.add(letter)
        self.cannot_be[i].add(letter)
    
    else:  # B (Black/Gris)
        # Gris : cette lettre n'est pas dans le mot
        self.cannot_contain.add(letter)
```

### Vérifier si un mot est valide

```python
def is_valid(self, word: str) -> bool:
```

Cette fonction vérifie qu'un mot respecte TOUTES les contraintes :

```python
# 1. Vérifier les positions obligatoires (lettres vertes)
for pos, letter in self.must_be.items():
    if word[pos] != letter:
        return False  # Le mot ne respecte pas cette contrainte

# 2. Vérifier les positions interdites (lettres jaunes)
for pos, forbidden_letters in self.cannot_be.items():
    if word[pos] in forbidden_letters:
        return False

# 3. Vérifier que toutes les lettres obligatoires sont présentes
for letter in self.must_contain:
    if letter not in word:
        return False

# 4. Vérifier qu'aucune lettre interdite n'est présente
for letter in self.cannot_contain:
    if letter in word:
        return False

return True  # Toutes les contraintes sont respectées !
```

**Exemple concret :**

```
Contraintes actuelles après "SLATE" → "BYGGG" :
- must_be = {2: 'A', 3: 'T', 4: 'E'}
- cannot_be = {1: {'L'}}
- must_contain = {'L', 'A', 'T', 'E'}
- cannot_contain = {'S'}

Test du mot "PLATE" :
✓ P en position 0 : OK (pas de contrainte)
✓ L en position 1 : STOP ! L est interdit en position 1
→ is_valid("PLATE") = False

Test du mot "BLATE" :
✓ Position 2 = A : OK
✓ Position 3 = T : OK
✓ Position 4 = E : OK
✓ Contient L : OK
✓ Ne contient pas S : OK
→ is_valid("BLATE") = True
```

### Filtrer les mots

```python
def filter_words(self, words):
    return [w for w in words if self.is_valid(w)]
```

Cette ligne parcourt tous les mots et ne garde que ceux qui passent le test `is_valid()`.

**Compréhension de liste (list comprehension) :**
```python
# Version longue :
result = []
for w in words:
    if self.is_valid(w):
        result.append(w)

# Version courte (équivalente) :
result = [w for w in words if self.is_valid(w)]
```

---

## 📊 PARTIE 4 : Stratégie d'entropie

### Qu'est-ce que l'entropie ?

**L'entropie mesure la quantité d'information.**

En Wordle :
- Plus un mot génère de feedbacks différents, plus il donne d'information
- Plus on a d'information, plus on réduit vite les possibilités

**Analogie :**

Imagine que tu cherches un nombre entre 1 et 100.

**Mauvaise question :** "Est-ce 42 ?"
→ Si oui : gagné ! Si non : tu as encore 99 possibilités

**Bonne question :** "Est-ce plus grand que 50 ?"
→ Dans tous les cas, tu divises les possibilités par 2 !

C'est pareil pour Wordle : certains mots sont meilleurs car ils "divisent" mieux l'espace des solutions.

### Calcul de l'entropie

```python
def entropy_of_guess(guess, possible_words):
    counts = defaultdict(int)
    n = len(possible_words)
    
    # Compter combien de fois chaque feedback apparaît
    for secret in possible_words:
        fb = build_feedback(secret, guess)
        counts[fb] += 1
    
    # Calculer l'entropie
    H = 0.0
    for fb, k in counts.items():
        p = k / n  # Probabilité de ce feedback
        if p > 0:
            H -= p * log2(p)
    
    return H
```

**Exemple concret :**

```
Mots possibles : ['PLANE', 'SLATE', 'PLATE', 'FLARE', 'GLARE']
On teste le mot "SLATE"

Feedbacks possibles :
- Pour PLANE : BYGGG
- Pour SLATE : GGGGG
- Pour PLATE : BGAGG
- Pour FLARE : BGBGG
- Pour GLARE : BGBGG

Groupes de feedbacks :
- BYGGG : 1 mot (20%)
- GGGGG : 1 mot (20%)
- BGAGG : 1 mot (20%)
- BGBGG : 2 mots (40%)

Entropie = -0.2*log2(0.2) - 0.2*log2(0.2) - 0.2*log2(0.2) - 0.4*log2(0.4)
         ≈ 1.92 bits

Plus l'entropie est haute, mieux c'est !
```

**Formule mathématique :**
```
H = -Σ p(x) * log2(p(x))

Où :
- p(x) = probabilité d'obtenir le feedback x
- log2 = logarithme en base 2
```

### Trouver le meilleur mot

```python
def best_guess_entropy(possible_words, all_words, limit=None):
    candidates = possible_words if limit == "possible_only" else all_words
    
    best_word = None
    best_score = -1.0
    
    # Tester tous les mots candidats
    for g in candidates:
        score = entropy_of_guess(g, possible_words)
        if score > best_score:
            best_score = score
            best_word = g
    
    return best_word, best_score
```

On teste tous les mots possibles et on garde celui avec l'entropie maximale.

---

## 🤖 PARTIE 5 : Intégration LLM

### Qu'est-ce qu'un LLM ici ?

**LLM = Large Language Model** (comme ChatGPT)

Dans une vraie implémentation, on appellerait l'API OpenAI pour que l'IA :
1. Analyse les contraintes actuelles
2. Décide quelle stratégie utiliser
3. Suggère le meilleur mot

Ici, on **simule** cette intelligence avec des règles simples.

### La fonction llm_suggest_word

```python
def llm_suggest_word(csp: WordleCSP, possible_words, history):
```

**Stratégie en 3 niveaux :**

#### Niveau 1 : Peu de mots restants (≤3)
```python
if len(possible_words) <= 3:
    return possible_words[0], "Peu de mots restants, choix direct"
```
Si on a 3 mots ou moins, on en choisit un directement. Pas besoin de calculer !

#### Niveau 2 : Beaucoup de mots (>10)
```python
if len(possible_words) > 10:
    word, score = best_guess_entropy(possible_words, possible_words)
    return word, f"Maximisation de l'information (entropie={score:.2f})"
```
On utilise l'entropie pour maximiser l'information.

#### Niveau 3 : Exploration (4-10 mots)
```python
# Trouver un mot avec beaucoup de lettres non testées
all_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
tested_letters = csp.must_contain | csp.cannot_contain
untested_letters = all_letters - tested_letters

for word in possible_words:
    new_count = sum(1 for letter in set(word) if letter in untested_letters)
    # Garder le mot avec le plus de nouvelles lettres
```

On cherche à explorer de nouvelles lettres pour réduire l'incertitude.

**Exemple :**
```
Lettres testées : S, L, A, T, E
Lettres non testées : B, C, D, F, G, H, I, J, K, M, N, O, P, Q, R, U, V, W, X, Y, Z

Mots possibles :
- PLANE : P(nouveau), L(déjà testé), A(déjà testé), N(nouveau), E(déjà testé) → 2 nouvelles
- CRANE : C(nouveau), R(nouveau), A(déjà testé), N(nouveau), E(déjà testé) → 3 nouvelles
- BRAKE : B(nouveau), R(nouveau), A(déjà testé), K(nouveau), E(déjà testé) → 3 nouvelles

Meilleur choix : CRANE ou BRAKE (3 nouvelles lettres)
```

---

## 🎮 PARTIE 6 : Mode interactif

C'est la partie qui gère l'interaction avec l'utilisateur.

### Structure de la boucle principale

```python
step = 1
while True:
    # 1. Vérifier si on a terminé
    if len(possible) == 0:  # Pas de solution
        print("❌ Plus aucune solution possible !")
        return
    
    if len(possible) == 1:  # Une seule solution
        print(f"✅ Mot trouvé : {possible[0]}")
        return
    
    # 2. Afficher l'état actuel
    print(f"Tour {step}")
    print(f"Contraintes : {csp.describe_constraints()}")
    print(f"Solutions possibles : {len(possible)}")
    
    # 3. Proposer un mot
    if step == 1:
        guess = "SLATE"  # Premier coup optimal
    else:
        guess, reason = llm_suggest_word(csp, possible, history)
    
    print(f"Proposition : {guess}")
    
    # 4. Demander le feedback à l'utilisateur
    fb = input("Feedback (G/Y/B) : ").strip().upper()
    
    # 5. Mettre à jour les contraintes
    csp.add_constraint_from_feedback(guess, fb)
    
    # 6. Filtrer les mots possibles
    possible = csp.filter_words(possible)
    
    # 7. Passer au tour suivant
    step += 1
```

### Affichage des contraintes

```python
def describe_constraints(self):
    desc = []
    
    if self.must_be:
        positions = ", ".join([f"pos {pos}: {letter}" 
                               for pos, letter in sorted(self.must_be.items())])
        desc.append(f"Lettres fixées : {positions}")
    
    if self.must_contain:
        desc.append(f"Doit contenir : {', '.join(sorted(self.must_contain))}")
    
    if self.cannot_contain:
        desc.append(f"Ne doit PAS contenir : {', '.join(sorted(self.cannot_contain))}")
    
    return " | ".join(desc) if desc else "Aucune contrainte"
```

**Exemple d'affichage :**
```
Lettres fixées : pos 2: A, pos 4: E | Doit contenir : L | Ne doit PAS contenir : S, T
```

---

## 🚀 PARTIE 7 : Fonction principale

```python
def main():
    print("Chargement du dictionnaire...")
    words = load_words("words.txt")
    print(f"✓ {len(words)} mots de 5 lettres chargés\n")
    
    interactive_solver(words)

if __name__ == "__main__":
    main()
```

**Qu'est-ce que `if __name__ == "__main__"` ?**

C'est une convention Python :
- Si tu exécutes ce fichier directement : `python wordle_solver_csp_llm.py`
  → `__name__` vaut `"__main__"` → la fonction `main()` s'exécute

- Si tu importes ce fichier dans un autre : `import wordle_solver_csp_llm`
  → `__name__` vaut `"wordle_solver_csp_llm"` → la fonction `main()` ne s'exécute PAS

Ça permet de réutiliser les fonctions sans lancer le programme automatiquement.

---

## 🎯 Exemple d'exécution complète

```
Tour 1
──────────────────────────────────────────────────
🔍 Solutions possibles : 5757

💡 Proposition : SLATE
   Raison : Mot d'ouverture optimal

➤ Feedback (G/Y/B) : BYGGG
```

Le programme analyse :
```
S → B : cannot_contain.add('S')
L → Y : must_contain.add('L'), cannot_be[1].add('L')
A → G : must_be[2] = 'A'
T → G : must_be[3] = 'T'
E → G : must_be[4] = 'E'
```

Contraintes CSP :
```
must_be = {2: 'A', 3: 'T', 4: 'E'}
cannot_be = {1: {'L'}}
must_contain = {'L', 'A', 'T', 'E'}
cannot_contain = {'S'}
```

Filtrage :
```
5757 mots → teste is_valid() sur chacun → 12 mots restants
```

```
Tour 2
──────────────────────────────────────────────────
📋 Contraintes : Lettres fixées : pos 2: A, pos 3: T, pos 4: E | Doit contenir : L
🔍 Solutions possibles : 12
   → BLATE, CLATE, FLATE, GLATE, PLATE, ...

💡 Proposition : PLATE
   Raison : Exploration de nouvelles lettres (1 lettre non testée)

➤ Feedback (G/Y/B) : GGGGG
```

```
🎉 Gagné en 2 coups ! Le mot était : PLATE
```

---

## 📝 Résumé des concepts clés

### 1. CSP (Constraint Satisfaction Problem)
- **Variables** : Les 5 positions du mot
- **Domaines** : Les lettres possibles (A-Z)
- **Contraintes** : Les règles basées sur les feedbacks
- **Résolution** : Filtrer les mots qui respectent toutes les contraintes

### 2. Entropie
- Mesure la quantité d'information
- Plus l'entropie est haute, plus le mot divise bien l'espace des solutions
- Formule : H = -Σ p(x) * log2(p(x))

### 3. LLM (simulé)
- Analyse l'état du jeu
- Choisit la meilleure stratégie
- Peut utiliser : entropie, exploration, choix direct

### 4. Structures de données Python
- **dict** : `{clé: valeur}` → Accès rapide par clé
- **set** : `{élément1, élément2}` → Pas de doublons, tests rapides
- **defaultdict** : dict qui crée automatiquement des valeurs par défaut
- **Counter** : Compte les occurrences

---

## 🔧 Améliorations possibles

1. **Vraie intégration API OpenAI**
   - Remplacer `llm_suggest_word()` par un vrai appel API
   - Utiliser function calling pour laisser l'IA exploiter le CSP

2. **Interface graphique**
   - Créer une interface web avec React
   - Afficher visuellement les contraintes

