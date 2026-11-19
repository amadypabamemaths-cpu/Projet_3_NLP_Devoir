# %% [markdown]
# # Projet 3 — Détection de messages frauduleux
# Notebook principal (Phase 1 : fondation).
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
# ## Cellules 7 à 14 — Modèles (Phase 2, à venir)
# Cette section recevra :
# - B2 : TF-IDF mots 1–2 + LR
# - B3 : TF-IDF caractères 2–5 + LR
# - M1 : embeddings multilingues + LR
# - M2 (option) : DistilBERT multilingue
# - Comparaison, seuil par coût, évaluation sur le test gelé.
# En attendant, ces cellules sont des stubs exécutables.

# %%
print("[Phase 2] Modèles non encore implémentés.")
print("Voir src/models.py et src/cost.py (livrés en Phase 2).")

# %% [markdown]
# ## Cellules 15 à 18 — Évasion, erreurs, démo, LLM (Phase 3)
# Test d'évasion, analyse d'erreurs, app Gradio, alerte LLM.
# En attendant, stub.

# %%
print("[Phase 3] Évasion, analyse d'erreurs, démo, LLM (livrés en Phase 3).")

# %% [markdown]
# ## Cellule 19 — Bilan critique (Phase 4, rapport)

# %%
print("[Phase 4] Bilan critique à rédiger dans report/rapport.md.")