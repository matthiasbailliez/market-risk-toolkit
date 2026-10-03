"""
Module DONNÉES : récupérer des prix et les transformer en rendements.

C'est la porte d'entrée du projet. Tous les autres modules (risque,
performance, analyse) travaillent sur des RENDEMENTS, jamais sur des prix :
un prix n'est pas stationnaire (il dérive dans le temps), alors qu'un
rendement oscille autour d'un niveau stable, ce qui autorise les
calculs statistiques (moyenne, écart-type, quantiles).
"""

import numpy as np
import pandas as pd


def charger_prix_yahoo(tickers, debut, fin=None):
    """
    Télécharge les prix de clôture ajustés depuis Yahoo Finance.

    Paramètres
    ----------
    tickers : liste de codes, par exemple ["TTE.PA", "MC.PA"]
    debut   : date de début, par exemple "2020-01-01"
    fin     : date de fin (facultative, par défaut : aujourd'hui)

    Renvoie un tableau pandas : une ligne par date, une colonne par actif.

    « Ajustés » signifie que les prix sont corrigés des dividendes et des
    divisions d'actions. Sans cet ajustement, le versement d'un dividende
    ferait apparaître une fausse baisse de prix, donc une fausse perte.
    """
    import yfinance as yf  # importé ici : seul ce module a besoin d'internet

    brut = yf.download(tickers, start=debut, end=fin, auto_adjust=True, progress=False)
    prix = brut["Close"]

    # On ne garde que les dates où TOUS les actifs ont un prix
    return prix.dropna()


def charger_prix_csv(chemin):
    """
    Charge des prix depuis un fichier CSV : une colonne "Date", puis une colonne par actif.
    Utile pour travailler sans connexion internet.
    """
    prix = pd.read_csv(chemin, parse_dates=["Date"], index_col="Date")
    return prix.sort_index().dropna()


def rendements_simples(prix):
    """
    Rendements arithmétiques, jour après jour :

        Rₜ = (Pₜ − Pₜ₋₁) / Pₜ₋₁

    .pct_change() applique exactement cette formule à chaque ligne.
    La première ligne n'a pas de prix précédent : elle vaut NaN
    (valeur manquante), et .dropna() la supprime.
    """
    return prix.pct_change().dropna()


def rendements_log(prix):
    """
    Rendements logarithmiques :

        rₜ = ln(Pₜ / Pₜ₋₁)

    Presque identiques aux rendements simples pour de petites variations.
    Leur intérêt : ils s'additionnent dans le temps (le rendement sur
    deux jours est la somme des deux rendements journaliers).
    """
    return np.log(prix / prix.shift(1)).dropna()


def rendements_portefeuille(rendements, poids):
    """
    Rendement quotidien d'un portefeuille à poids fixes :

        Rₚ,ₜ = Σᵢ wᵢ · Rᵢ,ₜ

    C'est la moyenne pondérée des rendements des actifs, chaque jour.
    On utilise ici les rendements SIMPLES, car ce sont eux qui
    s'additionnent entre actifs.

    poids : dictionnaire {ticker: poids}, par exemple {"TTE.PA": 0.5, "MC.PA": 0.5}
            La somme des poids doit valoir 1.
    """
    somme = sum(poids.values())
    if abs(somme - 1) > 1e-6:
        raise ValueError(f"La somme des poids vaut {somme}, elle doit valoir 1.")

    # On remet les poids dans l'ordre des colonnes du tableau
    vecteur_poids = [poids[colonne] for colonne in rendements.columns]

    # Produit matriciel : pour chaque jour, Σ poids × rendement
    return rendements @ vecteur_poids
