"""
Petites fonctions d'affichage à la française : virgule décimale, espace avant « % »
et espace comme séparateur de milliers (6,78 % ; 10 000 €).
"""


def pct(x, decimales=2):
    """0.0678 → '6,78 %'"""
    return f"{x * 100:.{decimales}f} %".replace(".", ",").replace("-", "−")


def euros(x):
    """10000 → '10 000 €'"""
    return f"{x:,.0f} €".replace(",", " ").replace("-", "−")


def nombre(x, decimales=2):
    """0.4012 → '0,40'"""
    return f"{x:.{decimales}f}".replace(".", ",").replace("-", "−")
