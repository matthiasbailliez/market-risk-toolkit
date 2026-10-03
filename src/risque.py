"""
Module RISQUE : mesurer ce qu'on peut perdre.

Convention : la VaR et l'Expected Shortfall sont exprimées comme des
PERTES POSITIVES. Une VaR à 99 % de 0,023 se lit : « dans 99 % des jours,
la perte ne dépasse pas 2,3 % de la valeur du portefeuille ».
"""

import numpy as np
from scipy.stats import norm

JOURS_DE_BOURSE = 252  # nombre moyen de séances de bourse par an


def volatilite_annualisee(rendements):
    """
    Volatilité annualisée : l'écart-type des rendements, ramené à un an.

        σ_annuelle = σ_journalière × √252

    Pourquoi la racine de 252 ? Si les rendements journaliers sont
    indépendants, leurs variances s'additionnent : la variance sur 252 jours
    vaut 252 fois la variance d'un jour. L'écart-type, racine de la variance,
    est donc multiplié par √252.
    """
    return rendements.std() * np.sqrt(JOURS_DE_BOURSE)


def var_historique(rendements, confiance=0.99):
    """
    Value at Risk HISTORIQUE (aucune hypothèse sur la forme de la distribution).

    On range les rendements passés du pire au meilleur, et on lit la valeur
    sous laquelle se trouvent seulement (1 − confiance) des jours.
    Pour une confiance de 99 %, c'est le 1er centile :

        VaR = − quantile à 1 % des rendements

    Force : utilise la vraie distribution observée, queues épaisses comprises.
    Limite : ne peut pas anticiper une perte plus forte que celles déjà vues.
    """
    return -np.quantile(rendements, 1 - confiance)


def var_gaussienne(rendements, confiance=0.99):
    """
    Value at Risk PARAMÉTRIQUE, sous hypothèse de loi normale.

    On suppose que les rendements suivent une loi normale de moyenne μ et
    d'écart-type σ, estimés sur l'historique. La VaR se calcule alors par formule :

        VaR = − (μ + z · σ)

    où z est le quantile de la loi normale centrée réduite
    (z ≈ −2,33 pour une confiance de 99 %).

    Limite connue : les rendements financiers ont des queues plus épaisses
    que la loi normale. Cette VaR sous-estime donc souvent les pertes extrêmes.
    La comparer à la VaR historique permet justement de le constater.
    """
    mu = rendements.mean()
    sigma = rendements.std()
    z = norm.ppf(1 - confiance)
    return -(mu + z * sigma)


def expected_shortfall(rendements, confiance=0.99):
    """
    Expected Shortfall (ES), aussi appelée CVaR.

    La VaR dit « au-delà de quel seuil on entre dans les 1 % pires jours ».
    L'ES répond à la question suivante : « quand on y entre, combien perd-on
    EN MOYENNE ? »

        ES = − moyenne des rendements inférieurs ou égaux au quantile à 1 %

    C'est la mesure retenue par la réglementation bancaire (Bâle III, FRTB)
    à la place de la VaR, car elle tient compte de la gravité des pertes extrêmes.
    """
    seuil = np.quantile(rendements, 1 - confiance)
    pires_jours = rendements[rendements <= seuil]
    return -pires_jours.mean()
