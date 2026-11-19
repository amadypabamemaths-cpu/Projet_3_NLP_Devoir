# Projet 3 — Détection de messages frauduleux

Système d'analyse d'un message entrant : score de risque, raisons détectées, action recommandée
(laisser passer / avertir / escalader).

Projet de fin de cours NLP — DIT, 2026–2027. Équipe de 4.
Langues : français dominant, anglais et pidgin en complément.

**État de livraison** : Phase 1 — fondation (modules de base + squelette notebook).
Les phases 2 à 4 (modèles, démo, rapport) sont documentées en fin de README.

---

## 1. Cadrage métier

| Élément | Contenu |
|---|---|
| Utilisateur | Analyste fraude d'un opérateur mobile money / fintech |
| Décision supportée | Laisser passer / avertir / escalader |
| Coût FN | 20 (une fraude non détectée peut vider un compte) |
| Coût FP | 1 (quelques secondes d'attention) |
| Critères | Rappel fraude ≥ 0,85 ; F1 macro ≥ 0,80 ; part traitée auto ≥ 40 % |

---

## 2. Données

| Source | Volume | Rôle |
|---|---|---|
| SMS Spam Collection (UCI) | ~5 574 | Entraînement de départ (EN) |
| `data/local/*.jsonl` | ≥ 750 (fraudes + légitimes) | Entraînement (FR/pidgin/EN) |
| `data/test_frozen.jsonl` | 150 dont 50 fraudes, 10 pièges | Test final — **hash vérifié** |
| `data/evasion.jsonl` | 30 | Robustesse (obfuscation) |

**Aucun message privé réel.** Vérifier la licence UCI avant usage.

---

## 3. Installation et démarrage

```bash
git clone <repo> && cd projet3_fraude
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .                     # rend `src` importable partout

# Tests unitaires (rapides, sans données)
pytest tests/ -v

# Premier lancement du notebook
jupytext --to ipynb notebooks/main.py
jupyter notebook notebooks/main.ipynb
```

Au premier run, le notebook génère :
- `data/test_frozen.jsonl` (150 messages)
- `data/evasion.jsonl` (30 messages)
- et **affiche le hash SHA256 du test**. Recopier ce hash dans
  `EXPECTED_TEST_HASH` (constante dans `src/data_io.py`) et committer : le test est
  dès lors **gelé**.

---

## 4. Rôles (4 personnes)

| Personne | Propriétaire | Secondaire |
|---|---|---|
| P1 | `src/data_io.py`, `src/templates.py`, `data/local/` | Section « Données » |
| P2 | `src/features.py`, `src/preprocess.py`, `src/models.py` | Section « Méthodes » |
| P3 | `src/rules.py`, `src/cost.py`, analyse d'erreurs | Section « Résultats » |
| P4 | `app/gradio_app.py`, test d'évasion, LLM optionnel | Bilan critique |

**Règle de collaboration** : un module = un propriétaire. Les autres ouvrent des issues, ne modifient pas directement.

---

## 5. Phases suivantes

- **Phase 2** — `src/models.py`, `src/cost.py`, notebook cellules 7–14 (baselines + modèle moderne + seuil).
- **Phase 3** — `app/gradio_app.py`, analyse d'évasion, analyse d'erreurs, LLM optionnel.
- **Phase 4** — `report/rapport.md` (4–8 p.), `report/slides.md` (8 diapos), script de soutenance.

---

## 6. Éthique et reproductibilité

- Aucun message privé réel ; corpus fabriqué documenté comme tel.
- L'analyste garde la décision finale.
- `random_state=42` partout ; versions figées ; hash du test vérifié à chaque run.