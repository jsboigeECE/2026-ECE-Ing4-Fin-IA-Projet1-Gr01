# Calendrier Sportif – Sports Tournament Scheduling

## Présentation du projet
Ce projet a pour objectif de générer automatiquement le calendrier d’un championnat sportif de type **round-robin aller-retour** (chaque équipe rencontre toutes les autres deux fois, une à domicile et une à l’extérieur), tout en respectant un ensemble de **contraintes réalistes** issues de la recherche opérationnelle.

Le problème est modélisé comme un **problème de satisfaction de contraintes (CSP)** et résolu à l’aide du solveur **CP-SAT d’OR-Tools**. L’optimisation porte principalement sur la **minimisation des "breaks"**, c’est-à-dire les enchaînements de matchs consécutifs joués au même endroit (deux domiciles ou deux déplacements d’affilée).

Ce projet s’inspire directement de travaux académiques reconnus en ordonnancement sportif (Régin, Schaerf) et des compétitions internationales de sports scheduling.

---

## Fonctionnalités principales
- Génération automatique d’un calendrier round-robin aller-retour
- Respect des contraintes suivantes :
  - Une équipe joue exactement un match par journée
  - Chaque paire d’équipes se rencontre exactement deux fois
  - Équilibre parfait entre matchs à domicile et à l’extérieur
  - Limitation et minimisation des breaks
- Optimisation du calendrier selon un critère global
- Affichage détaillé :
  - Calendrier par journée
  - Vue par équipe
  - Statistiques domicile / extérieur et breaks
- Visualisation graphique du calendrier sous forme de **diagramme de Gantt**

---

## Technologies utilisées
- **Python 3**
- **OR-Tools (CP-SAT)** pour la résolution par contraintes
- **Matplotlib** pour la visualisation graphique
- **NumPy** pour la gestion de données

---

## Installation

### Prérequis
- Python 3.9 ou supérieur
- Environnement virtuel recommandé (optionnel mais conseillé)

### Installation des dépendances
```bash
pip install ortools matplotlib numpy
```

---

## Lancement du projet

Le projet est autonome et peut être exécuté directement depuis le fichier principal.

```bash
python tournament_scheduler.py
```

Par défaut, le script :
1. Initialise un tournoi avec un nombre pair d’équipes
2. Résout le problème d’ordonnancement
3. Affiche le calendrier et les statistiques
4. Génère une visualisation graphique

---

## Paramétrage

Le nombre d’équipes peut être modifié dans la fonction `simple_demo()` :
```python
scheduler = TournamentScheduler(n_teams=4)
```

⚠️ Le nombre d’équipes doit être pair (une équipe fictive est ajoutée automatiquement si nécessaire).

---

## Tests et validation

Les tests sont réalisés de manière fonctionnelle via :
- La vérification automatique des contraintes (imposées par le solveur CP-SAT)
- L’affichage des statistiques finales :
  - Nombre de matchs domicile / extérieur par équipe
  - Nombre total de breaks
- L’inspection visuelle du diagramme de Gantt

Pour différents nombres d’équipes, les solutions trouvées respectent l’ensemble des contraintes et présentent un nombre de breaks minimal.

---

## Références académiques
- Régin, J.-C. (2008). *Minimizing breaks in sports schedules*
- Schaerf, A. (1999). *Sports scheduling: A survey*
- ITC 2021 – Sports Scheduling Track

---

## Auteur
Projet réalisé dans un cadre académique pour illustrer l’utilisation de la programmation par contraintes appliquée à l’ordonnancement sportif.

