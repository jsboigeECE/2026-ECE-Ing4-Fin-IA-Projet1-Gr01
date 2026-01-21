import os
import random
import ast
import webbrowser
import time
from grid_structure import GridStructure

try:
    from ortools.sat.python import cp_model
except ImportError:
    cp_model = None

# --- CONFIGURATION ---
# Chemin absolu vers le dictionnaire généré par recuperation_dico.py
PATH_DICO = r"C:\Users\antoi\OneDrive\Documents\ING4\S2\IA\fichier_texte\donnees\grand_dico_organise.txt"

class CrosswordSolver:
    def __init__(self, grid_layout, dictionary_path):
        self.grid_layout = grid_layout
        self.structure = GridStructure(grid_layout)
        self.dictionary_path = dictionary_path
        self.words_by_length = {}
        self.solution = None
        self.start_time = 0
        
        # Chargement des données au démarrage
        self._load_dictionary()

    def _load_dictionary(self):
        """Lit le fichier dictionnaire formaté et charge les mots en mémoire."""
        if not os.path.exists(self.dictionary_path):
            print(f"ERREUR CRITIQUE : Dictionnaire introuvable ici : {self.dictionary_path}")
            return

        print("Chargement du dictionnaire en mémoire...")
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    # Format attendu : "Longueur 2 (X mots) : ['MOT1', 'MOT2']"
                    if " : " in line:
                        parts = line.split(" : ")
                        list_str = parts[1] # La partie liste ['A', 'B']
                        meta = parts[0]     # La partie "Longueur X..."
                        try:
                            length = int(meta.split()[1])
                            # ast.literal_eval transforme la string en vraie liste Python de manière sécurisée
                            words = ast.literal_eval(list_str)
                            self.words_by_length[length] = words
                        except Exception as e:
                            continue
            print(f"Dictionnaire chargé ! {len(self.words_by_length)} longueurs de mots disponibles.")
        except Exception as e:
            print(f"Erreur globale lecture dico : {e}")

    def solve(self):
        """Lance la résolution avec Google OR-Tools (CP-SAT)."""
        if cp_model is None:
            print("\n!!! ERREUR CRITIQUE !!!")
            print("La bibliothèque 'ortools' est manquante.")
            print("Installez-la avec la commande : pip install ortools")
            return

        print("Début de la résolution (Mode CP-SAT)...")
        self.start_time = time.time()
        
        # 1. Création du Modèle
        model = cp_model.CpModel()
        
        # 2. Création des Variables : Une variable par case blanche (0..25 pour A..Z)
        # On utilise un dictionnaire pour mapper (row, col) -> Variable OR-Tools
        grid_vars = {}
        for r in range(len(self.grid_layout)):
            for c in range(len(self.grid_layout[0])):
                if self.grid_layout[r][c] != '#':
                    # Chaque case est un entier entre 0 (A) et 25 (Z)
                    grid_vars[(r, c)] = model.NewIntVar(0, 25, f'cell_{r}_{c}')

        # 3. Ajout des Contraintes : Table Constraints (Mots autorisés)
        # Pour chaque emplacement de mot (slot), la suite de cases doit former un mot du dico.
        for slot in self.structure.slots:
            # On récupère les variables des cases concernées par ce mot
            slot_cells = [grid_vars[(r, c)] for r, c in slot.cells]
            
            # On récupère la liste des mots possibles pour cette longueur
            words = self.words_by_length.get(slot.length, [])
            
            if not words:
                print(f"IMPOSSIBLE : Aucun mot de longueur {slot.length} dans le dictionnaire (Slot ID {slot.id})")
                return

            # On convertit les mots (strings) en listes d'entiers (A=0, B=1...)
            # OR-Tools a besoin de données numériques
            allowed_tuples = []
            for w in words:
                # Conversion "MOT" -> [12, 14, 19]
                int_tuple = [ord(char) - 65 for char in w]
                allowed_tuples.append(int_tuple)
            
            # LA MAGIE EST ICI : On dit au solveur "Ces variables ne peuvent prendre que ces valeurs combinées"
            model.AddAllowedAssignments(slot_cells, allowed_tuples)

        # 4. Résolution
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 240.0
        solver.parameters.log_search_progress = True  # Affiche les logs détaillés dans la console
        status = solver.Solve(model)
        
        if status == cp_model.FEASIBLE or status == cp_model.OPTIMAL:
            print(f"\n=== SOLUTION TROUVÉE ({solver.WallTime():.2f}s) ===")
            
            # Reconstruction de la solution lisible (Dictionnaire ID -> Mot)
            assignment = {}
            for slot in self.structure.slots:
                # On lit la valeur numérique trouvée par le solveur pour chaque case
                word_chars = [chr(solver.Value(grid_vars[(r, c)]) + 65) for r, c in slot.cells]
                assignment[slot.id] = "".join(word_chars)
            
            self.solution = assignment
            self.print_grid(assignment)
            self.generate_html(assignment)
            
        elif status == cp_model.UNKNOWN:
            print("\n=== TEMPS ÉCOULÉ ===")
            print("Le solveur n'a pas fini dans le temps imparti.")
        else:
            print("\n=== IMPOSSIBLE DE RÉSOUDRE ===")
            print("Il n'existe aucune combinaison de mots valide pour cette grille avec ce dictionnaire.")

    def print_grid(self, assignment):
        """Affiche la grille remplie dans la console."""
        display = [list(row) for row in self.grid_layout]
        
        for slot in self.structure.slots:
            if slot.id in assignment:
                word = assignment[slot.id]
                for i, (r, c) in enumerate(slot.cells):
                    display[r][c] = word[i]
        
        print("   " + " ".join([chr(65 + i) for i in range(len(display[0]))]))
        for i, row in enumerate(display):
            print(f"{str(i + 1).rjust(2)} {' '.join(row)}")

    def generate_html(self, assignment, filename="solution_mots_croises.html"):
        """Génère une page HTML avec la grille résolue et l'ouvre."""
        # Reconstruction de la grille
        display = [list(row) for row in self.grid_layout]
        for slot in self.structure.slots:
            if slot.id in assignment:
                word = assignment[slot.id]
                for i, (r, c) in enumerate(slot.cells):
                    display[r][c] = word[i]
        
        rows = len(display)
        cols = len(display[0])

        html = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>Solution IA</title>
            <style>
                body { font-family: sans-serif; background-color: #f4f4f9; padding: 20px; }
                h1 { color: #2c3e50; }
                .container { display: flex; gap: 40px; }
                
                /* Style de la grille */
                table { border-collapse: collapse; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
                td { 
                    width: 40px; height: 40px; 
                    border: 1px solid #333; 
                    text-align: center; font-size: 20px; font-weight: bold;
                }
                .header { background-color: #ddd; font-weight: bold; color: #555; border: none; }
                .black-cell { background-color: black; }
                .white-cell { background-color: white; color: #2980b9; }
                
                /* Style des infos */
                .info-box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 400px; }
                ul { max-height: 400px; overflow-y: auto; }
                li { margin-bottom: 5px; }
            </style>
        </head>
        <body>
            <h1>Résultat de la Résolution (""" + f"{rows}x{cols}" + """)</h1>
            <div class="container">
                <div>
                    <table>
        """
        
        # En-têtes colonnes
        html += "<tr><td class='header'></td>"
        for c in range(cols):
            html += f"<td class='header'>{chr(65 + c)}</td>"
        html += "</tr>"

        # Lignes
        for r in range(rows):
            html += "<tr>"
            html += f"<td class='header'>{r + 1}</td>"
            for c in range(cols):
                char = display[r][c]
                if char == '#':
                    html += "<td class='black-cell'></td>"
                else:
                    # Si c'est une lettre, on l'affiche, sinon vide (cas d'erreur)
                    val = char if char != '.' else ''
                    html += f"<td class='white-cell'>{val}</td>"
            html += "</tr>"
        
        html += """
                    </table>
                </div>
                <div class="info-box">
                    <h2>Mots placés</h2>
                    <ul>
        """
        
        # Liste des mots placés (triés par ID pour faire propre)
        sorted_ids = sorted(assignment.keys())
        for sid in sorted_ids:
            word = assignment[sid]
            # Retrouver le slot pour avoir les infos
            slot = next(s for s in self.structure.slots if s.id == sid)
            coord = f"{chr(65 + slot.col)}{slot.row + 1}"
            direction = "Horiz." if slot.direction == 'H' else "Vert."
            html += f"<li><strong>{coord} ({direction})</strong> : {word}</li>"

        html += """
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        path = os.path.abspath(filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Visualisation générée : {path}")
        webbrowser.open(path)

if __name__ == "__main__":
    # --- TEST RAPIDE ---
    ROWS, COLS = 12, 12
    
    print(f"--- Recherche d'une grille 12x12 (24 cases noires) ---")
    
    grid_str = []
    
    while True:
        # Nombre de cases noires fixe
        nb_noires = 24
        grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
        count = 0
        
        # Placement aléatoire
        while count < nb_noires:
            r = random.randint(0, ROWS - 1)
            c = random.randint(0, COLS - 1)
            if grid[r][c] == '.':
                grid[r][c] = '#'
                count += 1
        
        # Vérification des contraintes
        current_grid_str = ["".join(row) for row in grid]
        analyseur = GridStructure(current_grid_str)
        
        nb_mots_1_lettre = sum(1 for s in analyseur.slots if s.length == 1)
        
        if nb_mots_1_lettre <= 1:
            print(f"Grille trouvée : {nb_noires} cases noires, {nb_mots_1_lettre} mot(s) de 1 lettre.")
            grid_str = current_grid_str
            break
    
    # Résolution
    solver = CrosswordSolver(grid_str, PATH_DICO)
    solver.solve()