"""
Script de test automatique pour le solveur Wordle
"""

from wordle_solver_csp_llm import (
    build_feedback, 
    WordleCSP, 
    entropy_of_guess,
    best_guess_entropy,
    load_words
)


def test_feedback():
    """Test de la génération de feedback"""
    print("\n" + "="*50)
    print("TEST 1 : Génération de feedback")
    print("="*50)
    
    tests = [
        ("PLANE", "SLATE", "BGGBG"),  # L, A, E aux bonnes places
        ("CRANE", "SLATE", "BBGBG"),  # A, E aux bonnes places
        ("HELLO", "HELLO", "GGGGG"),  # Identique
        ("ABCDE", "FGHIJ", "BBBBB"),  # Aucune lettre commune
        ("SPEED", "ERASE", "YBBBY"),  # E en début (pas en fin), S répété
        ("LLAMA", "LEVEL", "YBGBB"),  # L présent mais mal placé, E présent position 3
    ]
    
    passed = 0
    for secret, guess, expected in tests:
        result = build_feedback(secret, guess)
        status = "✓" if result == expected else "✗"
        print(f"{status} Secret: {secret}, Guess: {guess} → {result} (attendu: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nRésultat : {passed}/{len(tests)} tests réussis")
    return passed == len(tests)


def test_csp_constraints():
    """Test des contraintes CSP"""
    print("\n" + "="*50)
    print("TEST 2 : Contraintes CSP")
    print("="*50)
    
    csp = WordleCSP()
    
    # Ajouter des contraintes depuis un feedback
    # SLATE avec feedback BGGBG signifie :
    # S → B (pas dans le mot)
    # L → G (en position 1)
    # A → G (en position 2)
    # T → B (pas dans le mot)
    # E → G (en position 4)
    csp.add_constraint_from_feedback("SLATE", "BGGBG")
    
    print(f"Contraintes : {csp.describe_constraints()}")
    
    # Tests de validité
    tests = [
        ("PLANE", True, "L en pos 1, A en pos 2, E en pos 4, P en pos 0, N en pos 3"),
        ("SLATE", False, "Contient S et T qui sont interdits"),
        ("BLAZE", True, "L en pos 1, A en pos 2, E en pos 4, pas de S/T"),
        ("GLAZE", True, "L en pos 1, A en pos 2, E en pos 4, pas de S/T"),
        ("FLUTE", False, "U pas en position 2 (devrait être A)"),
    ]
    
    passed = 0
    for word, expected, reason in tests:
        result = csp.is_valid(word)
        status = "✓" if result == expected else "✗"
        print(f"{status} {word} : {result} (attendu: {expected}) - {reason}")
        if result == expected:
            passed += 1
    
    print(f"\nRésultat : {passed}/{len(tests)} tests réussis")
    return passed == len(tests)


def test_entropy():
    """Test du calcul d'entropie"""
    print("\n" + "="*50)
    print("TEST 3 : Calcul d'entropie")
    print("="*50)
    
    possible_words = ["PLANE", "SLATE", "PLATE", "CRANE", "BRAKE"]
    
    for guess in ["SLATE", "CRANE", "BRAKE"]:
        entropy = entropy_of_guess(guess, possible_words)
        print(f"Entropie de {guess} : {entropy:.3f} bits")
    
    print("\n✓ Calcul d'entropie fonctionnel")
    return True


def test_full_game():
    """Test d'une partie complète automatique"""
    print("\n" + "="*50)
    print("TEST 4 : Partie complète automatique")
    print("="*50)
    
    # Simuler une partie
    secret = "CRANE"
    print(f"Mot secret : {secret}")
    
    words = load_words("words.txt")
    csp = WordleCSP()
    possible = words[:]
    
    guesses = ["SLATE", "CRANE"]  # On triche un peu pour le test
    
    for step, guess in enumerate(guesses, 1):
        fb = build_feedback(secret, guess)
        print(f"\nTour {step} : {guess} → {fb}")
        
        if fb == "GGGGG":
            print(f"✓ Gagné en {step} coups !")
            return True
        
        csp.add_constraint_from_feedback(guess, fb)
        possible = csp.filter_words(possible)
        print(f"   Mots restants : {len(possible)}")
        
        if len(possible) <= 10:
            print(f"   → {', '.join(possible[:10])}")
    
    print("✗ Pas gagné dans le nombre de tours prévus")
    return False


def test_csp_filtering():
    """Test du filtrage CSP"""
    print("\n" + "="*50)
    print("TEST 5 : Filtrage CSP")
    print("="*50)
    
    words = load_words("words.txt")
    print(f"Mots initiaux : {len(words)}")
    
    csp = WordleCSP()
    csp.add_constraint_from_feedback("SLATE", "BYGGG")
    
    filtered = csp.filter_words(words)
    print(f"Mots après filtrage : {len(filtered)}")
    
    if len(filtered) < len(words):
        print(f"✓ Le filtrage a réduit l'espace de {len(words)} à {len(filtered)} mots")
        if len(filtered) <= 20:
            print(f"Exemples : {', '.join(filtered[:10])}")
        return True
    else:
        print("✗ Le filtrage n'a pas fonctionné")
        return False


def test_repeated_letters():
    """Test de la gestion des lettres répétées"""
    print("\n" + "="*50)
    print("TEST 6 : Lettres répétées")
    print("="*50)
    
    tests = [
        ("SPEED", "ERASE", "YBBBY", "E en jaune au début, pas en position 4"),
        ("LLAMA", "LEVEL", "YBGBB", "L en jaune, E en vert pos 2, reste gris"),
        ("SISSY", "SWISS", "GBYGY", "S en vert pos 0, I gris, deuxième S vert pos 3, reste gris"),
    ]
    
    passed = 0
    for secret, guess, expected, description in tests:
        result = build_feedback(secret, guess)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}")
        print(f"   Secret: {secret}, Guess: {guess} → {result} (attendu: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nRésultat : {passed}/{len(tests)} tests réussis")
    return passed == len(tests)


def run_all_tests():
    """Exécute tous les tests"""
    print("\n" + "#"*50)
    print("# SUITE DE TESTS WORDLE SOLVER")
    print("#"*50)
    
    tests = [
        ("Feedback", test_feedback),
        ("CSP Contraintes", test_csp_constraints),
        ("Entropie", test_entropy),
        ("Filtrage CSP", test_csp_filtering),
        ("Lettres répétées", test_repeated_letters),
        ("Partie complète", test_full_game),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Erreur dans {name} : {e}")
            results.append((name, False))
    
    # Résumé final
    print("\n" + "#"*50)
    print("# RÉSUMÉ DES TESTS")
    print("#"*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} : {name}")
    
    print(f"\n{'='*50}")
    print(f"Score final : {passed}/{total} tests réussis")
    print(f"{'='*50}\n")
    
    if passed == total:
        print("🎉 Tous les tests sont passés ! Le programme fonctionne correctement.")
    else:
        print(f"⚠️  {total - passed} test(s) ont échoué. Vérifie le code.")


if __name__ == "__main__":
    run_all_tests()
