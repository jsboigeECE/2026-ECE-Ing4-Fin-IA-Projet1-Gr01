import pygame
import sys
import argparse  # <--- NOUVEAU : Pour gérer les arguments
from game_engine import Minesweeper
from gui import GameGUI
from csp_solver import CSPSolver

def main():
    # --- 1. GESTION DES ARGUMENTS ---
    parser = argparse.ArgumentParser(description="Démineur IA")
    parser.add_argument("--width", type=int, default=15, help="Largeur de la grille")
    parser.add_argument("--height", type=int, default=15, help="Hauteur de la grille")
    parser.add_argument("--mines", type=int, default=30, help="Nombre de mines")
    args = parser.parse_args()

    # --- 2. INITIALISATION PYGAME ---
    pygame.init()
    AI_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(AI_EVENT, 150) # Vitesse de l'IA

    def reset_game():
        """Fonction pour (re)démarrer une partie avec les paramètres choisis"""
        print(f"\n--- NOUVELLE PARTIE ({args.width}x{args.height} - {args.mines} mines) ---")
        
        # On utilise les arguments args.width, args.height, etc.
        g = Minesweeper(width=args.width, height=args.height, num_mines=args.mines)
        gui = GameGUI(g)
        s = CSPSolver(g)
        return g, gui, s

    # Initialisation première partie
    game, gui, solver = reset_game()
    
    running = True
    game_over = False
    game_status = None # "VICTOIRE" ou "DÉFAITE"

    while running:
        # Vérification Victoire
        if not game_over and len(game.revealed) + len(game.grid) == game.width * game.height:
            print("🏆 VICTOIRE ! Tous les pièges ont été évités.")
            game_over = True
            game_status = "VICTOIRE"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # --- GESTION DU RESTART (Touche R) ---
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game, gui, solver = reset_game()
                    game_over = False
                    game_status = None
            
            # --- GESTION DU CLIC MANUEL ---
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                 gui.handle_click(pygame.mouse.get_pos())
            
            # --- GESTION IA ---
            elif event.type == AI_EVENT and not game_over:
                safe, mines = solver.solve()
                
                # Appliquer les drapeaux
                for m in mines: game.flags.add(m)
                
                # Appliquer les révélations
                for s in safe:
                    if (s[0], s[1]) not in game.revealed:
                        if game.reveal(s[0], s[1]):
                            print(f"💀 GAME OVER ! L'IA a explosé en {s}")
                            game_over = True
                            game_status = "DÉFAITE"
                            # On révèle tout pour montrer les dégâts
                            game.revealed.update(game.grid)

        # Dessin (avec le statut pour le message de fin)
        gui.draw(game_status)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()