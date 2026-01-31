# Documentation technique – Calendrier Sportif

## 1. Modélisation du problème

Le problème traité est un **tournoi round-robin aller-retour** comportant un nombre pair d’équipes *n*.

- Nombre de journées : `2 × (n − 1)`
- Chaque équipe joue exactement un match par journée
- Chaque paire d’équipes se rencontre deux fois (domicile / extérieur)

L’objectif principal est de **minimiser le nombre total de breaks** dans le calendrier.

---

## 2. Variables de décision

### 2.1 Variables de match

Pour chaque équipe *i*, chaque équipe *j* (i ≠ j) et chaque journée *r* :

- `match_(i, j, r) ∈ {0,1}`

Valeur :
- `1` si l’équipe *i* reçoit l’équipe *j* à la journée *r*
- `0` sinon

Ces variables encodent à la fois :
- l’adversaire
- la journée
- le lieu (domicile / extérieur)

---

### 2.2 Variables de break

Pour chaque équipe *i* et chaque paire de journées consécutives *r* et *r+1* :

- `break_(i, r) ∈ {0,1}`

Valeur :
- `1` si l’équipe *i* joue deux matchs consécutifs au même endroit
- `0` sinon

---

## 3. Contraintes

### 3.1 Unicité des confrontations

Chaque paire d’équipes se rencontre exactement deux fois sur l’ensemble du calendrier :

- une fois avec *i* à domicile
- une fois avec *j* à domicile

Formulation :

Pour tout i < j :

Σ_r (match(i,j,r) + match(j,i,r)) = 2

---

### 3.2 Un match par équipe et par journée

À chaque journée, une équipe joue exactement un match, soit à domicile, soit à l’extérieur.

Pour toute équipe *i* et journée *r* :

Σ_j≠i match(i,j,r) + Σ_j≠i match(j,i,r) = 1

---

### 3.3 Détection des breaks

Un break est comptabilisé lorsqu’une équipe joue :
- deux matchs consécutifs à domicile (HH)
- ou deux matchs consécutifs à l’extérieur (AA)

Les variables `break_(i,r)` sont activées lorsque ces situations apparaissent entre les journées *r* et *r+1*.

---

### 3.4 Équilibre domicile / extérieur

Chaque équipe joue exactement *(n − 1)* matchs à domicile et *(n − 1)* à l’extérieur.

Pour toute équipe *i* :

Σ_r Σ_j≠i match(i,j,r) = n − 1

---

## 4. Fonction objectif

L’objectif du modèle est de **minimiser le nombre total de breaks** sur l’ensemble des équipes :

Minimiser :

Σ_i Σ_r break(i,r)

Ce critère est directement issu des travaux de Régin (2008), qui montrent que le nombre minimal de breaks est borné par *n − 2* pour *n* équipes.

---

## 5. Résolution

Le problème est résolu à l’aide du solveur **CP-SAT d’OR-Tools**, avec les paramètres suivants :

- Temps limite : 30 secondes
- Recherche parallèle activée (`num_search_workers = 10`)

Le solveur retourne une solution optimale ou faisable satisfaisant l’ensemble des contraintes.

---

## 6. Extraction et analyse de la solution

Une fois la solution trouvée :
- Le calendrier est extrait sous forme de dictionnaire `{journée → liste des matchs}`
- Des statistiques sont calculées pour chaque équipe :
  - Nombre de matchs à domicile
  - Nombre de matchs à l’extérieur
  - Nombre de breaks

Ces statistiques permettent de valider empiriquement la qualité du calendrier généré.

---

## 7. Visualisation

Le calendrier est représenté graphiquement à l’aide d’un **diagramme de Gantt** :

- Axe X : journées
- Axe Y : équipes
- Couleur verte : match à domicile
- Couleur rouge : match à l’extérieur

Cette visualisation facilite l’analyse humaine de l’alternance domicile / extérieur et la détection visuelle des breaks.

---

## 8. Limites et extensions possibles

- La taille du modèle croît quadratiquement avec le nombre d’équipes
- Pour des tournois de grande taille, des approches hybrides (CP + heuristiques) peuvent être envisagées
- Extensions possibles :
  - Contraintes de disponibilité de stades
  - Distances de déplacement
  - Fenêtres de repos
  - Multi-objectifs (équité, distances, diffusion TV)

---

## 9. Conclusion

Cette implémentation montre l’efficacité de la programmation par contraintes pour résoudre des problèmes complexes d’ordonnancement sportif, tout en conservant une forte lisibilité du modèle et une interprétabilité des solutions produites.

