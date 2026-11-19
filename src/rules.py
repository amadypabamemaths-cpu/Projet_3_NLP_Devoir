"""Baseline B1 : règles + regex, score additif interprétable.

Le score et les raisons sont dérivés de `extract_indices` : il n'y a pas de
duplication de logique entre les features et les règles.
"""
from typing import List, Tuple

from src.features import extract_indices

# Poids par indice. Justification dans le rapport :
# - demande de code secret = signal le plus fort (phishing direct)
# - lien + montant + urgence = combinaison classique des arnaques mobile money
WEIGHTS = {
    "has_url":          0.25,
    "has_money":        0.15,
    "has_code_request": 0.30,
    "has_urgency":      0.15,
    "has_send_request": 0.15,
    "has_congrats":     0.10,
}
UPPER_THRESHOLD = 0.30
UPPER_WEIGHT    = 0.10

# Libellés lisibles (affichés dans la démo)
LABELS = {
    "has_url":          "lien",
    "has_money":        "montant",
    "has_code_request": "demande_code",
    "has_urgency":      "urgence",
    "has_send_request": "demande_envoi",
    "has_congrats":     "felicitations",
}


def rule_score(text: str) -> Tuple[float, List[str]]:
    """Retourne (score ∈ [0,1], raisons lisibles)."""
    idx = extract_indices(text)
    score = sum(w for k, w in WEIGHTS.items() if idx.get(k))
    reasons = [LABELS[k] for k in WEIGHTS if idx.get(k)]
    if idx["upper_ratio"] > UPPER_THRESHOLD:
        score += UPPER_WEIGHT
        reasons.append("majuscules")
    return min(score, 1.0), reasons