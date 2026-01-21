import tkinter as tk
import random
from grid_structure import GridStructure  # On récupère la logique de l'autre fichier

# --- CONFIGURATION ---
ROWS = 12
COLS = 12
NB_NOIRES = 24
CELL_SIZE = 40  # Taille d'une case en pixels
MARGIN = 30     # Marge pour écrire les A, B, C et 1, 2, 3

class CrosswordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Mots Croisés - IA")
        
        # Calcul de la taille de la zone de dessin
        canvas_width = COLS * CELL_SIZE + 2 * MARGIN
        canvas_height = ROWS * CELL_SIZE + 2 * MARGIN
        
        # Création de la zone de dessin (Canvas)
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#f0f0f0")
        self.canvas.pack(padx=10, pady=10)
        
        # Bouton pour régénérer une grille
        self.btn_regen = tk.Button(root, text="Générer une nouvelle grille", command=self.regenerate, font=("Arial", 12))
        self.btn_regen.pack(pady=10)
        
        # On lance une première génération
        self.regenerate()

        # Ajout d'un événement : clic gauche pour changer une case
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def generate_grid_data(self):
        """Génère la structure de données (logique identique à la version console)."""
        while True:
            # 1. Grille vide
            grid = [['.' for _ in range(COLS)] for _ in range(ROWS)]
            
            # 2. Placement aléatoire des cases noires
            count = 0
            attempts = 0
            while count < NB_NOIRES and attempts < 200:
                attempts += 1
                r = random.randint(0, ROWS - 1)
                c = random.randint(0, COLS - 1)
                if grid[r][c] == '#': continue

                # Pas de contact
                if any(0 <= r+dr < ROWS and 0 <= c+dc < COLS and grid[r+dr][c+dc] == '#' 
                       for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]):
                    continue
                
                # Max 3 sur bords
                if r in [0, ROWS-1] or c in [0, COLS-1]:
                    if sum(1 for i in range(ROWS) for j in range(COLS) if grid[i][j] == '#' and (i in [0, ROWS-1] or j in [0, COLS-1])) >= 3:
                        continue

                grid[r][c] = '#'
                count += 1

            # Vérification de la contrainte : Max 1 mot de 1 lettre
            grid_strings = ["".join(row) for row in grid]
            analyseur = GridStructure(grid_strings)
            nb_mots_1_lettre = sum(1 for s in analyseur.slots if s.length == 1)

            if count >= 5 and nb_mots_1_lettre <= 1:
                return grid

    def regenerate(self):
        """Crée une nouvelle grille et met à jour l'affichage."""
        self.grid_data = self.generate_grid_data()
        self.draw_grid()
        self.analyze_grid()

    def analyze_grid(self):
        """Utilise notre script grid_structure.py pour analyser la grille visible."""
        # Conversion de la grille (liste de listes) en format attendu (liste de strings)
        grid_strings = ["".join(row) for row in self.grid_data]
        
        # Appel de la logique existante
        print("\n" + "="*30)
        print(" NOUVELLE ANALYSE DE GRILLE ")
        print("="*30)
        analyseur = GridStructure(grid_strings)
        analyseur.print_report()

    def draw_grid(self):
        """Dessine tout : quadrillage, cases noires, lettres et chiffres."""
        self.canvas.delete("all") # On efface tout
        
        # 1. Dessiner les en-têtes de colonnes (A, B, C...)
        for c in range(COLS):
            x = MARGIN + c * CELL_SIZE + CELL_SIZE / 2
            y = MARGIN / 2
            char = chr(65 + c) # 65 = 'A'
            self.canvas.create_text(x, y, text=char, font=("Arial", 10, "bold"))

        # 2. Dessiner les en-têtes de lignes (1, 2, 3...)
        for r in range(ROWS):
            x = MARGIN / 2
            y = MARGIN + r * CELL_SIZE + CELL_SIZE / 2
            self.canvas.create_text(x, y, text=str(r + 1), font=("Arial", 10, "bold"))

        # 3. Dessiner les cases
        for r in range(ROWS):
            for c in range(COLS):
                x1 = MARGIN + c * CELL_SIZE
                y1 = MARGIN + r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                if self.grid_data[r][c] == '#':
                    # Case noire
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black", outline="gray")
                else:
                    # Case blanche
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")

    def on_canvas_click(self, event):
        """Gère le clic sur la grille pour changer manuellement une case."""
        # On ignore les clics dans la marge
        if event.x < MARGIN or event.y < MARGIN:
            return
            
        c = int((event.x - MARGIN) / CELL_SIZE)
        r = int((event.y - MARGIN) / CELL_SIZE)
        
        if 0 <= r < ROWS and 0 <= c < COLS:
            # Inversion : . devient # et # devient .
            if self.grid_data[r][c] == '.':
                self.grid_data[r][c] = '#'
            else:
                self.grid_data[r][c] = '.'
            self.draw_grid()
            # On relance l'analyse car la grille a changé
            self.analyze_grid()

if __name__ == "__main__":
    # Création de la fenêtre principale
    root = tk.Tk()
    # Lancement de l'application
    app = CrosswordApp(root)
    # Boucle infinie pour garder la fenêtre ouverte
    root.mainloop()