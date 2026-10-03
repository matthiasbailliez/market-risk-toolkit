"""Mesures de performance : rendement annualisé, ratio de Sharpe, drawdown maximal."""

import numpy as np

JOURS_DE_BOURSE = 252

# Seuil plutôt que « == 0 » : sur une série constante, l'arithmétique flottante
# renvoie un écart-type de l'ordre de 1e-19, ce qui ferait exploser le Sharpe.
SEUIL_VOLATILITE_NULLE = 1e-12


def rendement_annualise(rendements):
    """Rendement annuel composé : (Π (1 + Rₜ))^(252 / T) − 1."""
    croissance_totale = (1 + rendements).prod()
    return croissance_totale ** (JOURS_DE_BOURSE / len(rendements)) - 1


def ratio_sharpe(rendements, taux_sans_risque=0.0):
    """
    Ratio de Sharpe annualisé : (R_annuel − r_f) / σ_annuelle.

    taux_sans_risque : taux annuel (0.02 pour 2 %).
    """
    volatilite = rendements.std() * np.sqrt(JOURS_DE_BOURSE)
    if volatilite < SEUIL_VOLATILITE_NULLE:
        return float("nan")
    return (rendement_annualise(rendements) - taux_sans_risque) / volatilite


def drawdown_maximal(rendements):
    """
    Pire baisse entre un plus haut et le creux suivant.

    Renvoie un dictionnaire : drawdown_max (négatif), date_sommet, date_creux.
    """
    valeur = (1 + rendements).cumprod()
    drawdown = valeur / valeur.cummax() - 1

    date_creux = drawdown.idxmin()
    date_sommet = valeur.loc[:date_creux].idxmax()

    return {
        "drawdown_max": drawdown.min(),
        "date_sommet": date_sommet,
        "date_creux": date_creux,
    }
