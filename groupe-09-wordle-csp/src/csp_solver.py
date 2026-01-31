from collections import Counter, defaultdict

def solve_wordle_csp(possible_words, constraints):
    """
    constraints : liste de tuples (lettre, position, feedback)
    feedback ∈ {'green', 'yellow', 'gray'}
    """

    green = {}
    forbidden_pos = defaultdict(set)
    min_count = defaultdict(int)
    max_count = defaultdict(lambda: 5)

    # --- Analyse des contraintes ---
    for letter, pos, fb in constraints:
        letter = letter.upper()

        if fb == 'green':
            green[pos] = letter
            min_count[letter] += 1

        elif fb == 'yellow':
            forbidden_pos[pos].add(letter)
            min_count[letter] += 1

        elif fb == 'gray':
            # si la lettre n'est jamais verte/jaune ailleurs
            if min_count[letter] == 0:
                max_count[letter] = 0
            else:
                # lettre grise mais déjà vue → limite max
                max_count[letter] = min_count[letter]

    # --- Filtrage du dictionnaire ---
    solutions = []

    for word in possible_words:
        word = word.upper()
        counts = Counter(word)
        valid = True

        # lettres vertes
        for pos, letter in green.items():
            if word[pos] != letter:
                valid = False
                break

        if not valid:
            continue

        # jaunes : pas à cette position
        for pos, letters in forbidden_pos.items():
            if word[pos] in letters:
                valid = False
                break

        if not valid:
            continue

        # occurrences min / max
        for letter in min_count:
            if counts[letter] < min_count[letter]:
                valid = False
                break

        for letter in max_count:
            if counts[letter] > max_count[letter]:
                valid = False
                break

        if valid:
            solutions.append(word)

    return solutions
