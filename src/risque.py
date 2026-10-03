"""
Mesures de risque : volatilité, VaR, Expected Shortfall.

La VaR et l'ES sont renvoyées comme des pertes positives :
0.023 correspond à une perte de 2,3 % de la valeur du portefeuille.
"""

import numpy as np
from scipy.stats import norm

JOURS_DE_BOURSE = 252


def volatilite_annualisee(rendements):
    """Écart-type des rendements journaliers, annualisé : σ × √252."""
    return rendements.std() * np.sqrt(JOURS_DE_BOURSE)


def var_historique(rendements, confiance=0.99):
    """VaR historique : opposé du quantile (1 − confiance) des rendements observés."""
    return -np.quantile(rendements, 1 - confiance)


def var_gaussienne(rendements, confiance=0.99):
    """VaR paramétrique sous hypothèse de normalité : −(μ + z · σ)."""
    mu = rendements.mean()
    sigma = rendements.std()
    z = norm.ppf(1 - confiance)
    return -(mu + z * sigma)


def expected_shortfall(rendements, confiance=0.99):
    """Expected Shortfall : perte moyenne sur les jours situés au-delà de la VaR historique."""
    seuil = np.quantile(rendements, 1 - confiance)
    pires_jours = rendements[rendements <= seuil]
    return -pires_jours.mean()
