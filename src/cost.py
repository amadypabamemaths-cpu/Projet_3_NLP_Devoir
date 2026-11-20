"""Calcul du coût métier et choix du seuil optimal."""
import numpy as np
from sklearn.metrics import recall_score, precision_score

# Coûts par défaut (FN = 20, FP = 1)
COST_FN = 20.0
COST_FP = 1.0

def expected_cost(y_true, y_score, threshold, cost_fn=COST_FN, cost_fp=COST_FP) -> float:
    """Calcule le coût espéré pour un seuil donné."""
    y_pred = (np.asarray(y_score) >= threshold).astype(int)
    fn = ((y_true == 1) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    return cost_fn * fn + cost_fp * fp

def cost_curve(y_true, y_score):
    """Retourne les seuils testés et les coûts associés."""
    thresholds = np.linspace(0, 1, 101)
    costs = np.array([expected_cost(y_true, y_score, t) for t in thresholds])
    return thresholds, costs

def choose_threshold(y_true, y_score) -> float:
    """Retourne le seuil qui minimise le coût espéré."""
    thresholds, costs = cost_curve(y_true, y_score)
    return thresholds[np.argmin(costs)]

def sensibilite_ratio(y_true, y_score):
    """Affiche le rappel et la précision pour différents ratios FN/FP."""
    print("Sensibilité au ratio de coût (rappel fraude au seuil optimal) :")
    for ratio in [5, 10, 20, 50]:
        def _ec(t): return expected_cost(y_true, y_score, t, cost_fn=ratio, cost_fp=1.0)
        thresholds = np.linspace(0, 1, 101)
        t_opt = thresholds[np.argmin([_ec(t) for t in thresholds])]
        y_pred = (np.asarray(y_score) >= t_opt).astype(int)
        r = recall_score(y_true, y_pred, zero_division=0)
        p = precision_score(y_true, y_pred, zero_division=0)
        print(f"  FN/FP={ratio:3d} → seuil={t_opt:.2f} | R={r:.3f} | P={p:.3f}")