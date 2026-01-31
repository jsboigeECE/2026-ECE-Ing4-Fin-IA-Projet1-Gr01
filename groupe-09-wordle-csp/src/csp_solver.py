from ortools.sat.python import cp_model

def solve_wordle_csp(possible_words, constraints):
    """
    constraints: liste de tuples (lettre, position, type_indice)
    type_indice: 'green' (correct), 'yellow' (present), 'gray' (absent)
    """
    filtered_words = []
    
    for word in possible_words:
        is_valid = True
        for letter, pos, feedback in constraints:
            if feedback == 'green' and word[pos] != letter:
                is_valid = False
            elif feedback == 'yellow' and (letter not in word or word[pos] == letter):
                is_valid = False
            elif feedback == 'gray' and letter in word:
                # Attention : gestion plus fine necessaire si la lettre est aussi verte ailleurs
                is_valid = False
        
        if is_valid:
            filtered_words.append(word)
            
    return filtered_words

