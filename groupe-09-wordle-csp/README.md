
# Wordle AI Solver (CSP + LLM)

Ce projet est un solveur intelligent pour le jeu Wordle. Il utilise une approche hybride: un algorithme de filtrage strict (CSP) pour éliminer les mots impossibles, et un modèle de langage (Llama 3.1 via Ollama) pour choisir le meilleur mot parmi les options restantes.

## Fonctionnement

Le solveur fonctionne en trois étapes clés :

1.  **Extraction (LLM)** : L'IA interprète le texte (ex: "Le P est gris en position 0, le R est jaune en position 4") pour extraire les indices de couleur. 
2. **Filtrage (CSP)**: Un algorithme de résolution de contraintes parcourt le dictionnaire et ne garde que les mots qui respectent strictement les positions vertes et jaunes, ainsi que les lettres grises.
3.  **Décision (LLM)** : L'IA analyse la liste des mots restants et sélectionne le plus pertinent en fonction de la fréquence d'utilisation en anglais et de la variété des lettres.
    

## Installation

### 1. Prérequis
 - Python 3.8+ 
 - Ollama installé et configuré.
    
Installation de Ollama :
 - Aller sur le site [ollama.com](http://ollama.com)
 - Télécharger le modèle Llama 3.1 : ollama pull llama3.1
    
### 2. Créer l’environnement virtuel
Pour Windows :  python -m venv venv
Quand on ouvre un nouveau Terminal : venv\Scripts\activate

### 3. Dépendances Python
Installer les bibliothèques nécessaires :
 - pip install keyboard

### 4. Fichier de données
Nous avons créé un fichier d’environ 22000 mots anglais de 5 lettres à partir d’un fichier contenant la plupart des mots anglais. Nous avons ensuite gardé les mots de 5 lettres sans caractères spéciaux tels que “-” ou “ '”
