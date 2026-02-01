from collections import Counter

def wordle_feedback_vjg(secret: str, guess: str) -> str:
    """
    Feedback Wordle (FR) :
      V = vert, J = jaune, G = gris
    Règles Wordle exactes, y compris doublons.
    """
    secret = secret.strip().upper()
    guess = guess.strip().upper()
    if len(secret) != 5 or len(guess) != 5:
        raise ValueError("secret et guess doivent faire 5 lettres")

    res = ["G"] * 5
    remaining = Counter(secret)

    # 1) Verts
    for i in range(5):
        if guess[i] == secret[i]:
            res[i] = "V"
            remaining[guess[i]] -= 1

    # 2) Jaunes
    for i in range(5):
        if res[i] == "V":
            continue
        ch = guess[i]
        if remaining[ch] > 0:
            res[i] = "J"
            remaining[ch] -= 1

    return "".join(res)


def solve_wordle_csp(possible_words, attempts):
    """
    Solver Wordle exact basé sur des tentatives (non-plat).

    possible_words: iterable de mots 5 lettres (dictionnaire)
    attempts: liste de tentatives [(guess, feedback), ...]
      - guess: str de 5 lettres
      - feedback: str de 5 chars parmi V/J/G (V=vert, J=jaune, G=gris)

    Retour: liste des mots du dictionnaire compatibles avec toutes les tentatives.
    """
    # --- nettoyage / validation attempts ---
    cleaned_attempts = []
    for item in attempts:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        guess, fb = item
        if not isinstance(guess, str) or not isinstance(fb, str):
            continue

        guess = guess.strip().upper()
        fb = fb.strip().upper()

        if len(guess) != 5 or len(fb) != 5:
            continue
        if any(c not in "VJG" for c in fb):
            continue
        if any(not ("A" <= ch <= "Z") for ch in guess):
            continue

        cleaned_attempts.append((guess, fb))

    # --- filtrage dictionnaire ---
    solutions = []
    for w in possible_words:
        w = w.strip().upper()
        if len(w) != 5:
            continue

        ok = True
        for guess, fb in cleaned_attempts:
            if wordle_feedback_vjg(w, guess) != fb:
                ok = False
                break

        if ok:
            solutions.append(w)

    return solutions