"""Chargement des prix et calcul des rendements."""

import numpy as np
import pandas as pd


def charger_prix_yahoo(tickers, debut, fin=None):
    """
    Prix de clôture ajustés (dividendes et divisions d'actions) depuis Yahoo Finance.

    Renvoie un DataFrame : une ligne par date, une colonne par actif.
    Seules les dates où tous les actifs ont un prix sont conservées.
    """
    import yfinance as yf

    brut = yf.download(tickers, start=debut, end=fin, auto_adjust=True, progress=False)
    return brut["Close"].dropna()


def charger_prix_csv(chemin):
    """Prix depuis un CSV : une colonne « Date », puis une colonne par actif."""
    prix = pd.read_csv(chemin, parse_dates=["Date"], index_col="Date")
    return prix.sort_index().dropna()


def rendements_simples(prix):
    """Rendements arithmétiques : Rₜ = (Pₜ − Pₜ₋₁) / Pₜ₋₁."""
    return prix.pct_change().dropna()


def rendements_log(prix):
    """Rendements logarithmiques : rₜ = ln(Pₜ / Pₜ₋₁)."""
    return np.log(prix / prix.shift(1)).dropna()


def rendements_portefeuille(rendements, poids):
    """
    Rendement quotidien d'un portefeuille à poids fixes : Rₚ,ₜ = Σᵢ wᵢ · Rᵢ,ₜ

    poids : dictionnaire {ticker: poids}, dont la somme doit valoir 1.
    """
    somme = sum(poids.values())
    if abs(somme - 1) > 1e-6:
        raise ValueError(f"La somme des poids vaut {somme}, elle doit valoir 1.")

    vecteur_poids = [poids[colonne] for colonne in rendements.columns]
    return rendements @ vecteur_poids
