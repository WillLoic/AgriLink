from datetime import timedelta,datetime
from models.config import Scan
from fpdf import FPDF
import io

"""class ScoreModels():
    def calculate_global_score(self, current_user):
        # 1. Récupérer les scans triés par date (du plus ancien au plus récent)
        scans = Scan.query.filter_by(parcelle_id=current_user.id).order_by(Scan.date_analyse.asc()).all()
        
        if not scans:
            return 0

        # 2. Filtrage des "Scans Qualifiés" (Intervalle de 7 jours minimum)
        scans_qualifies = []
        derniere_date = None
        INTERVALLE_MIN = timedelta(days=5) # On peut mettre 3 ou 5 jours selon ta stratégie

        for s in scans:
            if derniere_date is None or (s.date_analyse - derniere_date) >= INTERVALLE_MIN:
                scans_qualifies.append(s)
                derniere_date = s.date_analyse

        nb_qualifies = len(scans_qualifies)

        # 3. Calcul de la moyenne de santé (sur TOUS les scans ou seulement les qualifiés ?)
        # Rigueur : On prend la moyenne des qualifiés pour éviter de doper le score avec 10 scans sains le même jour
        somme_sante = sum([s.facteur_sante for s in scans_qualifies if s.facteur_sante is not None])
        moyenne_sante = somme_sante / nb_qualifies

        # 4. Multiplicateur de Constance (Pénurie de données = Petit score)
        # On est TRÈS punitif ici
        if nb_qualifies == 1:
            multiplicateur = 0.25 # "Débutant" - Trop risqué pour un prêt
        elif nb_qualifies == 2:
            multiplicateur = 0.50 # "En observation"
        elif nb_qualifies == 3:
            multiplicateur = 0.75 # "Sérieux"
        else:
            multiplicateur = 1.0  # "Profil de Confiance" (4 semaines de suivi minimum)

        score_final = (moyenne_sante * 100) * multiplicateur

        return round(min(score_final, 100))"""

class ScoreModels():
    # LE CERVEAU (La méthode à tester) : Elle ne prend qu'une liste d'objets
    def logic_core(self, scans_list):
        if not scans_list:
            return 0

        scans_qualifies = []
        derniere_date = None
        INTERVALLE_MIN = timedelta(days=5)

        for s in scans_list:
            if derniere_date is None or (s.date_analyse - derniere_date) >= INTERVALLE_MIN:
                scans_qualifies.append(s)
                derniere_date = s.date_analyse

        nb_qualifies = len(scans_qualifies)
        if nb_qualifies == 0: return 0

        somme_sante = sum([s.facteur_sante for s in scans_qualifies if s.facteur_sante is not None])
        moyenne_sante = somme_sante / nb_qualifies

        # Ta logique de multiplicateurs
        mapping = {1: 0.25, 2: 0.50, 3: 0.75}
        multiplicateur = mapping.get(nb_qualifies, 1.0)

        score_final = (moyenne_sante * 100) * multiplicateur
        return round(min(score_final, 100))

        # LE CORPS : Il va chercher les données en base
    def calculate_global_score(self, current_user):
        scans = Scan.query.filter_by(parcelle_id=current_user.id).order_by(Scan.date_analyse.asc()).all()
        if not scans:
            return 0
        
        # On délègue le calcul au cerveau
        return self.logic_core(scans)



class PDFService:
    def generate_certificat(self, user_data, score, dernier_diagnostic):
        pdf = FPDF()
        pdf.add_page()
        
        # --- EN-TÊTE ---
        pdf.set_font("Arial", "B", 20)
        pdf.set_text_color(34, 139, 34) # Vert forêt
        pdf.cell(0, 20, "AGRILINK - CERTIFICAT DE CRÉDIBILITÉ", ln=True, align="C")
        
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f"Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", ln=True, align="C")
        pdf.ln(10)

        # --- INFO AGRICULTEUR ---
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, " INFORMATIONS DE LA PARCELLE", ln=True, fill=True)
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, f" Propriétaire : {user_data.nom}", ln=True)
        pdf.cell(0, 8, f" Culture : {user_data.culture_type}", ln=True)
        pdf.cell(0, 8, f" Contact : {user_data.phone}", ln=True)
        pdf.ln(5)

        # --- LE SCORE (L'élément central) ---
        pdf.set_fill_color(34, 139, 34)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 15, f" AGRI-SCORE : {score} / 100", ln=True, align="C", fill=True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", "I", 9)
        mention = "PROFIL DE CONFIANCE" if score > 70 else "EN COURS D'OBSERVATION"
        pdf.cell(0, 8, f"Mention : {mention}", ln=True, align="C")
        pdf.ln(10)

        # --- DERNIER DIAGNOSTIC IA ---
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, " DERNIER BILAN DE SANTÉ (IA)", ln=True)
        pdf.set_font("Arial", "", 10)
        # On écrit le diagnostic (Gemini) - multi_cell pour les longs textes
        pdf.multi_cell(0, 7, f"Diagnostic : {dernier_diagnostic}")
        pdf.ln(10)

        # --- SÉCURITÉ (QR CODE Fictif pour l'instant) ---
        pdf.set_draw_color(200, 0, 0)
        pdf.set_font("Arial", "B", 8)
        pdf.cell(0, 10, "DOCUMENT INFALSIFIABLE - CONSULTABLE UNIQUEMENT VIA L'INTERFACE AGRILINK", border=1, ln=True, align="C")

        # --- SORTIE (Flux binaire) ---
        return pdf.output() # Retourne les bytes du PDF