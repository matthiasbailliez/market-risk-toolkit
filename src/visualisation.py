"""Graphique de la distribution des rendements, avec la VaR et l'Expected Shortfall."""

import matplotlib

matplotlib.use("Agg")  # rendu sans fenêtre
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from .format_fr import pct

FOND = "#fcfcfb"
ENCRE = "#0b0b0b"
ENCRE_SECONDAIRE = "#52514e"
GRILLE = "#e4e3df"
BLEU_CLAIR = "#86b6ef"
BLEU_FONCE = "#184f95"


def tracer_distribution(rendements, var, es, confiance, chemin, titre=None):
    """
    Histogramme des rendements quotidiens avec la VaR et l'ES en lignes verticales.
    Les barres situées au-delà de la VaR sont mises en évidence.
    """
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    fig.patch.set_facecolor(FOND)
    ax.set_facecolor(FOND)

    _, bords, barres = ax.hist(rendements, bins=80, color=BLEU_CLAIR, edgecolor=FOND, linewidth=1.0)

    for bord_droit, barre in zip(bords[1:], barres):
        if bord_droit <= -var:
            barre.set_facecolor(BLEU_FONCE)

    hauteur = ax.get_ylim()[1]
    ax.axvline(-var, color=ENCRE_SECONDAIRE, linestyle="--", linewidth=1.5)
    ax.axvline(-es, color=ENCRE, linestyle="-", linewidth=1.5)
    ax.text(-var, hauteur * 0.92, f"  VaR {pct(confiance, 0)}\n  {pct(-var)}",
            color=ENCRE_SECONDAIRE, fontsize=9, va="top", ha="left")
    ax.text(-es, hauteur * 0.92, f"ES {pct(confiance, 0)}  \n{pct(-es)}  ",
            color=ENCRE, fontsize=9, va="top", ha="right")

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
