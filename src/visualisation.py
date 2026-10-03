"""
Module VISUALISATION : rendre les résultats lisibles d'un coup d'œil.

Le graphique principal montre la distribution des rendements quotidiens,
avec la VaR et l'Expected Shortfall placées dessus. Les jours situés au-delà
de la VaR — la « queue gauche », ceux que ces mesures décrivent — sont
mis en évidence d'une teinte plus foncée.
"""

import matplotlib

matplotlib.use("Agg")  # permet d'enregistrer l'image sans ouvrir de fenêtre
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from .format_fr import pct

# Couleurs : une seule teinte (bleu), claire pour le corps, foncée pour la queue
FOND = "#fcfcfb"
ENCRE = "#0b0b0b"
ENCRE_SECONDAIRE = "#52514e"
GRILLE = "#e4e3df"
BLEU_CLAIR = "#86b6ef"
BLEU_FONCE = "#184f95"


def tracer_distribution(rendements, var, es, confiance, chemin, titre=None):
    """
    Histogramme des rendements quotidiens, avec la VaR et l'ES en lignes verticales.

    La VaR et l'ES étant des pertes positives, elles sont placées en −VaR et −ES
    sur l'axe des rendements.
    """
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    fig.patch.set_facecolor(FOND)
    ax.set_facecolor(FOND)

    # Histogramme : un liseré de la couleur du fond sépare les barres
    _, bords, barres = ax.hist(rendements, bins=80, color=BLEU_CLAIR, edgecolor=FOND, linewidth=1.0)

    # Les barres entièrement au-delà de la VaR passent en bleu foncé
    for bord_droit, barre in zip(bords[1:], barres):
        if bord_droit <= -var:
            barre.set_facecolor(BLEU_FONCE)

    # Repères VaR et ES, étiquetés directement sur le graphique
    hauteur = ax.get_ylim()[1]
    ax.axvline(-var, color=ENCRE_SECONDAIRE, linestyle="--", linewidth=1.5)
    ax.axvline(-es, color=ENCRE, linestyle="-", linewidth=1.5)
    ax.text(-var, hauteur * 0.92, f"  VaR {pct(confiance, 0)}\n  {pct(-var)}",
            color=ENCRE_SECONDAIRE, fontsize=9, va="top", ha="left")
    ax.text(-es, hauteur * 0.92, f"ES {pct(confiance, 0)}  \n{pct(-es)}  ",
            color=ENCRE, fontsize=9, va="top", ha="right")

    # Axes discrets
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: pct(x, 0)))
    ax.grid(axis="y", color=GRILLE, linewidth=0.8)
    ax.set_axisbelow(True)
    for cote in ("top", "right", "left"):
        ax.spines[cote].set_visible(False)
    ax.spines["bottom"].set_color(ENCRE_SECONDAIRE)
    ax.tick_params(colors=ENCRE_SECONDAIRE, labelsize=9, length=0)

    ax.set_xlabel("Rendement quotidien du portefeuille", color=ENCRE_SECONDAIRE, fontsize=10)
    ax.set_ylabel("Nombre de jours", color=ENCRE_SECONDAIRE, fontsize=10)
    ax.set_title(titre or "Distribution des rendements quotidiens", color=ENCRE,
                 fontsize=12, loc="left", pad=12)

    fig.tight_layout()
    fig.savefig(chemin, facecolor=FOND)
    plt.close(fig)
