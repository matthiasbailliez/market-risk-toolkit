"""
Module PERFORMANCE : ce que le portefeuille a rapporté, au regard du risque pris.
"""

import numpy as np

JOURS_DE_BOURSE = 252

# En dessous de ce seuil, une volatilité est considérée comme nulle.
# On ne teste pas « == 0 » : sur une série constante, le calcul en virgule
# flottante renvoie un écart-type de l'ordre de 10⁻¹⁹ au lieu de 0, ce qui
# ferait exploser le ratio de Sharpe vers des valeurs absurdes.
SEUIL_VOLATILITE_NULLE = 1e-12


def rendement_annualise(rendements):
    """
    Rendement annuel moyen, en composant réellement les rendements :

        R_annuel = (Π (1 + Rₜ))^(252 / T) − 1

    où T est le nombre de jours observés. On multiplie les (1 + Rₜ) entre eux
    plutôt que d'additionner les rendements, parce que les gains se capitalisent :
    +10 % puis −10 % ne donne pas 0 %, mais 1,10 × 0,90 − 1 = −1 %.
    """
    croissance_totale = (1 + rendements).prod()
    nombre_jours = len(rendements)
    return croissance_totale ** (JOURS_DE_BOURSE / nombre_jours) - 1


def ratio_sharpe(rendements, taux_sans_risque=0.0):
    """
    Ratio de Sharpe annualisé :

        Sharpe = (R_annuel − r_f) / σ_annuelle

    Combien de rendement obtient-on au-dessus du taux sans risque r_f,
    par unité de volatilité prise ? taux_sans_risque est un taux ANNUEL
    (0.02 pour 2 %).

    Repères usuels : en dessous de 0,5 faible, autour de 1 correct,
    au-dessus de 1,5 bon. Limite : le Sharpe pénalise de la même façon
    la volatilité à la hausse et à la baisse.
    """
    volatilite = rendements.std() * np.sqrt(JOURS_DE_BOURSE)
    if volatilite < SEUIL_VOLATILITE_NULLE:
        return float("nan")
    return (rendement_annualise(rendements) - taux_sans_risque) / volatilite


def drawdown_maximal(rendements):
    """
    Drawdown maximal : la pire chute entre un sommet et le creux qui suit.

    On reconstruit la valeur du portefeuille jour après jour (en partant de 1),
    on note à chaque date le plus haut atteint jusque-là, et on mesure l'écart :

        Drawdownₜ = Valeurₜ / Plus_hautₜ − 1

    Le drawdown maximal est le plus négatif de ces écarts. C'est la mesure
    la plus « vécue » par un investisseur : combien il a perdu au pire
    moment, depuis son meilleur niveau.

    Renvoie un dictionnaire : la chute (négative), la date du sommet, la date du creux.
    """
    valeur = (1 + rendements).cumprod()
    plus_haut = valeur.cummax()
    drawdown = valeur / plus_haut - 1

    date_creux = drawdown.idxmin()
    date_sommet = valeur.loc[:date_creux].idxmax()

    return {
        "drawdown_max": drawdown.min(),
        "date_sommet": date_sommet,
        "date_creux": date_creux,
    }
