"""
Tests : chaque formule est vérifiée sur un cas dont on connaît la réponse
à l'avance (calcul à la main, ou propriété mathématique de la loi normale).

Lancer avec :  python -m pytest
"""

import numpy as np
import pandas as pd
import pytest
from scipy.stats import norm

from src.donnees import rendements_portefeuille, rendements_simples
from src.performance import drawdown_maximal, rendement_annualise, ratio_sharpe
from src.risque import expected_shortfall, var_gaussienne, var_historique, volatilite_annualisee


@pytest.fixture
def rendements_normaux():
    """250 000 rendements tirés d'une loi normale : moyenne 0,05 %, écart-type 1 %."""
    generateur = np.random.default_rng(0)
    return pd.Series(generateur.normal(0.0005, 0.01, size=250_000))


# --- Données -----------------------------------------------------------------

def test_rendements_simples_calcul_a_la_main():
    """100 → 102 → 99 donne +2 % puis −2,94 %, et la ligne vide disparaît."""
    r = rendements_simples(pd.Series([100.0, 102.0, 99.0]))
    assert len(r) == 2
    assert r.iloc[0] == pytest.approx(0.02)
    assert r.iloc[1] == pytest.approx(-3 / 102)


def test_rendement_portefeuille_moyenne_ponderee():
    rendements = pd.DataFrame({"A": [0.01, -0.02], "B": [0.03, 0.04]})
    rp = rendements_portefeuille(rendements, {"A": 0.6, "B": 0.4})
    assert rp.iloc[0] == pytest.approx(0.6 * 0.01 + 0.4 * 0.03)
    assert rp.iloc[1] == pytest.approx(0.6 * -0.02 + 0.4 * 0.04)


def test_poids_qui_ne_somment_pas_a_un():
    rendements = pd.DataFrame({"A": [0.01], "B": [0.02]})
    with pytest.raises(ValueError):
        rendements_portefeuille(rendements, {"A": 0.5, "B": 0.6})


# --- Risque ------------------------------------------------------------------

def test_volatilite_regle_de_la_racine(rendements_normaux):
    """σ journalière de 1 % → σ annuelle de 1 % × √252 ≈ 15,9 %."""
    assert volatilite_annualisee(rendements_normaux) == pytest.approx(0.01 * np.sqrt(252), rel=0.01)


def test_var_gaussienne_formule_fermee(rendements_normaux):
    """La VaR gaussienne doit valoir exactement −(μ + z·σ)."""
    mu, sigma = rendements_normaux.mean(), rendements_normaux.std()
    attendu = -(mu + norm.ppf(0.01) * sigma)
    assert var_gaussienne(rendements_normaux, 0.99) == pytest.approx(attendu)


def test_var_historique_proche_de_la_gaussienne_sur_donnees_normales(rendements_normaux):
    """Si les données sont VRAIMENT normales, les deux méthodes doivent concorder."""
    assert var_historique(rendements_normaux, 0.99) == pytest.approx(
        var_gaussienne(rendements_normaux, 0.99), rel=0.02
    )


def test_expected_shortfall_superieure_a_la_var(rendements_normaux):
    """L'ES est une moyenne de pertes toutes au-delà de la VaR : elle est forcément plus grande."""
    assert expected_shortfall(rendements_normaux, 0.99) > var_historique(rendements_normaux, 0.99)


def test_var_augmente_avec_la_confiance(rendements_normaux):
    assert (
        var_historique(rendements_normaux, 0.95)
        < var_historique(rendements_normaux, 0.99)
        < var_historique(rendements_normaux, 0.999)
    )


# --- Performance -------------------------------------------------------------

def test_rendement_annualise_composition():
    """+1 % par jour pendant 252 jours compose à 1,01²⁵² − 1."""
    assert rendement_annualise(pd.Series([0.01] * 252)) == pytest.approx(1.01**252 - 1)


def test_sharpe_non_defini_sans_volatilite():
    """Série constante : pas de volatilité, le Sharpe n'existe pas (et ne doit pas exploser)."""
    assert np.isnan(ratio_sharpe(pd.Series([0.001] * 100)))


def test_drawdown_trajectoire_a_la_main():
    """1 → 1,10 → 0,55 → 0,66 : sommet à 1,10, creux à 0,55, soit −50 %."""
    chute = drawdown_maximal(pd.Series([0.10, -0.50, 0.20]))
    assert chute["drawdown_max"] == pytest.approx(-0.50)
    assert chute["date_sommet"] == 0
    assert chute["date_creux"] == 1
