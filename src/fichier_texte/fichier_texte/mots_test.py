import os
import unicodedata
import re

# --- CONFIGURATION ---
# Ton dossier spécifique
DOSSIER_TRAVAIL = r"C:\Users\antoi\OneDrive\Documents\ING4\S2\IA\fichier_texte"
NOM_FICHIER_DICO = "mots.txt"
NOM_DOSSIER_TEST = "donnee test"

class DictionaryHandler:
    def __init__(self):
        # Stocke les mots par longueur: { 3: ["ANI", "BOL"], 4: ["GARE"] }
        self.words_by_length = {}
        # Mapping Alphabet -> Entier (A=0, B=1...) pour le solveur plus tard
        self.char_map = {chr(i): i - 65 for i in range(65, 91)} 

    def _clean_word(self, word):
        """
        Nettoie le mot : Enlève les accents, met en majuscules, garde seulement A-Z.
        Exemple : "Fête" -> "FETE"
        """
        # 1. Séparer les accents des lettres (ex: 'é' devient 'e' + '´')
        nfkd_form = unicodedata.normalize('NFKD', word)
        # 2. Garder uniquement les caractères de base (ASCII)
        only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
        # 3. Tout mettre en majuscule
        upper_word = only_ascii.upper()
        # 4. Sécurité : virer tout ce qui n'est pas une lettre (espaces, tirets...)
        clean_word = re.sub(r'[^A-Z]', '', upper_word)
        return clean_word

    def load_from_file(self, full_path):
        """Lit le fichier texte et range les mots en mémoire."""
        if not os.path.exists(full_path):
            print(f"ERREUR : Le fichier {full_path} n'existe pas.")
            return

        print(f"--- Lecture du fichier : {full_path} ---")
        count = 0
        
        with open(full_path, 'r', encoding='utf-8') as f:
            for line in f:
                raw_word = line.strip()
                if not raw_word: continue
                
                # Nettoyage
                cleaned = self._clean_word(raw_word)
                
                # On ignore les mots trop courts (< 2 lettres)
                if len(cleaned) < 2: continue
                
                # Rangement par longueur
                length = len(cleaned)
                if length not in self.words_by_length:
                    self.words_by_length[length] = []
                
                # On évite les doublons
                if cleaned not in self.words_by_length[length]:
                    self.words_by_length[length].append(cleaned)
                    count += 1
        
        print(f"SUCCÈS : {count} mots chargés et nettoyés.")

    def display_sample(self):
        """Affiche ce qu'on a en mémoire pour vérifier."""
        print("\n--- Contenu du Dictionnaire (Mémoire) ---")
        for length in sorted(self.words_by_length.keys()):
            mots = self.words_by_length[length]
            print(f"Longueur {length} ({len(mots)} mots) : {mots}")

    def save_to_file(self, output_path):
        """Sauvegarde le dictionnaire organisé par longueur dans un fichier txt."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for length in sorted(self.words_by_length.keys()):
                mots = self.words_by_length[length]
                line = f"Longueur {length} ({len(mots)} mots) : {mots}\n"
                f.write(line)
        print(f"\nFichier sauvegardé : {output_path}")

# --- FONCTION UTILITAIRE POUR CRÉER UN FICHIER TEST ---
def creer_fichier_test(chemin_complet):
    """Crée un fichier avec des mots 'sales' (accents, minuscules) pour tester le nettoyage."""
    contenu_test = """
    été
    fête
    noël
    rat
    art
    tarte
    tâte
    âme
    Python
    """
    # Écriture du fichier seulement s'il n'existe pas déjà
    if not os.path.exists(chemin_complet):
        with open(chemin_complet, 'w', encoding='utf-8') as f:
            f.write(contenu_test.strip())
        print(f"Fichier de test créé : {chemin_complet}")
    else:
        print(f"Le fichier existe déjà, on l'utilise : {chemin_complet}")

# --- MAIN (EXÉCUTION) ---
if __name__ == "__main__":
    # 1. Construction du chemin complet
    dossier_test = os.path.join(DOSSIER_TRAVAIL, NOM_DOSSIER_TEST)
    
    if not os.path.exists(dossier_test):
        os.makedirs(dossier_test)
        print(f"Dossier créé : {dossier_test}")

    chemin_fichier = os.path.join(dossier_test, NOM_FICHIER_DICO)
    
    # 2. Création des fausses données pour tester
    creer_fichier_test(chemin_fichier)
    
    # 3. Utilisation de notre classe
    dico_handler = DictionaryHandler()
    dico_handler.load_from_file(chemin_fichier)
    
    # 4. Vérification visuelle
    dico_handler.display_sample()
    
    # 5. Sauvegarde dans un nouveau fichier txt
    chemin_sortie = os.path.join(dossier_test, "mots_organises.txt")
    dico_handler.save_to_file(chemin_sortie)