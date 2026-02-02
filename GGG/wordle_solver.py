from collections import Counter, defaultdict
from math import log2

# -----------------------------
# Utils dictionnaire + feedback
# -----------------------------
def load_words(filename="words.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        return [w.strip().upper() for w in f if len(w.strip()) == 5]



def build_feedback(secret: str, guess: str) -> str:
    """
    Feedback Wordle exact (G/Y/B), gère les lettres répétées.
    """
    secret = secret.upper()
    guess = guess.upper()

    fb = ["B"] * 5
    secret_count = Counter(secret)

    # Greens
    for i in range(5):
        if guess[i] == secret[i]:
            fb[i] = "G"
            secret_count[guess[i]] -= 1

    # Yellows
    for i in range(5):
        if fb[i] == "B":
            if secret_count[guess[i]] > 0:
                fb[i] = "Y"
                secret_count[guess[i]] -= 1

    return "".join(fb)


def filter_possible(possible_words, guess, feedback):
    """
    Garde uniquement les mots qui produisent exactement ce feedback.
    """
    out = []
    for w in possible_words:
        if build_feedback(w, guess) == feedback:
            out.append(w)
    return out


# -----------------------------
# Stratégie entropie
# -----------------------------
def entropy_of_guess(guess, possible_words):
    """
    Entropie attendue des feedbacks si on joue 'guess' alors que le secret
    est dans possible_words.
    """
    counts = defaultdict(int)
    n = len(possible_words)
    for secret in possible_words:
        fb = build_feedback(secret, guess)
        counts[fb] += 1

    H = 0.0
    for fb, k in counts.items():
        p = k / n
        H -= p * log2(p)
    return H


def best_guess_entropy(possible_words, all_words, limit_guesses=None):
    """
    Retourne le mot qui maximise l'entropie.
    - possible_words : secrets possibles
    - all_words : mots autorisés comme guess
    - limit_guesses : optionnel, pour accélérer (ex: tester que sur possible_words)
    """
    candidates = all_words
    if limit_guesses == "possible_only":
        candidates = possible_words

    best_word = None
    best_score = -1.0

    for g in candidates:
        score = entropy_of_guess(g, possible_words)
        if score > best_score:
            best_score = score
            best_word = g

    return best_word, best_score


# -----------------------------
# Mode interactif
# -----------------------------
def interactive_solver(words):
    possible = words[:]          # secrets possibles
    all_words = words[:]         # guesses autorisés (ici = même liste)

    print("\n=== WORDLE SOLVER (ENTROPIE) ===")
    print("Entre ton feedback en G/Y/B (ex: BYGBB).")
    print("Tape 'quit' pour arrêter.\n")

    step = 1
    while True:
        if len(possible) == 0:
            print("❌ Plus aucune solution possible (données incohérentes).")
            return

        if len(possible) == 1:
            print(f"✅ Mot trouvé : {possible[0]}")
            return

        if step == 1:
            guess = "SLATE"   # tu peux mettre "CRANE" ou "ALERT"
            score = 0.0
            print(f"[Tour {step}] Je propose : {guess} (mot fixe pour aller vite)")
        else:
            guess, score = best_guess_entropy(possible, all_words, limit_guesses="possible_only")
            print(f"[Tour {step}] Je propose : {guess}  (entropie={score:.3f})")

        fb = input("Feedback (G/Y/B) : ").strip().upper()

        if fb == "QUIT":
            return
        if len(fb) != 5 or any(ch not in "GYB" for ch in fb):
            print("⚠️ Feedback invalide. Exemple valide: BYGBB")
            continue

        possible = filter_possible(possible, guess, fb)
        print(f"→ Solutions restantes : {len(possible)}")
        if len(possible) <= 20:
            print("  ", possible)

        step += 1


def main():
    words = load_words("words.txt")
    print(f"{len(words)} mots chargés")

    interactive_solver(words)


if __name__ == "__main__":
    main()
