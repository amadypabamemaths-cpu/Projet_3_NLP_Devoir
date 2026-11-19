"""Extraction d'indices (features) à partir d'un message.

Ces indices sont les signaux de fraude : lien, montant, demande de code,
urgence, demande d'envoi d'argent, félicitations, majuscules, ponctuation.
Ils sont calculés SANS modifier le texte brut.
"""
import re
from typing import Dict

# --- Regex (source unique) -------------------------------------------------
URL_RE = re.compile(
    r"(https?://\S+|www\.\S+|\b\S+\.(?:xyz|top|tk|ml|ga|cf|gq|bit)\b)", re.I
)
MONEY_RE = re.compile(
    r"(\d[\d\s.,]*)\s*(FCFA|F\s?CFA|CFA|XOF|€|\$|EUR|USD|F\b)", re.I
)
CODE_RE = re.compile(r"\b(code|otp|pin|mot de passe|secret)\b", re.I)
URGENCY_RE = re.compile(
    r"\b(urgent|immédiat|suspendu|bloqué|24h|48h|dernier avis|aujourd'hui)\b", re.I
)
SEND_RE = re.compile(
    r"\b(envoyez|renvoyez|transférez|payez|déposez|versez)\b", re.I
)
CONGRATS_RE = re.compile(
    r"\b(félicitations|congratulation|gagné|won)\b", re.I
)


def extract_indices(text: str) -> Dict[str, float]:
    """Retourne un dict de features binaires/numériques.

    Ne modifie jamais `text`. Utilisable par les modèles, les règles, la démo.
    """
    n_links = len(URL_RE.findall(text))
    n_chars = max(len(text), 1)
    return {
        "has_url": int(n_links > 0),
        "has_money": int(bool(MONEY_RE.search(text))),
        "has_code_request": int(bool(CODE_RE.search(text))),
        "has_urgency": int(bool(URGENCY_RE.search(text))),
        "has_send_request": int(bool(SEND_RE.search(text))),
        "has_congrats": int(bool(CONGRATS_RE.search(text))),
        "upper_ratio": sum(c.isupper() for c in text) / n_chars,
        "digit_ratio": sum(c.isdigit() for c in text) / n_chars,
        "n_exclam": text.count("!"),
        "n_links": n_links,
        "len": len(text),
    }