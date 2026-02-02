# Analyse des Projets Etudiants - IA Finance ING4
**Module:** Intelligence Artificielle - Finance
**Date d'analyse:** 02/02/2026
**Evaluation pour présentations en classe**

---

## Grille d'Evaluation Commune (barème /20)

| Critère | Poids | Description |
|---------|-------|-------------|
| **Architecture & Code** | 4 pts | Modularité, lisibilité, typage, structure du projet |
| **Concepts IA/CSP** | 5 pts | Utilisation pertinente des techniques (OR-Tools, propagation, heuristiques...) |
| **Fonctionnalités** | 4 pts | Complétude, robustesse, cas limites gérés |
| **Documentation** | 3 pts | README, commentaires, identification équipe |
| **Exécutabilité** | 3 pts | Le projet fonctionne-t-il correctement? Testable facilement? |
| **Bonus** | 1 pt | Visualisation, originalité, fonctionnalités avancées |

---

## Projet 1: Wordle AI Solver (CSP + LLM)
**Dossier:** `groupe-09-wordle-csp`
**Sujet:** Solveur Wordle combinant CSP et LLM

### Equipe
Non spécifiée dans le README

### Description Technique
- **Approche:** Filtrage par contraintes + ranking LLM (Llama 3.1 via Ollama)
- **Modélisation:** Variables = mot secret, Domaine = dictionnaire, Contraintes = feedback Wordle
- **Gestion des doublons:** Correcte via Counter (règles Wordle exactes - 2 passes)
- **Interface:** Streamlit (UI web) + CLI

### Points Forts
- Bonne séparation des responsabilités (csp_solver.py, llm_agent.py)
- Gestion robuste des entrées (regex + fallback LLM)
- Documentation claire du format feedback (V/J/G)
- Limitation intelligente des candidats envoyés au LLM (MAX_CANDIDATES=40)

### Points Faibles
- **Ce n'est pas vraiment du CSP** : simple filtrage brut sans propagation de contraintes
- OR-Tools non utilisé - juste un filtre Python itératif
- Pas de tests unitaires ni de benchmark de performance
- Dépendance à Ollama (serveur local requis)
- Equipe non identifiée

### Analyse du Code
```python
# Le "solveur CSP" est en fait un filtre simple:
for w in possible_words:
    ok = True
    for guess, fb in attempts:
        if wordle_feedback_vjg(w, guess) != fb:
            ok = False; break
    if ok: solutions.append(w)
```
Pas de propagation ni de techniques CSP avancées.

### Test d'Exécution
- **Statut:** Requiert Ollama installé localement
- **Code CSP:** Fonctionnel mais basique

### Note: 12.5/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 3/4 | Bonne structure, code propre |
| Concepts IA/CSP | 2/5 | **Pas de vrai CSP**, juste filtrage |
| Fonctionnalités | 3/4 | Complet avec LLM |
| Documentation | 2/3 | Format OK mais pas d'équipe |
| Exécutabilité | 1.5/3 | Dépendance Ollama bloquante |
| Bonus | 1/1 | LLM original |

### Questions de Présentation

**Niveau Facile:**
1. Expliquez le format de feedback V/J/G. Pourquoi ce choix plutôt que Vert/Jaune/Gris?
   > **Réponse:** V/J/G = Version/Jaune/Gris, format compact 1 caractère vs 4-5 caractères

2. Quel est le rôle du fichier `wordle.txt`?
   > **Réponse:** Dictionnaire français ~23k mots de 5 lettres pour filtrage CSP

**Niveau Moyen:**
3. Comment gérez-vous les lettres en double dans un mot (ex: "ALLER")? Montrez avec un exemple concret.
   > **Réponse:** Counter compte occurrences : "ALLER" avec feedback VGJ_G sur "ELLE" → 1 L vert consommé, reste 1 L pour jaune

4. Pourquoi limitez-vous à 40 le nombre de candidats envoyés au LLM?
   > **Réponse:** Limite prompt LLM (tokens) + améliore pertinence (top candidates déjà filtrés)

5. Quelle est la différence entre le mode "texte structuré" et "texte libre"?
   > **Réponse:** Structuré = format strict "MOT\nMOT", Libre = phrase naturelle parsée par regex

**Niveau Difficile:**
6. Pourquoi votre fonction `wordle_feedback_vjg()` fait-elle deux passes (verts puis jaunes)? Que se passerait-il sinon?
   > **Réponse:** Passe 1 (verts) consomme lettres du Counter, passe 2 (jaunes) sur le reste. Sinon un jaune pourrait "voler" une lettre verte

7. **En quoi votre approche diffère-t-elle d'un vrai solveur CSP avec propagation de contraintes?**
   > **Réponse:** Filtrage = vérification a posteriori O(N). CSP = propagation proactive (arc-consistency, domaine réduit dynamiquement)

8. Comment OR-Tools pourrait-il améliorer votre solveur? Quelles techniques de propagation utiliseriez-vous?
   > **Réponse:** AllDifferent sur positions, Table constraints sur patterns, propagation = réduction exponentielle espace recherche

9. Quelle est la complexité temporelle de votre filtrage pour N mots candidats avec M contraintes? Comment l'optimiser?
   > **Réponse:** O(N×M×5) où N=mots, M=contraintes. Optimisation: index inverse par lettre, early exit, cache feedback

---

## Projet 2: Graph/Map Coloring
**Dossier:** `groupe-15-graph-coloring`
**Sujet 16:** Coloration de graphe et de carte

### Equipe
- Elsa Bodenan
- Shaili Tuil

### Description Technique
- **Solveur:** Google OR-Tools CP-SAT
- **Méthodes:** Greedy, DSATUR, CP avec k fixé, CP recherche minimum
- **Instances:** Triangle, Cycle, Grid, Erdos-Renyi, Map-like
- **Optimisations:** Symmetry breaking, hints greedy, bornes LB/UB

### Points Forts
- **Architecture exemplaire** : dataclasses, type hints, modules séparés
- Comparaison systématique de 4 méthodes avec benchmark CSV
- Mode interactif ET ligne de commande
- Export JSON + visualisation PNG avant/après
- Documentation détaillée avec répartition des tâches
- Utilisation avancée des hints OR-Tools

### Points Faibles
- Pas de gestion d'instances réelles (vraies cartes géographiques)
- Visualisation basique (couleurs pas toujours distinctives)

### Analyse du Code
```python
# Excellent usage des dataclasses et type hints
@dataclass(frozen=True)
class SolveInfo:
    status: str
    time_s: float
    conflicts: int
    branches: int

# Utilisation correcte des hints OR-Tools
if use_hints:
    hint = _greedy_hint(nodes, edges)
    for v, hv in hint.items():
        model.AddHint(c[v], int(hv))
```

### Test d'Exécution
```
Instance: erdos_n10_p0.3_s1 | nodes=10 edges=18
Method: cp_min | LB=1 UB=4 | k*=4 | colors_used=4 | valid=True
```
**Statut:** FONCTIONNEL - Temps de résolution rapide (~0.05s)

### Note: 18/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 4/4 | **Exemplaire** - dataclasses, typage, modules |
| Concepts IA/CSP | 5/5 | Hints, symmetry breaking, bornes |
| Fonctionnalités | 3.5/4 | Multiple méthodes, benchmark |
| Documentation | 3/3 | Complète avec répartition tâches |
| Exécutabilité | 3/3 | Testé OK, rapide |
| Bonus | 0.5/1 | Visualisation présente |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce qu'une coloration valide d'un graphe?
   > **Réponse:** Coloration valide = arêtes adjacentes ont couleurs différentes

2. Quelle est la différence entre l'heuristique Greedy et DSATUR?
   > **Réponse:** Greedy = ordre fixe + 1ère couleur dispo. DSATUR = degré saturation (couleurs voisins) → meilleure heuristique

**Niveau Moyen:**
3. Expliquez le concept de "symmetry breaking". Pourquoi fixez-vous la couleur du premier noeud à 0?
   > **Réponse:** Sans symmetry breaking : k! solutions équivalentes. Fixer nœud 0 = couleur 0 → divise espace par k

4. Comment calculez-vous la borne inférieure (LB) basée sur la clique?
   > **Réponse:** LB = taille max clique (sous-graphe complet). Clique de taille k → besoin ≥k couleurs

5. Que se passe-t-il si le timeout est atteint avant de trouver une solution optimale?
   > **Réponse:** Status = UNKNOWN, meilleure solution partielle retournée (pas optimale)

**Niveau Difficile:**
6. Pourquoi OR-Tools CP-SAT est-il plus efficace qu'un backtracking naïf pour ce problème? Quelles techniques utilise-t-il?
   > **Réponse:** CP-SAT: propagation contraintes, nogood learning, restarts, SAT encoding. Backtracking naïf = pas de learning

7. Comment la fonction `_greedy_hint()` aide-t-elle le solveur CP-SAT? Quel est l'impact sur le temps de résolution?
   > **Réponse:** Hint donne point départ → warm start, réduit branches explorées, 10-100× plus rapide sur grands graphes

8. Démontrez que le nombre chromatique d'un graphe planaire est au plus 4 (théorème des 4 couleurs). Votre algorithme peut-il le prouver?
   > **Réponse:** Théorème 4 couleurs (Appel-Haken 1976, preuve assistée). Algorithme trouve χ(G) mais ne prouve pas ≤4 pour planaires

9. Comparez DSATUR et Greedy : dans quels cas DSATUR donne-t-il de meilleurs résultats? Donnez un exemple de graphe.
   > **Réponse:** DSATUR meilleur sur graphes denses/structurés (ex: grille, Queen graph). Greedy suffit sur arbres/bipartis

---

## Projet 3: XAI Finance - IA Explicable pour Investissement
**Dossier:** `groupe-48-IA explicable pour décisions d'investissement (XAI Finance)`
**Sujet 48:** IA Explicable pour décisions d'investissement

### Equipe
- Alexis Thébault
- Maxime Delplace
- Malek Boussofara

### Description Technique
- **Modèle ML:** XGBoost Classifier avec régularisation forte
- **Explicabilité:** SHAP (TreeExplainer) pour feature importance
- **Architecture:** Backend FastAPI + Frontend Next.js/React
- **Données:** Prix, indicateurs techniques, macro, fondamentaux via API

### Points Forts
- **Projet full-stack complet** (backend Python + frontend React moderne)
- Utilisation avancée de SHAP pour l'explicabilité (TreeExplainer)
- API RESTful bien structurée avec endpoints clairs
- Génération de commentaires via LLM
- Arguments bullish/bearish séparés avec scores SHAP

### Points Faibles
- Dépendance à des clés API externes (non fournies, non testable)
- Pas de tests unitaires
- Documentation technique sommaire
- Sujet différent (ML) - moins de CSP

### Analyse du Code
```python
# Bonne utilisation de SHAP
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Régularisation forte pour éviter overfitting
params = {
    'gamma': 1.0,
    'reg_alpha': 0.5,
    'max_depth': 3
}
```

### Test d'Exécution
- **Statut:** Requiert configuration .env avec clés API (non testable)
- **Code backend:** Bien structuré mais non exécutable sans credentials

### Note: 16/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 3.5/4 | Full-stack, bonne structure |
| Concepts IA/CSP | 3.5/5 | SHAP correct mais pas CSP |
| Fonctionnalités | 3.5/4 | Complet, LLM intégré |
| Documentation | 2/3 | Basique |
| Exécutabilité | 1.5/3 | **Clés API requises** |
| Bonus | 1.5/1 | Full-stack + originalité |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce que XAI (Explainable AI)? Pourquoi est-ce important en finance?
   > **Réponse:** XAI = modèle explicable (feature importance). Finance → réglementation (MiFID II), confiance investisseurs

2. Quelle est la différence entre une prédiction "LONG" et "SHORT"?
   > **Réponse:** LONG = acheter (pari hausse), SHORT = vendre à découvert (pari baisse)

**Niveau Moyen:**
3. Expliquez comment SHAP calcule l'importance d'une feature. Quelle est la différence avec une simple feature importance?
   > **Réponse:** SHAP = Shapley values (théorie jeux). Contribution marginale feature en moyenne sur toutes coalitions. Feature importance = simple corrélation

4. Pourquoi utilisez-vous des paramètres de régularisation forts (gamma=1.0, reg_alpha=0.5)?
   > **Réponse:** Régularisation forte évite overfitting sur bruit marché. Gamma=1.0 pénalise feuilles, reg_alpha=0.5 pénalise poids

5. Comment la fonction `format_feature_impact()` génère-t-elle des arguments lisibles?
   > **Réponse:** Parse SHAP values, trie par impact absolu, génère phrases "RSI contribue +0.15 (bullish car >70)"

**Niveau Difficile:**
6. Qu'est-ce que le `base_value` dans SHAP et comment contribue-t-il à la prédiction finale?
   > **Réponse:** Base_value = prédiction moyenne sur training set. SHAP values = déviations. Pred_finale = base + Σ(shap_i)

7. Comment gérez-vous le risque d'overfitting avec votre modèle XGBoost? Quel serait le risque si vous n'aviez pas de régularisation?
   > **Réponse:** Early stopping, validation croisée TimeSeriesSplit, régularisation L1/L2. Sans → mémorise patterns aléatoires

8. Pourquoi utiliser TimeSeriesSplit plutôt qu'un split aléatoire pour les données financières? Quel biais évitez-vous?
   > **Réponse:** TimeSeriesSplit = respect temporalité (train passé, test futur). Split aléatoire → data leakage (futur → passé)

9. Comment interpréteriez-vous un SHAP value négatif sur une feature lors d'une prédiction LONG? Que signifie-t-il concrètement?
   > **Réponse:** SHAP négatif sur LONG = feature tire vers BAS. Ex: RSI=30 (survente) → shap=-0.2 sur LONG (suggère SHORT)

---

## Projet 4: Démineur IA (CSP + Probabilités)
**Dossier:** `groupe-XX-Maisonnave-Couvert-sujet11`
**Sujet 11:** Résolveur Démineur

### Equipe
- Gabriel Maisonnave
- Raphaël Couvert
- Aurèle DeGasquet

### Description Technique
- **Approche multi-niveaux:**
  1. Logique simple (règles triviales)
  2. Backtracking CSP (exploration exhaustive)
  3. Calcul probabiliste (dernier recours)
- **Interface:** Pygame avec heatmap de probabilités
- **Optimisation:** Limite MAX_BACKTRACK_VARS=14 pour éviter explosion combinatoire

### Points Forts
- **Progression pédagogique claire** (3 niveaux d'IA documentés)
- Benchmark intégré (mode headless avec statistiques)
- Visualisation des probabilités en temps réel (heatmap)
- Safe start (premier clic jamais une mine)
- README très détaillé et authentique
- Pruning efficace dans le backtracking

### Points Faibles
- Pas d'utilisation d'OR-Tools (backtracking maison)
- Limite de 14 variables peut bloquer sur grandes grilles
- Requiert Pygame (dépendance graphique)

### Analyse du Code
```python
# Backtracking avec pruning correct
def _is_consistent(self, assignment, constraints):
    for (cx, cy) in constraints:
        val = self.game.get_value(cx, cy)
        # Early exit si trop de mines
        if mines_count > val: return False
        # Early exit si pas assez de cases
        if mines_count + unknowns_count < val: return False
    return True
```

### Test d'Exécution
- **Statut:** Requiert Pygame et affichage graphique
- **Code logique:** Bien structuré, approche CSP correcte

### Note: 16/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 3.5/4 | Propre, bien commenté |
| Concepts IA/CSP | 4/5 | Backtracking + pruning + proba |
| Fonctionnalités | 3.5/4 | 3 niveaux, benchmark, heatmap |
| Documentation | 3/3 | **Excellente** |
| Exécutabilité | 1.5/3 | Requiert GUI Pygame |
| Bonus | 0.5/1 | Heatmap originale |

### Questions de Présentation

**Niveau Facile:**
1. Quelles sont les règles de base du Démineur que votre logique simple utilise?
   > **Réponse:** Si flags = chiffre → reste sûr. Si cachées+flags = chiffre → tout mine

2. Qu'est-ce que la "frontière" dans votre algorithme?
   > **Réponse:** Frontière = cases cachées adjacentes à cases révélées (zone active)

**Niveau Moyen:**
3. Pourquoi avez-vous limité MAX_BACKTRACK_VARS à 14? Quelle est la complexité au-delà?
   > **Réponse:** 2^14 = 16k combinaisons max (1-2s). Au-delà 2^20 = 1M+ → timeout (>10s)

4. Comment la fonction `_is_consistent()` valide-t-elle une assignation partielle? Donnez un exemple.
   > **Réponse:** Pour chaque contrainte (x,y,val): compte mines assignées + inconnues. Si mines>val OU mines+inconnues<val → False

5. Comment calculez-vous la probabilité de danger d'une case?
   > **Réponse:** P(mine) = (val - flags) / cachées. Max sur voisinages → pire cas conservateur

**Niveau Difficile:**
6. Démontrez avec un exemple que le backtracking peut identifier une case sûre même quand aucune règle simple ne s'applique.
   > **Réponse:** Exemple: Config A (case safe) ✓ pour toutes contraintes, Config B (case mine) ✓ aussi → incertain. Mais Config C (case mine) ✗ → case SAFE certain

7. Pourquoi votre taux de réussite diminue-t-il drastiquement sur les grandes grilles? Comment l'améliorer?
   > **Réponse:** Grandes grilles → frontière >14 vars → pas de backtracking → probabilités pures (30-40% réussite vs 80% petites grilles)

8. Comment OR-Tools CP-SAT pourrait-il améliorer votre solveur? Quels avantages par rapport au backtracking manuel?
   > **Réponse:** CP-SAT: propagation globale (pas limite 14), nogood learning, parallélisme. Backtracking: limite arbitraire, pas de learning

9. Expliquez pourquoi le calcul probabiliste est un "dernier recours". Dans quel cas devient-il la seule option viable?
   > **Réponse:** Dernier recours car non-déterministe (chance). Viable quand: frontière >14 vars OU toutes configs backtracking sont contradictoires

---

## Projet 5: Mots Croisés IA (Générateur & Solveur)
**Dossier:** `groupe-XX-mots-croises-csp`
**Sujet:** Générateur et solveur de mots croisés

### Equipe
Non spécifiée (à compléter lors de la présentation)

### Description Technique
- **Solveur:** Google OR-Tools CP-SAT
- **Contraintes:** Table constraints (AddAllowedAssignments)
- **Dictionnaire:** Fichier texte avec définitions parsées
- **Interface:** Flask web + génération HTML
- **Bonus:** Générateur de grille automatique via CSP

### Points Forts
- Utilisation élégante des Table Constraints (AddAllowedAssignments)
- Double fonctionnalité : génération ET résolution de grille
- Visualisation HTML soignée de la solution
- Parsing intelligent du dictionnaire avec définitions

### Points Faibles
- **README très minimaliste** (quelques lignes)
- Pas d'identification des auteurs
- Pas de tests unitaires
- Interface web basique (Flask simple)

### Analyse du Code
```python
# Bonne utilisation des Table Constraints
allowed_tuples = []
for w in words:
    int_tuple = [ord(char) - 65 for char in w]  # A=0, B=1...
    allowed_tuples.append(int_tuple)

# LA MAGIE EST ICI
model.AddAllowedAssignments(slot_cells, allowed_tuples)
```

### Test d'Exécution
```
Grille 12x12 - 20 cases noires
Slots générés avec croisements automatiques
```
**Statut:** FONCTIONNEL - Génération + résolution OK

### Note: 14/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 3/4 | Correct mais basique |
| Concepts IA/CSP | 4/5 | Table constraints bien utilisées |
| Fonctionnalités | 3/4 | Génération + résolution |
| Documentation | 1/3 | **Très insuffisante** |
| Exécutabilité | 2.5/3 | Testé OK |
| Bonus | 0.5/1 | HTML sympa |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce qu'un "slot" dans votre modélisation?
   > **Réponse:** Slot = emplacement mot (séquence cases consécutives H ou V)

2. Comment représentez-vous une lettre en tant que variable CP-SAT?
   > **Réponse:** Variable IntVar(0,25) où 0=A, 1=B... 25=Z

**Niveau Moyen:**
3. Expliquez la méthode `AddAllowedAssignments()`. Pourquoi est-elle adaptée à ce problème?
   > **Réponse:** AddAllowedAssignments(vars, tuples) = table constraint. Liste exhaustive combinaisons valides → propagation efficace

4. Comment détectez-vous les intersections entre mots horizontaux et verticaux?
   > **Réponse:** Intersection = cases communes (slot_H[i], slot_V[j]) doivent avoir même lettre → contrainte égalité

5. Que se passe-t-il si aucun mot du dictionnaire n'a la bonne longueur pour un slot?
   > **Réponse:** UNSAT immédiat. Checker avant: min/max longueurs dico vs grille

**Niveau Difficile:**
6. Quelle est la complexité théorique du problème des mots croisés? Est-il NP-complet? Prouvez-le.
   > **Réponse:** NP-complet (réduction depuis 3-SAT). Preuve: mots=clauses, croisements=variables partagées

7. Comment pourriez-vous optimiser la génération de grille pour maximiser les croisements?
   > **Réponse:** Objectif: maximize Σ(croisements). Contrainte: cases noires pas adjacentes. Générer grille d'abord avec CSP

8. Pourquoi utiliser des Table Constraints plutôt que des contraintes individuelles lettre par lettre? Quel impact sur la propagation?
   > **Réponse:** Table = propagation globale sur slot entier (arc-consistency multi-variables). Lettre-par-lettre = propagation locale faible

9. Expliquez comment AddAllowedAssignments implémente l'arc-consistency. Quelle serait la différence avec un filtrage naïf?
   > **Réponse:** Arc-consistency: supprime tuples incompatibles récursivement. Filtrage naïf = check exhaustif sans propagation itérative

---

## Projet 6: Planning Infirmiers (Nurse Rostering)
**Dossier:** `groupe-01-optimisation-planning-infirmiers`
**Sujet:** Optimisation du planning infirmier

### Equipe
Tom Beckermann, Romain Settbon

### Description Technique
- **Solveur:** Google OR-Tools CP-SAT
- **Variables:** x[infirmier, jour, shift] booléennes
- **Contraintes dures:** Couverture exacte, repos min, nuits consécutives, limite nuits
- **Contraintes souples:** Préférences, équilibrage charge/nuits
- **Fonction objectif:** Minimisation pénalités pondérées

### Points Forts
- **Modélisation CSP complète et rigoureuse**
- Séparation claire contraintes dures/souples
- Configuration facile via dataclass frozen
- Visualisation Matplotlib du planning
- Validation automatique des solutions
- Multi-workers (8 par défaut)

### Points Faibles
- README en texte brut (pas de markdown)
- Pas de scénarios de test variés (instances préfabriquées)
- Extension MiniZinc mentionnée mais non implémentée

### Analyse du Code
```python
@dataclass(frozen=True)
class ConfigurationPlanning:
    shifts: Tuple[Shift, ...] = ("M", "A", "N")
    min_jours_repos: int = 1
    max_jours_travail_consecutifs: int = 5
    poids_preferences: int = 10  # Soft constraint

# Objectif multi-critères
modele.Minimize(
    config.poids_preferences * sum(penalites_preferences)
    + config.poids_equilibrage_travail * (max_travail - min_travail)
    + config.poids_equilibrage_nuits * (max_nuits - min_nuits)
)
```

### Test d'Exécution
```
Faisable: True
Statut: OPTIMAL | Temps: 0.037s | Branches: 379
```
**Statut:** FONCTIONNEL - Excellent temps de résolution

### Note: 15/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 3.5/4 | Propre, dataclass |
| Concepts IA/CSP | 4.5/5 | Hard/soft bien séparés |
| Fonctionnalités | 3/4 | Fonctionnel mais peu d'instances |
| Documentation | 2/3 | README minimaliste |
| Exécutabilité | 3/3 | **Testé OK** |
| Bonus | 0/1 | Basique |

### Questions de Présentation

**Niveau Facile:**
1. Quels sont les trois types de shifts dans votre modèle?
   > **Réponse:** Matin (M), Après-midi (A), Nuit (N)

2. Pourquoi imposer un repos obligatoire après une nuit?
   > **Réponse:** Fatigue physiologique. Réglementation travail (Code du travail)

**Niveau Moyen:**
3. Expliquez la différence entre contraintes dures et contraintes souples dans votre modèle. Donnez un exemple de chaque.
   > **Réponse:** Dures = DOIT être respectée (coverage, repos). Souples = préférence (ex: équilibrage, souhaits) → pénalité objectif

4. Comment modélisez-vous la contrainte "maximum K jours consécutifs de travail"?
   > **Réponse:** BoolVar consecutive[i,j,k] = True si jours j,j+1,...,j+k travaillés. AddBoolOr sur fenêtres → interdit K+1 consécutifs

5. Pourquoi utilisez-vous `AddMaxEquality` et `AddMinEquality` pour l'équilibrage?
   > **Réponse:** AddMaxEquality(max_var, [charge_i]) trouve max. Objectif minimise (max-min) → équilibrage

**Niveau Difficile:**
6. Comment la fonction objectif combine-t-elle les différentes pénalités? Justifiez les poids choisis (10, 3, 2).
   > **Réponse:** Poids 10 (préférences) = prioritaire. Poids 3/2 (équilibrage) = secondaire. Trade-off: satisfaction vs équité

7. Que se passe-t-il si les contraintes dures sont insatisfiables? Comment le détecter et informer l'utilisateur?
   > **Réponse:** Status INFEASIBLE. Détection: analyser contraintes conflictuelles (ex: trop peu d'infirmiers pour coverage)

8. Comment adapteriez-vous le modèle pour gérer des compétences différentes entre infirmiers (ex: certains ne peuvent pas faire de nuits)?
   > **Réponse:** Ajout: skill[infirmier, type_shift] booléen. Contrainte: shift type N → sum(x[i,j,N] for i if skill[i,N]) >= coverage

9. Comparez votre approche CSP avec une approche métaheuristique (simulated annealing). Quels seraient les avantages/inconvénients?
   > **Réponse:** CSP: garanties optimalité, rapidité (secondes). Métaheuristiques: solutions approchées, bonnes pour très grandes instances

---

## Projet 7: Calendrier Sportif (Sports Scheduling)
**Dossier:** `Groupe-01-Sujet20-Calendrier-sportif`
**Sujet 20:** Génération de calendrier sportif round-robin

### Equipe
Non spécifiée dans le README

### Description Technique
- **Solveur:** Google OR-Tools CP-SAT
- **Problème:** Round-robin double (aller-retour)
- **Variables:** match_vars[i,j,r], is_home[i,r], break_vars[i,r]
- **Objectif:** Minimiser les breaks (matchs consécutifs domicile/extérieur)

### Points Forts
- Modélisation complète du problème round-robin
- Gestion automatique nombre impair d'équipes (ajout équipe fictive)
- Visualisation Gantt claire avec Matplotlib
- Statistiques détaillées par équipe (domicile/extérieur/breaks)
- Borne théorique n-2 breaks appliquée

### Points Faibles
- Pas de gestion des indisponibilités (contraintes calendrier)
- README minimaliste
- Code avec quelques redondances (ligne 251 dupliquée)
- Commentaires en français avec fautes

### Analyse du Code
```python
# Bonne modélisation des breaks
model.Add(break_vars[(i, r)] >=
    is_home[(i, r)] + is_home[(i, r + 1)] - 1)

# Borne théorique appliquée
model.Add(total_breaks <= (max_breaks * self.n_teams) - 2)
```

### Test d'Exécution
```
Equipes: 8 | Journées: 14
Solution trouvée avec succès!
Total breaks: 6 (optimal pour n=8)
```
**Statut:** FONCTIONNEL - Résolution rapide

### Note: 14/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 2.5/4 | Une seule classe, code dupliqué |
| Concepts IA/CSP | 4/5 | Breaks bien modélisés |
| Fonctionnalités | 3/4 | Complet pour le sujet |
| Documentation | 1.5/3 | Minimaliste, pas d'équipe |
| Exécutabilité | 3/3 | **Testé OK** |
| Bonus | 0/1 | Gantt basique |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce qu'un calendrier round-robin? Pourquoi "aller-retour"?
   > **Réponse:** Round-robin = tous contre tous. Aller-retour = domicile + extérieur (2× matchs)

2. Qu'est-ce qu'un "break" dans un calendrier sportif?
   > **Réponse:** Break = 2 matchs consécutifs même lieu (ex: 2 domiciles d'affilée). Pénalité logistique/équité

**Niveau Moyen:**
3. Pourquoi la variable `is_home[i,r]` est-elle nécessaire en plus de `match_vars[i,j,r]`?
   > **Réponse:** is_home booléenne = simplification. match_vars seul → requêtes complexes (sum sur adversaires)

4. Comment garantissez-vous que chaque équipe joue exactement n-1 matchs à domicile sur la saison?
   > **Réponse:** Contrainte: sum(is_home[i,r] for r) = n-1 (moitié des 2(n-1) journées)

5. Expliquez la contrainte de détection des breaks. Pourquoi deux inégalités?
   > **Réponse:** Deux inégalités capturent OR logique: (home[r] AND home[r+1]) OR (away[r] AND away[r+1])

**Niveau Difficile:**
6. Démontrez que le nombre minimum de breaks pour n équipes est n-2. Donnez un exemple pour n=4.
   > **Réponse:** Preuve: n équipes → n-1 journées aller. Optimal = alterné dom/ext. 1 break inévitable par équipe (transition aller→retour). n breaks - 2 = n-2. Exemple n=4: 3-2=1 break minimum

7. Comment modéliseriez-vous des contraintes de type "l'équipe X ne joue pas le dimanche" ou "pas deux matchs le même week-end"?
   > **Réponse:** Contrainte: BoolVar plays_sunday[i,r]. AddForbiddenAssignments sur (equipe_X, dimanche)

8. Le problème de sports scheduling avec minimisation des breaks est-il NP-difficile? Comment le prouver?
   > **Réponse:** OUI, NP-difficile (réduction depuis HAM-PATH). Minimisation breaks = variant Travelling Tournament Problem

9. Pourquoi utilisez-vous deux contraintes (≥) pour détecter un break au lieu d'une seule équation? Quelle est la logique booléenne sous-jacente?
   > **Réponse:** Deux contraintes = DISJUNCTION. is_home[r]+is_home[r+1]-1 ≥ break (si 2 domiciles → break=1). Idem extérieur

---

## Projet 8: Détection Fraude Financière (ILP - Aleph)
**Dossier:** `projet42_fraude_financiere_BALAGUER_FLOCH`
**Sujet 42:** Détection de fraude par IA symbolique (Inductive Logic Programming)

### Equipe
- Jules Balaguer
- Anaïs Floch

### Description Technique
- **Approche:** Inductive Logic Programming (ILP) avec Aleph (Prolog)
- **Modélisation:** Graphe de transactions (NetworkX) + extraction features symboliques
- **Pipeline complet:** Python → Graphe → Features → Prolog → Aleph → Règles logiques
- **Intégration:** SWI-Prolog portable inclus + Aleph (GitHub)

### Points Forts
- **Approche très originale** : seul projet ILP/symbolic AI du lot
- Pipeline entièrement automatisé (Python génère le Prolog)
- Features symboliques explicables (cycles, degrés, montants ronds)
- SWI-Prolog portable inclus (pas d'installation requise)
- Documentation claire avec méthodologie
- Evaluation avec métriques (précision, rappel, accuracy)

### Points Faibles
- Pas de résultats concrets fournis (règles apprises absentes du repo)
- Pas de tests unitaires
- Dataset Kaggle requis (mais lien fourni, normal pour 50+ MB)

### Analyse du Code
```python
# Architecture propre avec classe unique
class AlephFraudDetector:
    def train(self):
        self.build_graph()           # NetworkX DiGraph
        self.extract_features()      # Cycles, degrés, patterns
        self.generate_prolog_file()  # Automatique !
        self.run_aleph()             # subprocess SWI-Prolog
        self.evaluate_rules()        # Métriques ML

# Features symboliques bien pensées
in_cycle = 'yes' if nx.has_path(graph, to, from) and path_length <= 3
is_round = 'yes' if amount % 1000 == 0
```

### Test d'Exécution
- **Statut:** Prêt à exécuter - SWI-Prolog inclus, dépendances OK, dataset Kaggle à télécharger
- **Code:** Très bien structuré, pipeline complet et automatisé

### Note: 17/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 4/4 | **Excellente** classe, pipeline automatisé |
| Concepts IA/CSP | 4/5 | **ILP = IA symbolique** (très pertinent!) |
| Fonctionnalités | 4/4 | Pipeline complet + métriques ML |
| Documentation | 3/3 | README complet avec méthodologie |
| Exécutabilité | 2/3 | Dataset Kaggle (lien fourni, normal) |
| Bonus | 1/1 | Très original (ILP rare) |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce que l'ILP (Inductive Logic Programming)? En quoi diffère-t-il du machine learning classique?
   > **Réponse:** ILP = apprend règles logiques (Prolog) depuis exemples. ML classique = boîte noire (poids, neurones). ILP = explicable

2. Pourquoi utiliser Prolog pour ce problème?
   > **Réponse:** Prolog = logique du 1er ordre, backtracking natif, intégration Aleph (écrit en Prolog)

**Niveau Moyen:**
3. Expliquez comment vous détectez les cycles dans le graphe de transactions. Pourquoi un cycle pourrait-il indiquer une fraude?
   > **Réponse:** Cycles détectés via `nx.has_path(to, from)` avec path_length ≤3. Fraude car: A→B→C→A = circuit blanchiment

4. Quelle est la différence entre les features symboliques (is_round_amount, in_cycle) et des features numériques brutes?
   > **Réponse:** Symboliques = catégories (is_round=yes/no). Numériques = valeurs continues (amount=5420.32). ILP requiert symbolique

5. Comment Aleph génère-t-il des règles logiques à partir de vos exemples?
   > **Réponse:** Aleph = recherche en faisceau (beam search) sur espace règles. Evalue coverage + accuracy → garde meilleures

**Niveau Difficile:**
6. Expliquez le rôle des déclarations `modeh` et `modeb` dans Aleph. Pourquoi sont-elles nécessaires?
   > **Réponse:** modeh = tête règle (ce qu'on veut prédire: laundering). modeb = corps (features utilisables). Langage bias

7. Comment garantir que les règles apprises ne sont pas du surapprentissage? Quelle est votre stratégie de validation?
   > **Réponse:** Train/test split 70/30. Validation croisée. Paramètres: minpos (3 exemples min), minacc (5% précision min)

8. **En quoi ILP diffère-t-il fondamentalement de CSP?** Quelle est la différence entre "apprendre des règles" et "satisfaire des contraintes"?
   > **Réponse:** **ILP = induction (généralisation depuis exemples)**. **CSP = déduction (satisfaire contraintes données)**. ILP crée connaissance, CSP l'applique

9. Pourquoi la détection de cycles courts (≤3 sauts) est-elle pertinente pour détecter du blanchiment? Donnez un exemple concret.
   > **Réponse:** Cycles courts = structuring/layering rapide. Exemple: Compte A (sale) → B (intermédiaire) → C (clean) → A. ≤3 sauts évite détection longue chaîne

---

## Projet 9: Wordle CSP + Optimisation Entropie
**Dossier:** `GGG`
**Sujet:** Solveur Wordle avec CSP et optimisation par entropie

### Equipe
- Toni Awad
- Ethan (nom complet à confirmer)

### Description Technique
- **Approche:** CSP (Constraint Satisfaction Problem) + Optimisation par entropie de Shannon
- **Modélisation:** Variables = positions, Domaine = lettres, Contraintes = feedback Wordle
- **Stratégie:** Adaptive selon nombre de candidats (entropie si >10, exploration si 4-10, direct si ≤3)
- **Interface:** CLI interactif + HTML standalone

### Points Forts
- **Vrai CSP** : Contraintes explicites (must_be, cannot_be, must_contain, cannot_contain)
- Optimisation par entropie de Shannon (H = -Σ p(feedback) × log₂(p(feedback)))
- Stratégie adaptative sophistiquée selon contexte
- Aucune dépendance externe (bibliothèque standard Python uniquement)
- Documentation exceptionnelle (GUIDE_COMPLET.md détaille chaque ligne)
- Tests unitaires présents (test_wordle.py)
- Interface web standalone (solver_web.html)
- Gestion correcte des doublons (Counter)

### Points Faibles
- Pas d'OR-Tools (CSP manuel, mais bien implémenté)
- Pas de benchmark de performance formalisé
- Equipe non complètement identifiée

### Analyse du Code
```python
# CSP bien modélisé
class WordleCSP:
    def __init__(self):
        self.must_be = {}                    # Position → Lettre obligatoire
        self.cannot_be = defaultdict(set)    # Position → Lettres interdites
        self.must_contain = set()            # Lettres présentes
        self.cannot_contain = set()          # Lettres absentes

# Calcul d'entropie pour optimisation
def compute_entropy(word, possible_words):
    feedback_counts = Counter()
    for candidate in possible_words:
        fb = build_feedback(candidate, word)
        feedback_counts[fb] += 1

    total = len(possible_words)
    entropy = 0.0
    for count in feedback_counts.values():
        p = count / total
        if p > 0:
            entropy -= p * log2(p)  # Shannon entropy
    return entropy
```

### Test d'Exécution
- **Statut:** FONCTIONNEL - Aucune dépendance, prêt à l'emploi
- **Performances:** 3-4 coups en moyenne, ~100% réussite

### Note: 16/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 3.5/4 | Propre, bien structuré, sans dépendances |
| Concepts IA/CSP | 4.5/5 | **Vrai CSP + optimisation entropie** |
| Fonctionnalités | 3.5/4 | Stratégie adaptative, tests, web UI |
| Documentation | 3/3 | **GUIDE_COMPLET.md exceptionnel** |
| Exécutabilité | 3/3 | **Parfait** - aucune installation |
| Bonus | 0.5/1 | Entropie originale |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce que l'entropie de Shannon? Pourquoi l'utiliser pour Wordle?
   > **Réponse:** Entropie = mesure d'information H = -Σ p(feedback) × log₂(p(feedback)). Entropie élevée → mot divise bien l'espace, maximise info gagnée

2. Quelle est la différence entre must_contain et must_be?
   > **Réponse:** must_contain = lettre présente quelque part (jaune). must_be = lettre fixée à position précise (vert)

**Niveau Moyen:**
3. Comment votre stratégie adaptative fonctionne-t-elle? Pourquoi changer selon le nombre de candidats?
   > **Réponse:** ≤3 mots → choix direct. 4-10 → exploration nouvelles lettres. >10 → maximisation entropie (calcul coûteux mais efficace)

4. Comment gérez-vous les lettres en double (ex: "ALLER" avec 2 L)?
   > **Réponse:** Counter() compte occurrences. Étape 1: marque verts (consomme lettres). Étape 2: jaunes sur reste. Évite conflit vert/jaune

5. Pourquoi "SLATE" est-il un bon mot d'ouverture?
   > **Réponse:** Contient 5 lettres fréquentes (S, L, A, T, E), toutes différentes. Entropie élevée (~5.8 bits). Maximise information premier coup

**Niveau Difficile:**
6. Expliquez le calcul d'entropie. Que représente chaque terme de la formule?
   > **Réponse:** H = -Σ p(fb) × log₂(p(fb)). p(fb) = probabilité du feedback fb. Chaque terme = contribution du feedback. Somme négative car log₂(p)<0 si p<1

7. Comment optimiseriez-vous le calcul d'entropie pour un grand dictionnaire (>10k mots)?
   > **Réponse:** 1) Échantillonnage: tester subset de candidats. 2) Cache: mémoriser entropies. 3) Parallélisation: multiprocessing. 4) Pré-calcul: database entropies offline

8. **En quoi votre approche diffère-t-elle fondamentalement du projet groupe-09?**
   > **Réponse:** **Groupe-09 = filtrage naïf O(N×M)**. **GGG = CSP + optimisation entropie**. Différence: groupe-09 vérifie tous mots, GGG choisit le mot qui maximise information (stratégie glouton informée)

9. Prouvez que l'entropie maximale pour 5 feedbacks est log₂(3^5) = 5×log₂(3) ≈ 7.92 bits. Pourquoi n'atteint-on jamais cette valeur en pratique?
   > **Réponse:** Théoriquement 3^5=243 feedbacks possibles → H_max=log₂(243)≈7.92 bits. En pratique: certains feedbacks impossibles (contradictions), distribution non uniforme → entropie réelle < 7.92

---

## Projet 10: Fair Credit Scoring (Fairlearn)
**Dossier:** `FCC`
**Sujet:** Scoring de crédit équitable par optimisation sous contraintes

### Equipe
- Hugo Chrismant
- Jeremy Clement
- Mael Faye

### Description Technique
- **Approche:** Optimisation sous contraintes d'équité (Fairlearn)
- **Contraintes:** Demographic Parity, Equalized Odds
- **Algorithme:** ExponentiatedGradient (réduction de Fairlearn)
- **Trade-off:** Performance prédictive vs non-discrimination (paramètre epsilon)
- **Dataset:** clients.csv (income, credit_amount, sex, education, etc.)

### Points Forts
- **Architecture exemplaire** : Modules séparés (preprocessing, models, fairness, evaluate, explain)
- Intégration formelle de contraintes d'équité dans l'apprentissage (pas post-processing)
- Analyse trade-off epsilon → quantification compromis performance/équité
- Métriques d'équité rigoureuses (DP diff, EO diff, MetricFrame par groupe)
- Tests unitaires présents
- Visualisations (taux acceptation par groupe, courbes trade-off)
- Documentation technique complète + slides PDF
- SHAP pour explicabilité (bonus)

### Points Faibles
- Dataset synthétique (pas de vraies données financières)
- Pas d'API ou interface utilisateur
- Requiert dépendances (Fairlearn, scikit-learn, pandas, matplotlib)

### Analyse du Code
```python
# Optimisation sous contraintes (Fairlearn)
from fairlearn.reductions import ExponentiatedGradient, DemographicParity, EqualizedOdds

def train_fair_model(X_train, y_train, A_train, constraint="dp", eps=0.02):
    if constraint == "dp":
        moment = DemographicParity()  # Contrainte: P(Y=1|A=a) ≈ P(Y=1|A=b)
    elif constraint == "eo":
        moment = EqualizedOdds()      # Contrainte: FPR + FNR équilibrés par groupe

    mitigator = ExponentiatedGradient(
        estimator=LogisticRegression(),
        constraints=moment,
        eps=eps  # Tolérance violation contrainte
    )
    mitigator.fit(X_train, y_train, sensitive_features=A_train)
    return mitigator

# Trade-off sweep
for eps in [0.005, 0.01, 0.02, 0.05, 0.1]:
    model = train_fair_model(X, y, A, constraint="dp", eps=eps)
    # Plus eps petit → contrainte stricte → équité forte, performance dégradée
```

### Test d'Exécution
- **Statut:** FONCTIONNEL - Dépendances OK, dataset inclus
- **Résultats:** Trade-off visible (baseline AUC ~0.75, fair models ~0.70-0.73)

### Note: 17/20
| Critère | Note | Commentaire |
|---------|------|-------------|
| Architecture & Code | 4/4 | **Exemplaire** - modules séparés, propre |
| Concepts IA/CSP | 4.5/5 | **Optimisation sous contraintes** (Fairlearn) |
| Fonctionnalités | 3.5/4 | Trade-off analysis, métriques, viz |
| Documentation | 3/3 | README complet + slides + doc technique |
| Exécutabilité | 2.5/3 | Dataset OK, dépendances standards |
| Bonus | 1/1 | SHAP + originalité (fairness rare) |

### Questions de Présentation

**Niveau Facile:**
1. Qu'est-ce que Fairlearn? Pourquoi l'utiliser pour le scoring de crédit?
   > **Réponse:** Fairlearn = bibliothèque Microsoft pour fairness ML. Crédit → régulation (discrimination sexe/race interdite). Fairlearn impose contraintes d'équité formellement

2. Quelle est la différence entre une approche "post-processing" et "in-processing" pour la fairness?
   > **Réponse:** Post-processing = ajuster prédictions après entraînement. In-processing = contraintes intégrées pendant apprentissage (Fairlearn). In-processing plus robuste

**Niveau Moyen:**
3. Expliquez la différence entre Demographic Parity et Equalized Odds.
   > **Réponse:** DP = P(Ŷ=1|A=a) ≈ P(Ŷ=1|A=b) (taux acceptation égal par groupe). EO = FPR et FNR égaux par groupe (erreurs équilibrées). DP plus strict, EO permet différences justifiées

4. Que représente le paramètre epsilon? Comment l'ajuster?
   > **Réponse:** Epsilon = tolérance violation contrainte. Petit epsilon → contrainte stricte → forte équité, baisse performance. Grand epsilon → contrainte relâchée → performance préservée, équité faible

5. Comment Fairlearn mesure-t-il les disparités entre groupes?
   > **Réponse:** MetricFrame calcule métriques (FPR, FNR, selection_rate) par groupe. Diff = max - min entre groupes. DP diff, EO diff = métriques scalaires agrégées

**Niveau Difficile:**
6. Expliquez l'algorithme ExponentiatedGradient. Comment minimise-t-il la contrainte?
   > **Réponse:** EG = algorithme réduction. Reformule fairness contrainte comme jeu à somme nulle. Joueur 1 (learner) minimise loss. Joueur 2 (auditor) maximise violation contrainte. Nash equilibrium = modèle équitable optimal

7. Démontrez mathématiquement que Demographic Parity est incompatible avec l'accuracy parfaite si base rates diffèrent entre groupes.
   > **Réponse:** Si P(Y=1|A=a) ≠ P(Y=1|A=b), alors DP impose P(Ŷ=1|A=a)=P(Ŷ=1|A=b). Mais accuracy optimale → Ŷ≈Y → P(Ŷ=1|A) ≈ P(Y=1|A). Contradiction si base rates diffèrent. QED: trade-off inévitable

8. **En quoi ce projet est-il un problème CSP/optimisation sous contraintes?**
   > **Réponse:** **CSP car variables=prédictions, contraintes=fairness metrics (DP/EO), objectif=minimize loss SOUS contraintes**. ExponentiatedGradient = solveur CSP pour ML. Différence CSP classique: variables continues, contraintes soft (epsilon tolérance)

9. Comment adapteriez-vous le modèle pour gérer 3+ groupes protégés (ex: sexe + nationalité)? Quels nouveaux défis apparaissent?
   > **Réponse:** Fairlearn supporte multi-groupes (sensitive_features=array 2D). Défis: 1) Intersectionnalité (femmes noires vs hommes blancs). 2) Combinatoire: K groupes → K(K-1)/2 comparaisons. 3) Trade-off: satisfaire contraintes pour TOUS groupes → perte performance accrue. Solution: contraintes hiérarchiques ou relaxation epsilon adaptative

---

## Tableau Récapitulatif des Notes

| Rang | Projet | Note /20 | Points Forts | Points Faibles |
|------|--------|----------|--------------|----------------|
| 1 | **Graph Coloring** | **18** | Architecture exemplaire, hints OR-Tools | Pas de vraies cartes |
| 2 | **Fraude ILP (Aleph)** | **17** | ILP symbolique, pipeline automatisé | Pas de résultats fournis |
| 2 | **Fair Credit Scoring** | **17** | Fairlearn, trade-off analysis | Dataset synthétique |
| 4 | Démineur IA | **16** | 3 niveaux, heatmap, documentation | Pas d'OR-Tools |
| 4 | XAI Finance | **16** | Full-stack, SHAP | Pas testable (API) |
| 4 | **Wordle CSP + Entropie** | **16** | Vrai CSP, optimisation entropie | Pas d'OR-Tools |
| 7 | Planning Infirmiers | **15** | CSP rigoureux, hard/soft | Doc basique |
| 8 | Mots Croisés | **14** | Table constraints | **Doc très faible** |
| 8 | Calendrier Sportif | **14** | Modèle complet, Gantt | Code pas propre |
| 10 | **Wordle CSP+LLM** | **12.5** | LLM original | **Pas vraiment CSP** |

**Moyenne:** 15.55/20
**Ecart-type:** 1.59
**Min:** 12.5 | **Max:** 18
**Nombre de projets:** 10

---

## Barème détaillé pour la soutenance

### Pondération suggérée
- Note technique (ce document): **60%**
- Présentation orale: **25%**
- Réponses aux questions: **15%**

### Critères de présentation orale
| Critère | Points |
|---------|--------|
| Clarté de l'explication | /5 |
| Démonstration live | /5 |
| Compréhension du code | /5 |
| Maîtrise des concepts CSP/IA | /5 |

---

## Notes pour l'Evaluation en Présentation

### Conseils généraux
- Vérifier que les étudiants peuvent expliquer leur propre code
- Poser au moins une question de chaque niveau de difficulté
- Demander une démonstration live si possible
- Vérifier la compréhension des concepts CSP/IA sous-jacents
- **Demander l'identification de l'équipe si absente du README**

### Points d'attention par projet
- **Wordle groupe-09:** Demander pourquoi ce n'est pas vraiment du CSP (filtrage vs propagation)
- **Wordle GGG:** Faire expliquer calcul entropie + stratégie adaptative
- **Graph Coloring:** Tester la compréhension des hints et du symmetry breaking
- **XAI Finance:** S'assurer de la compréhension de SHAP vs feature importance
- **Démineur:** Demander un exemple de backtracking manuel sur papier
- **Mots Croisés:** Vérifier compréhension des table constraints vs contraintes unitaires
- **Planning:** Tester distinction contraintes dures/souples avec exemples concrets
- **Calendrier:** Vérifier calcul théorique des breaks (n-2)
- **Fraude ILP:** Demander la différence fondamentale entre ILP et CSP (apprentissage vs satisfaction)
- **Fair Credit Scoring:** Faire expliquer ExponentiatedGradient + trade-off DP/EO

### Questions bonus transversales
1. Quelle est la différence entre CP-SAT et un MIP solver?
2. Quand utiliser des hints vs pas de hints?
3. Comment détecter qu'un problème n'a pas de solution?
4. Quelle est la complexité worst-case de vos algorithmes?

---

## Historique des versions

- **Version 2.3** (02/02/2026 - 17h30) :
  - Ajout Projet 9 (Wordle CSP + Entropie - GGG) : **16/20** (PR #15)
  - Ajout Projet 10 (Fair Credit Scoring - FCC) : **17/20** (PR #16)
  - Réorganisation réponses (inline après chaque question)
  - Moyenne: 15.55/20 | Écart-type: 1.59 | 10 projets
- **Version 2.2** (02/02/2026 - 16h00) :
  - Réévaluation Projet 8 (Fraude ILP) : 13.5 → **17/20** (ILP = IA symbolique ✓)
  - Ajout 9ème question par projet (total: 9 questions/projet)
  - Moyenne: 15.31/20 | Écart-type: 1.75 | 8 projets
- **Version 2.1** (02/02/2026 - 15h30) : Ajout Projet 8 (Fraude ILP) suite fusion PR #13
- **Version 2.0** (02/02/2026 - 14h00) : Révision complète avec notes ajustées
- **Version 1.0** (01/02/2026) : Création initiale avec 7 projets

---

*Document généré automatiquement par analyse de code - Version 2.3 - 02/02/2026*
*A mettre à jour après présentations avec notes finales*
