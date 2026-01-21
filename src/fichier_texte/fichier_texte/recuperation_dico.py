import os
import urllib.request
import unicodedata
import re

# --- CONFIGURATION ---
DOSSIER_TRAVAIL = r"C:\Users\antoi\OneDrive\Documents\ING4\S2\IA\fichier_texte"
# URL d'une liste de mots français open source (environ 336k mots)
URL_DICO = "https://raw.githubusercontent.com/chrplr/openlexicon/master/datasets-info/Liste-de-mots-francais-Gutenberg/liste.de.mots.francais.frgut.txt"
NOM_FICHIER_BRUT = "grand_dico_brut.txt"
NOM_FICHIER_FINAL = "grand_dico_organise.txt"
NOM_DOSSIER_DONNEES = "donnees"

class DictionaryProcessor:
    def __init__(self):
        # Utilisation de sets pour éviter les doublons instantanément
        self.words_by_length = {}

    def _clean_word(self, word):
        """Nettoie le mot : enlève accents, majuscules, garde A-Z."""
        nfkd_form = unicodedata.normalize('NFKD', word)
        only_ascii = nfkd_form.encode('ASCII', 'ignore').decode('utf-8')
        upper_word = only_ascii.upper()
        # On ne garde que les lettres
        clean_word = re.sub(r'[^A-Z]', '', upper_word)
        return clean_word

    def process_file(self, input_path, output_path):
        print(f"--- Traitement du fichier : {input_path} ---")
        
        if not os.path.exists(input_path):
            print(f"Erreur : Le fichier {input_path} n'existe pas.")
            return

        count_total = 0
        
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                raw_word = line.strip()
                if not raw_word: continue
                
                count_total += 1
                cleaned = self._clean_word(raw_word)
                
                # On ignore les mots trop courts (< 2 lettres)
                if len(cleaned) < 2: continue
                
                length = len(cleaned)
                if length not in self.words_by_length:
                    self.words_by_length[length] = set()
                
                self.words_by_length[length].add(cleaned)

        print(f"Analyse terminée : {count_total} mots lus.")
        self._save_organized(output_path)

    def _save_organized(self, output_path):
        print(f"--- Sauvegarde dans : {output_path} ---")
        with open(output_path, 'w', encoding='utf-8') as f:
            # On trie les longueurs
            for length in sorted(self.words_by_length.keys()):
                # On convertit le set en liste triée alphabétiquement
                mots = sorted(list(self.words_by_length[length]))
                line = f"Longueur {length} ({len(mots)} mots) : {mots}\n"
                f.write(line)
        print("Sauvegarde réussie !")

def telecharger_fichier(url, chemin_destination):
    print(f"Téléchargement en cours depuis : {url}")
    try:
        urllib.request.urlretrieve(url, chemin_destination)
        print(f"Fichier téléchargé avec succès : {chemin_destination}")
        return True
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return False

if __name__ == "__main__":
    # Chemins complets
    dossier_donnees = os.path.join(DOSSIER_TRAVAIL, NOM_DOSSIER_DONNEES)
    
    if not os.path.exists(dossier_donnees):
        os.makedirs(dossier_donnees)
        print(f"Dossier créé : {dossier_donnees}")

    chemin_brut = os.path.join(dossier_donnees, NOM_FICHIER_BRUT)
    chemin_final = os.path.join(dossier_donnees, NOM_FICHIER_FINAL)

    # 1. Téléchargement du grand dictionnaire
    if telecharger_fichier(URL_DICO, chemin_brut):
        # 2. Nettoyage et organisation
        processor = DictionaryProcessor()
        processor.process_file(chemin_brut, chemin_final)