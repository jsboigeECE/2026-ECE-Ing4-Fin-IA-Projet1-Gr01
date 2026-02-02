
from collections import Counter, defaultdict
from math import log2
import json


# ====================================
# PARTIE 1 : CHARGEMENT DES MOTS
# ====================================
def load_words(filename="words.txt"):
    """
    Charge tous les mots de 5 lettres depuis le fichier.
    """
    with open(filename, "r", encoding="utf-8") as f:
        return [w.strip().upper() for w in f if len(w.strip()) == 5]


# ====================================
# PARTIE 2 : FEEDBACK WORDLE
# ====================================
def build_feedback(secret: str, guess: str) -> str:
    """
    Génère le feedback Wordle :
    - G (Green/Vert) : lettre correcte à la bonne position
    - Y (Yellow/Jaune) : lettre correcte mais mauvaise position
    - B (Black/Gris) : lettre absente du mot
    
    Exemple : secret="PLANE", guess="SLATE" → "BYGGG"
    """
    secret = secret.upper()
    guess = guess.upper()
    
    fb = ["B"] * 5
    secret_letters = list(secret)
    
    # Étape 1 : Marquer les verts (bonne lettre, bonne position)
    for i in range(5):
        if guess[i] == secret[i]:
            fb[i] = "G"
            secret_letters[i] = None  # Marquer comme utilisée
    
    # Étape 2 : Marquer les jaunes (bonne lettre, mauvaise position)
    for i in range(5):
        if fb[i] == "B":  # Pas encore vert
            letter = guess[i]
            # Chercher cette lettre dans les positions non utilisées
            if letter in secret_letters:
                fb[i] = "Y"
                # Retirer la première occurrence de cette lettre
                secret_letters[secret_letters.index(letter)] = None
    
    return "".join(fb)


# ====================================
# PARTIE 3 : CSP (CONSTRAINT SATISFACTION PROBLEM)
# ====================================

class WordleCSP:
    """
    Un CSP simplifié pour Wordle.
    On stocke les contraintes et on filtre les mots qui les respectent.
    """
    
    def __init__(self):
        # Contraintes sur chaque position (0 à 4)
        self.must_be = {}           # Position → Lettre obligatoire
        self.cannot_be = defaultdict(set)  # Position → Lettres interdites
        self.must_contain = set()   # Lettres qui doivent être dans le mot
        self.cannot_contain = set() # Lettres qui ne doivent PAS être dans le mot
    
    def add_constraint_from_feedback(self, guess: str, feedback: str):
        """
        Ajoute des contraintes basées sur un feedback.
        
        Exemple : guess="SLATE", feedback="BYGGG"
        - Position 0 : S n'est pas dans le mot → cannot_contain
        - Position 1 : L est dans le mot mais pas en position 1 → must_contain + cannot_be[1]
        - Position 2,3,4 : A,T,E sont aux bonnes positions → must_be
        """
        guess = guess.upper()
        feedback = feedback.upper()
        
        # Compter les lettres vertes/jaunes pour chaque lettre
        letter_status = defaultdict(lambda: {'green': 0, 'yellow': 0, 'black': 0})
        
        for i in range(5):
            letter = guess[i]
            if feedback[i] == 'G':
                letter_status[letter]['green'] += 1
            elif feedback[i] == 'Y':
                letter_status[letter]['yellow'] += 1
            else:
                letter_status[letter]['black'] += 1
        
        for i in range(5):
            letter = guess[i]
            
            if feedback[i] == 'G':
                # Vert : cette lettre doit être à cette position
                self.must_be[i] = letter
                self.must_contain.add(letter)
            
            elif feedback[i] == 'Y':
                # Jaune : cette lettre est dans le mot mais pas ici
                self.must_contain.add(letter)
                self.cannot_be[i].add(letter)
            
            else:  # B (Black)
                # Gris : cette lettre n'est pas dans le mot
                # SAUF si elle apparaît aussi en vert/jaune ailleurs
                if letter_status[letter]['green'] == 0 and letter_status[letter]['yellow'] == 0:
                    self.cannot_contain.add(letter)
                # Sinon, elle est juste pas à cette position
                self.cannot_be[i].add(letter)
    
    def is_valid(self, word: str) -> bool:
        """
        Vérifie si un mot respecte toutes les contraintes.
        """
        word = word.upper()
        
        # Vérifier les positions obligatoires
        for pos, letter in self.must_be.items():
            if word[pos] != letter:
                return False
        
        # Vérifier les positions interdites
        for pos, forbidden_letters in self.cannot_be.items():
            if word[pos] in forbidden_letters:
                return False
        
        # Vérifier les lettres obligatoires
        for letter in self.must_contain:
            if letter not in word:
                return False
        
        # Vérifier les lettres interdites
        for letter in self.cannot_contain:
            if letter in word:
                return False
        
        return True
    
    def filter_words(self, words):
        """
        Filtre une liste de mots pour ne garder que ceux qui respectent les contraintes.
        """
        return [w for w in words if self.is_valid(w)]
    
    def describe_constraints(self):
        """
        Retourne une description lisible des contraintes actuelles.
        """
        desc = []
        
        if self.must_be:
            positions = ", ".join([f"pos {pos}: {letter}" for pos, letter in sorted(self.must_be.items())])
            desc.append(f"Lettres fixées : {positions}")
        
        if self.must_contain:
            desc.append(f"Doit contenir : {', '.join(sorted(self.must_contain))}")
        
        if self.cannot_contain:
            desc.append(f"Ne doit PAS contenir : {', '.join(sorted(self.cannot_contain))}")
        
        return " | ".join(desc) if desc else "Aucune contrainte"


# ====================================
# PARTIE 4 : STRATÉGIE ENTROPIE
# ====================================

def entropy_of_guess(guess, possible_words):
    """
    Calcule l'entropie d'un mot guess.
    Plus l'entropie est élevée, plus le mot nous donne d'informations.
    """
    counts = defaultdict(int)
    n = len(possible_words)
    
    for secret in possible_words:
        fb = build_feedback(secret, guess)
        counts[fb] += 1
    
    H = 0.0
    for fb, k in counts.items():
        p = k / n
        if p > 0:
            H -= p * log2(p)
    
    return H


def best_guess_entropy(possible_words, all_words, limit=None):
    """
    Trouve le meilleur mot à jouer selon l'entropie.
    """
    candidates = possible_words if limit == "possible_only" else all_words
    
    best_word = None
    best_score = -1.0
    
    for g in candidates:
        score = entropy_of_guess(g, possible_words)
        if score > best_score:
            best_score = score
            best_word = g
    
    return best_word, best_score


# ====================================
# PARTIE 5 : INTÉGRATION LLM (SIMULATION)
# ====================================

def llm_suggest_word(csp: WordleCSP, possible_words, history):
    """
    Simule l'intégration d'un LLM qui suggère un mot.
    
    Dans une vraie implémentation, on appellerait l'API OpenAI avec function calling.
    Ici, on simule juste la logique qu'un LLM pourrait suivre.
    """
    
    # Créer un contexte pour le LLM
    context = {
        "constraints": csp.describe_constraints(),
        "remaining_words": len(possible_words),
        "history": history
    }
    
    # Stratégie LLM simulée :
    # 1. Si peu de mots restants (≤3), choisir directement
    if len(possible_words) <= 3:
        return possible_words[0], "Peu de mots restants, choix direct"
    
    # 2. Si beaucoup de mots, utiliser l'entropie
    if len(possible_words) > 10:
        word, score = best_guess_entropy(possible_words, possible_words, limit="possible_only")
        return word, f"Maximisation de l'information (entropie={score:.2f})"
    
    # 3. Sinon, chercher un mot avec lettres communes non testées
    all_letters = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    tested_letters = csp.must_contain | csp.cannot_contain
    untested_letters = all_letters - tested_letters
    
    # Trouver un mot avec beaucoup de lettres non testées
    best = None
    best_new_count = 0
    
    for word in possible_words:
        new_count = sum(1 for letter in set(word) if letter in untested_letters)
        if new_count > best_new_count:
            best_new_count = new_count
            best = word
    
    if best:
        return best, f"Exploration de nouvelles lettres ({best_new_count} lettres non testées)"
    
    return possible_words[0], "Choix par défaut"


# ====================================
# PARTIE 6 : MODE INTERACTIF
# ====================================

def interactive_solver(words):
    """
    Mode interactif où l'utilisateur entre les feedbacks.
    """
    
    # Initialisation
    csp = WordleCSP()
    possible = words[:]
    history = []
    
    print("\n")
    print("WORDLE SOLVER")
    print("="*50)
    print("\nInstructions :")
    print("- Entre le feedback en G/Y/B après chaque proposition")
    print("- G = Vert (bonne lettre, bonne position)")
    print("- Y = Jaune (bonne lettre, mauvaise position)")
    print("- B = Gris (lettre absente)")
    print("- Tape 'quit' pour arrêter\n")
    
    step = 1
    
    while True:
        # Vérifications
        if len(possible) == 0:
            print("\n❌ Plus aucune solution possible !")
            print("Le feedback était probablement incorrect.")
            return
        
        if len(possible) == 1:
            print(f"\n✅ Mot trouvé : {possible[0]}")
            return
        
        print(f"\n{'─'*50}")
        print(f"Tour {step}")
        print(f"{'─'*50}")
        
        # Afficher les contraintes actuelles
        if step > 1:
            print(f"📋 Contraintes : {csp.describe_constraints()}")
        
        print(f"🔍 Solutions possibles : {len(possible)}")
        if len(possible) <= 10:
            print(f"   → {', '.join(possible)}")
        
        # Suggestion du mot
        if step == 1:
            # Premier coup : mot fixe optimal
            guess = "SLATE"
            reason = "Mot d'ouverture optimal"
        else:
            # Utiliser le LLM simulé
            guess, reason = llm_suggest_word(csp, possible, history)
        
        print(f"\n💡 Proposition : {guess}")
        print(f"   Raison : {reason}")
        
        # Demander le feedback
        fb = input("\n➤ Feedback (G/Y/B) : ").strip().upper()
        
        if fb == "QUIT":
            print("Arrêt du programme.")
            return
        
        if len(fb) != 5 or any(ch not in "GYB" for ch in fb):
            print("⚠️  Feedback invalide ! Exemple : BYGGG")
            continue
        
        # Si on a gagné
        if fb == "GGGGG":
            print(f"\n🎉 Gagné en {step} coups ! Le mot était : {guess}")
            return
        
        # Ajouter les contraintes au CSP
        csp.add_constraint_from_feedback(guess, fb)
        
        # Filtrer les mots possibles
        possible = csp.filter_words(possible)
        
        # Enregistrer dans l'historique
        history.append({
            "step": step,
            "guess": guess,
            "feedback": fb,
            "remaining": len(possible)
        })
        
        step += 1


# ====================================
# PARTIE 7 : FONCTION PRINCIPALE
# ====================================

def main():
    """
    Point d'entrée du programme.
    """
    print("\n Chargement du dictionnaire...")
    words = load_words("words.txt")
    print(f"✓ {len(words)} mots de 5 lettres chargés\n")
    
    interactive_solver(words)


if __name__ == "__main__":
    main()
