import keyboard
import sys
from llm_agent import interroger_agent_wordle

def main():
    print("--- 🧠 Wordle Solver IA (Ollama + CSP) ---")
    print("Pour quitter : Appuyez sur 'Echap' ET 'Entrée'\n")

    while True:
        # 1. Saisie utilisateur
        prompt = input("Décrivez vos indices : ").strip()

        # 2. Vérification de sortie (Touche Echap ou commande 'q')
        if keyboard.is_pressed('esc'):
            print("\nArrêt du programme... Au revoir !")
            sys.exit()

        # 3. Éviter de lancer l'IA si l'entrée est vide
        if not prompt:
            continue
        
        print("\n🤔 L'IA réfléchit...\n")
        
        try:
            reponse = interroger_agent_wordle(prompt)
            print(reponse)
        except Exception as e:
            print(f"❌ Erreur lors de l'appel à l'IA : {e}")
            
        print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    main()


