"""
Exemple complet : analyse du risque d'un portefeuille de quatre actions françaises.

Lancer depuis le dossier du projet :
    python exemple.py

Le script télécharge les prix, calcule le bilan risque / performance,
l'affiche, et enregistre le graphique dans figures/.
"""

from pathlib import Path

from src.analyse import afficher_bilan, analyser_portefeuille, tableau_markdown
from src.donnees import charger_prix_yahoo, rendements_portefeuille, rendements_simples
from src.format_fr import pct
from src.visualisation import tracer_distribution

# ---------------------------------------------------------------------------
# Paramètres de l'analyse — c'est ici qu'on change le portefeuille étudié
# ---------------------------------------------------------------------------
PORTEFEUILLE = {
    "TTE.PA": 0.25,  # TotalEnergies — énergie
    "MC.PA": 0.25,   # LVMH — luxe
    "SAN.PA": 0.25,  # Sanofi — santé
    "AIR.PA": 0.25,  # Airbus — aéronautique
}
DEBUT = "2020-01-01"      # inclut le krach du Covid de mars 2020
CONFIANCE = 0.99
TAUX_SANS_RISQUE = 0.02   # hypothèse : taux court terme annuel en euros, à ajuster
CAPITAL = 10_000          # en euros


def main():
    prix = charger_prix_yahoo(list(PORTEFEUILLE), debut=DEBUT)
    rendements = rendements_simples(prix)
    rp = rendements_portefeuille(rendements, PORTEFEUILLE)

    bilan = analyser_portefeuille(rp, CONFIANCE, TAUX_SANS_RISQUE, CAPITAL)

    print("Portefeuille :", ", ".join(f"{t} ({pct(w, 0)})" for t, w in PORTEFEUILLE.items()))
    afficher_bilan(bilan)

    dossier = Path(__file__).parent / "figures"
    dossier.mkdir(exist_ok=True)
    chemin = dossier / "distribution_rendements.png"
    tracer_distribution(
        rp,
        bilan["var_historique"],
        bilan["expected_shortfall"],
        CONFIANCE,
        chemin,
        titre="Portefeuille équipondéré TTE · MC · SAN · AIR — rendements quotidiens",
    )
    print(f"\nGraphique enregistré : {chemin}")

    print("\nTableau à copier dans le README :\n")
    print(tableau_markdown(bilan))


if __name__ == "__main__":
    main()
