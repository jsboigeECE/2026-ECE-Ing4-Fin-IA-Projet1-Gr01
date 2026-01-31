class CSPSolver:
    def __init__(self, game):
        self.game = game

    def solve(self):
        """
        Analyse le plateau et retourne une liste d'actions sûres.
        Retourne : (liste_a_reveler, liste_a_flagger)
        """
        moves = set()   # Cases sûres à cliquer
        flags = set()   # Mines trouvées à flagger
        
        # On parcourt toutes les cases déjà révélées (nos indices)
        # On copie la liste pour éviter les erreurs de modification pendant la boucle
        for (x, y) in list(self.game.revealed):
            
            # 1. On récupère le chiffre de la case
            value = self.game.get_value(x, y)
            
            # 2. On analyse les voisins
            neighbors = self.game.get_neighbors(x, y)
            hidden_neighbors = []
            flagged_neighbors = []
            
            for nx, ny in neighbors:
                if (nx, ny) in self.game.revealed:
                    continue # Déjà ouverte, pas intéressante
                
                if (nx, ny) in self.game.flags:
                    flagged_neighbors.append((nx, ny))
                else:
                    hidden_neighbors.append((nx, ny))
            
            # S'il n'y a plus de voisins cachés, cette case est résolue
            if not hidden_neighbors:
                continue

            # --- RÈGLE 1 : Si le nombre de flags autour égale la valeur ---
            # Alors tout le reste est sûr (safe)
            if len(flagged_neighbors) == value:
                for n in hidden_neighbors:
                    if n not in self.game.flags:
                        moves.add(n)

            # --- RÈGLE 2 : Si le nombre de voisins cachés + flags égale la valeur ---
            # Alors tous les voisins cachés sont des mines
            if len(hidden_neighbors) + len(flagged_neighbors) == value:
                for n in hidden_neighbors:
                    flags.add(n)

        return list(moves), list(flags)