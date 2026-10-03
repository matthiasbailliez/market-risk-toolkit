"""Assemble les mesures de risque et de performance en un bilan unique."""

from .format_fr import euros, nombre, pct
from .performance import drawdown_maximal, rendement_annualise, ratio_sharpe
from .risque import expected_shortfall, var_gaussienne, var_historique, volatilite_annualisee


def analyser_portefeuille(rendements, confiance=0.99, taux_sans_risque=0.0, capital=10_000):
    """
    Bilan risque / performance d'une série de rendements quotidiens.

    confiance        : niveau de confiance de la VaR et de l'ES (0.99 = 99 %)
    taux_sans_risque : taux annuel utilisé dans le ratio de Sharpe
    capital          : montant investi, pour exprimer les pertes en euros
    """
    var_hist = var_historique(rendements, confiance)
    var_norm = var_gaussienne(rendements, confiance)
    es = expected_shortfall(rendements, confiance)
    chute = drawdown_maximal(rendements)

    return {
        "periode": (rendements.index[0], rendements.index[-1]),
        "nombre_jours": len(rendements),
        "confiance": confiance,
        "capital": capital,
        "rendement_annualise": rendement_annualise(rendements),
        "volatilite_annualisee": volatilite_annualisee(rendements),
        "sharpe": ratio_sharpe(rendements, taux_sans_risque),
        "drawdown_max": chute["drawdown_max"],
        "date_sommet": chute["date_sommet"],
        "date_creux": chute["date_creux"],
        "var_historique": var_hist,
        "var_gaussienne": var_norm,
        "expected_shortfall": es,
    }


def afficher_bilan(bilan):
    """Affiche le bilan dans le terminal."""
    c = pct(bilan["confiance"], 0)
    k = bilan["capital"]
    debut, fin = bilan["periode"]

    print(f"Période : {debut:%d/%m/%Y} → {fin:%d/%m/%Y}  ({bilan['nombre_jours']} jours de bourse)")
    print()
    print("PERFORMANCE")
    print(f"  Rendement annualisé    : {pct(bilan['rendement_annualise']):>10}")
    print(f"  Volatilité annualisée  : {pct(bilan['volatilite_annualisee']):>10}")
    print(f"  Ratio de Sharpe        : {nombre(bilan['sharpe']):>10}")
    print(f"  Drawdown maximal       : {pct(bilan['drawdown_max']):>10}"
          f"   (du {bilan['date_sommet']:%d/%m/%Y} au {bilan['date_creux']:%d/%m/%Y})")
    print()
    print(f"RISQUE SUR UN JOUR — confiance {c}, capital de {euros(k)}")
    for nom, cle in [("VaR historique", "var_historique"),
                     ("VaR gaussienne", "var_gaussienne"),
                     ("Expected Shortfall", "expected_shortfall")]:
        print(f"  {nom:<22} : {pct(bilan[cle]):>10}   soit {euros(bilan[cle] * k):>9}")


def tableau_markdown(bilan):
    """Bilan au format tableau Markdown."""
    c = pct(bilan["confiance"], 0)
    k = bilan["capital"]
    lignes = [
        "| Mesure | Valeur |",
        "|---|---|",
        f"| Rendement annualisé | {pct(bilan['rendement_annualise'])} |",
        f"| Volatilité annualisée | {pct(bilan['volatilite_annualisee'])} |",
        f"| Ratio de Sharpe | {nombre(bilan['sharpe'])} |",
        f"| Drawdown maximal | {pct(bilan['drawdown_max'])} |",
        f"| VaR historique {c} (1 jour) | {pct(bilan['var_historique'])} — {euros(bilan['var_historique'] * k)} |",
        f"| VaR gaussienne {c} (1 jour) | {pct(bilan['var_gaussienne'])} — {euros(bilan['var_gaussienne'] * k)} |",
        f"| Expected Shortfall {c} (1 jour) | {pct(bilan['expected_shortfall'])} — {euros(bilan['expected_shortfall'] * k)} |",
    ]
    return "\n".join(lignes)
