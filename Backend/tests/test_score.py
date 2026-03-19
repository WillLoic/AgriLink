import pytest
from datetime import datetime, timedelta
from services.score import ScoreModels

# On crée une petite classe "FakeScan" pour simuler l'objet de la DB
class FakeScan:
    def __init__(self, facteur, jours_decalage):
        self.facteur_sante = facteur
        self.date_analyse = datetime.now() + timedelta(days=jours_decalage)

def test_score_punitif_un_seul_scan():
    engine = ScoreModels()
    # 1 scan à 80% (0.8)
    scans = [FakeScan(0.8, 0)]
    
    # Résultat attendu : (0.8 * 100) * 0.25 = 20
    assert engine.logic_core(scans) == 20

def test_score_intervalle_trop_court():
    engine = ScoreModels()
    # 2 scans à 100% mais le même jour (un seul sera qualifié)
    scans = [FakeScan(1.0, 0), FakeScan(1.0, 0.1)] 
    
    # Résultat attendu : Un seul qualifié -> (1.0 * 100) * 0.25 = 25
    assert engine.logic_core(scans) == 25

def test_score_confiance_maximale():
    engine = ScoreModels()
    # 4 scans à 100% espacés de 6 jours chacun
    scans = [
        FakeScan(1.0, 0), 
        FakeScan(1.0, 6), 
        FakeScan(1.0, 12), 
        FakeScan(1.0, 18)
    ]
    
    # Résultat attendu : 4 qualifiés -> (1.0 * 100) * 1.0 = 100
    assert engine.logic_core(scans) == 100