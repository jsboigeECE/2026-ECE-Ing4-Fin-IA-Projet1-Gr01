import pygame
import sys
from game_engine import Minesweeper
from gui import GameGUI
from csp_solver import CSPSolver

def main():
    pygame.init()
    
    # Difficulté augmentée pour tester l'intelligence
    game = Minesweeper(width=15, height=15, num_mines=30)
    gui = GameGUI(game)
    solver = CSPSolver(game)
    
    # --- CONFIGURATION AUTOMATIQUE ---
    # L'IA jouera un coup toutes les 200 millisecondes
    AI_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(AI_EVENT, 200) # Change 200 pour accélérer/ralentir
    
    running = True
    game_over = False
    win = False
    
    while running:
        # Vérification Victoire
        if len(game.revealed) + len(game.grid) == game.width * game.height:
            if not win:
                print("🏆 VICTOIRE ! Tous les pièges ont été évités.")
                win = True
                game_over = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Gestion du clic manuel (toujours actif si besoin)
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                gui.handle_click(pygame.mouse.get_pos())

            # --- INTELLIGENCE ARTIFICIELLE ---
            elif event.type == AI_EVENT and not game_over and not win:
                
                safe_moves, mines = solver.solve()
                
                # Si l'IA ne trouve rien et ne peut plus rien faire
                if not safe_moves and not mines:
                    print("🛑 L'IA est bloquée (plus de coups logiques ou probabilistes).")
                
                # Application des choix
                for x, y in mines:
                    if (x,y) not in game.flags:
                        game.flags.add((x, y))
                
                for x, y in safe_moves:
                    if (x,y) not in game.revealed:
                        is_mine = game.reveal(x, y)
                        if is_mine:
                            print(f"💀 GAME OVER ! L'IA a explosé en ({x},{y})")
                            game_over = True

        gui.draw()
        pygame.display.flip()

    pygame.quit()
    sys.exit()
if __name__ == "__main__":
    main()