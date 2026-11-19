"""Prétraitement NON destructif.

Règle : on ne supprime ni liens, ni chiffres, ni ponctuation, ni majuscules.
Ces signaux sont précisément ceux qui distinguent une fraude d'un message
légitime. La normalisation ci-dessous est *douce* : elle sert uniquement à
alimenter les modèles de texte, pas à jeter de l'information.
"""
import unicodedata
import re

_ZERO_WIDTH_RE = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff]")


def remove_zero_width(text: str) -> str:
    """Retire les caractères invisibles (utilisés en obfuscation)."""
    return _ZERO_WIDTH_RE.sub("", text)


def normalize_light(text: str) -> str:
    """Normalisation douce pour les modèles TF-IDF / embeddings.

    - Forme Unicode NFKC (unifie les homoglyphes de compatibilité)
    - Suppression des caractères zero-width
    - Passage en minuscules
    - On NE TOUCHE PAS aux liens, chiffres, ponctuation.
    """
    text = unicodedata.normalize("NFKC", text)
    text = remove_zero_width(text)
    return text.lower()