# %% [markdown]
# # Projet 3 — Détection de messages frauduleux
# Notebook principal (Phase 1 et 2).
# Exécutable de haut en bas sur Colab frais : toutes les données ont un repli.
#
# **Règle d'or** : le test est gelé en cellule 6, jamais utilisé pour régler.

# %% [markdown]
# ## Cellule 1 — Installation (Colab)
# Sur Colab frais, décommenter puis exécuter. En local après `pip install -r requirements.txt` et `pip install -e .`, inutile.

# %%
# !pip -q install "scikit-learn>=1.4" "jupytext>=1.16" 2>/dev/null || True
# !pip -q install -e . 2>/dev/null || True
print("Installation OK (décommenter au premier run Colab).")

# %% [markdown]
# ## Cellule 2 — Imports et configuration

# %%
import sys
from pathlib import Path

# Rendre `src` importable même sans `pip install -e .`
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

from src.data_io import load_all_train, get_frozen_test, get_evasion
from src.features import extract_indices
from src.rules import rule_score

SEED = 42
np.random.seed(SEED)

COST_FN = 20.0
COST_FP = 1.0

print(f"ROOT = {ROOT}")
print(f"Seed = {SEED} | COST_FN = {COST_FN} | COST_FP = {COST_FP}")

# %% [markdown]
# ## Cellule 3 — Chargement des données
# Trois jeux : train (UCI + local), test gelé, test d'évasion.
# Le premier run génère `data/test_frozen.jsonl` et affiche son hash.

# %%
train_df = load_all_train()
print(f"\nTrain : {len(train_df)} messages "
      f"({int(train_df.label.sum())} fraudes, {(train_df.label==0).sum()} légitimes)")

test_df = get_frozen_test()
evasion_df = get_evasion()
print(f"Test : {len(test_df)} | Évasion : {len(evasion_df)}")

# %% [markdown]
# ## Cellule 4 — Prétraitement : démonstration sur un exemple

# %%
example = ("URGENT ! Votre compte Wave sera suspendu. "
           "Cliquez http://bit.ly/xx et envoyez 5 000 FCFA.")
print("Message :", example)
print("\nIndices extraits :")
for k, v in extract_indices(example).items():
    print(f"  {k:20s} = {v}")
print("\nBaseline règles B1 :")
score, reasons = rule_score(example)
print(f"  score = {score:.2f}")
print(f"  raisons = {reasons}")

# %% [markdown]
# ## Cellule 5 — Petite EDA

# %%
print("Distribution des labels (train) :")
print(train_df.label.value_counts(normalize=True).rename("proportion"))
print("\nTest gelé :")
print(test_df.label.value_counts())
print("\nTest gelé — répartition par type :")
print(test_df.type.value_counts())
print("\nÉvasion :")
print(evasion_df.label.value_counts())

# %% [markdown]
# ## Cellule 6 — Split train/val + vérification du hash du test
# ⚠️ **À faire une seule fois à la fin de la semaine 1** : noter le hash affiché
# dans `EXPECTED_TEST_HASH` (`src/data_io.py`), committer, et ne plus jamais
# toucher `data/test_frozen.jsonl`.

# %%
X_train, X_val, y_train, y_val = train_test_split(
    train_df["text"], train_df["label"],
    test_size=0.2, random_state=SEED, stratify=train_df["label"],
)
X_test, y_test = test_df["text"], test_df["label"]
print(f"Train = {len(X_train)} | Val = {len(X_val)} | Test = {len(X_test)}")

from src.data_io import file_sha256, DATA
print(f"\n🔒 Hash du test gelé : {file_sha256(DATA / 'test_frozen.jsonl')}")
print("   Recopier dans EXPECTED_TEST_HASH (src/data_io.py) puis commit.")

# %% [markdown]
# ## Cellule 7 — Modèles (Phase 2)
# Baselines B2, B3, et approche moderne M1.

# %%
import time
from src.models import build_b2, build_b3, build_m1, predict_scores
from src.cost import choose_threshold, sensibilite_ratio, expected_cost
from sklearn.metrics import precision_score, recall_score, f1_score, average_precision_score, confusion_matrix

# -- Baseline B2 --
b2 = build_b2()
b2.fit(X_train, y_train)
b2_val_scores = predict_scores("B2", b2, X_val)
b2_val_pred = (b2_val_scores >= 0.5).astype(int)
print("=== B2 (TF-IDF mots + LR) ===")
print(f"P={precision_score(y_val, b2_val_pred):.3f} | R={recall_score(y_val, b2_val_pred):.3f} | F1={f1_score(y_val, b2_val_pred, average='macro'):.3f} | PR-AUC={average_precision_score(y_val, b2_val_scores):.3f}")

# -- Baseline B3 --
b3 = build_b3()
b3.fit(X_train, y_train)
b3_val_scores = predict_scores("B3", b3, X_val)
b3_val_pred = (b3_val_scores >= 0.5).astype(int)
print("\n=== B3 (TF-IDF car + LR) ===")
print(f"P={precision_score(y_val, b3_val_pred):.3f} | R={recall_score(y_val, b3_val_pred):.3f} | F1={f1_score(y_val, b3_val_pred, average='macro'):.3f} | PR-AUC={average_precision_score(y_val, b3_val_scores):.3f}")

# -- Modèle moderne M1 --
print("\nChargement et entraînement de M1 (peut prendre ~30s)...")
t0 = time.time()
m1_embedder, m1_clf = build_m1(X_train, y_train)
m1_val_scores = predict_scores("M1", (m1_embedder, m1_clf), X_val)
m1_val_pred = (m1_val_scores >= 0.5).astype(int)
print(f"\n=== M1 (Embeddings + LR) | Temps: {time.time()-t0:.1f}s ===")
print(f"P={precision_score(y_val, m1_val_pred):.3f} | R={recall_score(y_val, m1_val_pred):.3f} | F1={f1_score(y_val, m1_val_pred, average='macro'):.3f} | PR-AUC={average_precision_score(y_val, m1_val_scores):.3f}")

# %% [markdown]
# ## Cellule 8 — Seuil par coût et Évaluation finale
# Choix du seuil sur la validation, puis application sur le test gelé.

# %%
# -- Seuil par coût --
print("\n--- Choix du seuil (Modèle M1) ---")
best_t = choose_threshold(y_val, m1_val_scores)
print(f"Seuil retenu (minimise le coût FN/FP=20) : {best_t:.2f}\n")
sensibilite_ratio(y_val, m1_val_scores)

# -- Évaluation sur le TEST GELÉ --
print("\n=== ÉVALUATION SUR LE TEST GELÉ (M1) ===")
m1_test_scores = predict_scores("M1", (m1_embedder, m1_clf), X_test)
m1_test_pred = (m1_test_scores >= best_t).astype(int)

cm = confusion_matrix(y_test, m1_test_pred)
tn, fp, fn, tp = cm.ravel()
print(f"Matrice de confusion :\n{cm}")
print(f"P fraude = {precision_score(y_test, m1_test_pred):.3f}")
print(f"R fraude = {recall_score(y_test, m1_test_pred):.3f}")
print(f"Coût total = {20*fn + 1*fp:.1f} (FN={fn}, FP={fp})")

# -- Analyse des pièges --
trap_mask = (test_df["type"] == "trap").values
traps_mal_classees = ((m1_test_pred == 1) & trap_mask).sum()
print(f"\nPièges (lien+montant, légitimes) : {traps_mal_classees} / {trap_mask.sum()} classés fraude par erreur.")

# %% [markdown]
# ## Cellule 9 — Évasion, erreurs, démo, LLM (Phase 3)
# Test d'évasion, analyse d'erreurs, app Gradio, alerte LLM.
# En attendant, stub.

# %%
# %% [markdown]
# ## Cellule 9 — Test d'évasion et Sauvegarde du modèle

# %%
import joblib
from src.data_io import DATA

# -- Sauvegarde du modèle B3 pour l'application Gradio --
model_dir = DATA / "processed"
model_dir.mkdir(parents=True, exist_ok=True)
joblib.dump(b3, model_dir / "model_b3.joblib")
print("✅ Modèle B3 sauvegardé pour l'application Gradio.")

# -- Test d'évasion --
print("\n=== TEST D'ÉVASION (30 messages obfusqués) ===")
X_ev = evasion_df["text"].tolist()
y_ev = evasion_df["label"].values

b2_ev_scores = predict_scores("B2", b2, X_ev)
b3_ev_scores = predict_scores("B3", b3, X_ev)
m1_ev_scores = predict_scores("M1", (m1_embedder, m1_clf), X_ev)

# On applique le seuil de 0.5 pour comparer
for name, scores in [("B2", b2_ev_scores), ("B3", b3_ev_scores), ("M1", m1_ev_scores)]:
    pred = (scores >= 0.5).astype(int)
    r_evasion = recall_score(y_ev, pred, zero_division=0)
    print(f"Rappel {name} sur messages obfusqués : {r_evasion:.3f}")

# %% [markdown]
# ## Cellule 10 — Analyse d'erreurs (Top 10)
# Le sujet exige au moins 10 erreurs examinées et classées.

# %%
print("\n=== ANALYSE D'ERREURS SUR LE TEST GELÉ ===")
df_errors = test_df.copy()
df_errors["score"] = m1_test_scores
df_errors["pred"] = m1_test_pred

# Filtrer uniquement les erreurs
errors = df_errors[df_errors.label != df_errors.pred].copy()

def classify_cause(row):
    txt = row["text"]
    if row["label"] == 0 and row["pred"] == 1 and row["type"] == "trap":
        return "Piège (lien+montant légitime)"
    if row["label"] == 1 and ("@" in txt or "\u200b" in txt or re.search(r"\d\s\d", txt)):
        return "Obfuscation"
    if len(txt) < 30:
        return "Message trop court"
    return "Ambiguïté sémantique"

import re
errors["cause"] = errors.apply(classify_cause, axis=1)

# Affichage des 10 erreurs
sample = errors.head(10)
for idx, row in sample.iterrows():
    print(f"[{row['cause']}] Vrai: {row['label']} | Prédit: {row['pred']} (score {row['score']:.2f})")
    print(f"  Texte: {row['text'][:100]}...\n")

# %% [markdown]
# ## Cellule 11 — (Phase 4, rapport)
# Bilan critique.

# %%
print("[Phase 4] Bilan critique à rédiger dans report/rapport.md.")