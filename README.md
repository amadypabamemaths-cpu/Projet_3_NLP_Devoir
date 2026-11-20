# 🛡️ BOUCLIER ANTI-FRAUDE (FraudShield NLP)

Plateforme **local-first** d’aide à la décision face aux messages frauduleux :
phishing, arnaques financières et fraude Mobile Money. L’objectif est de fournir
un verdict clair (`SÉCURISÉ`, `SUSPECT`, `DANGEREUX`), un score de
risque et une explication lisible, sans envoyer les données à un service tiers.

> **État actuel : Version 1.0.0 (Projet NLP terminé).**
> Le projet couvre l'intégralité du cycle de vie NLP : génération et annotation des données,
> implémentation de règles métier, comparaison de modèles (TF-IDF, Embeddings),
> évaluation rigoureuse sur un jeu de test gelé (Hash SHA256), test d'évasion, 
> analyse d'erreurs et interface de démonstration interactive (Gradio).

---

## Stack Technique

| Couche | Technologie |
| --- | --- |
| Langage | Python 3.11 |
| Machine Learning | scikit-learn (TF-IDF, Régression Logistique), `sentence-transformers` |
| Traitement du texte | Expressions régulières (Regex), normalisation Unicode (NFKC) |
| Interface / Démo | Gradio (Thème sombre, Dashboard dynamique, SVG) |
| Notebook | Jupytext (`main.py` → `main.ipynb`) |
| Tests & Qualité | pytest (16 tests unitaires), Hash SHA256 (gel du test) |
| Conteneurisation | Aucune (Exécution locale-first pour garantir la reproductibilité) |

Aucun LLM externe n’est utilisé. Les modèles NLP sont entraînés et exécutés
localement ; aucun message n’est envoyé à un service tiers.

### Interface de Démonstration (Gradio)

L’interface est servie localement (par défaut sur `http://127.0.0.1:7860`) et permet 
de tester le système en temps réel. Les fonctionnalités incluent :

| Fonctionnalité | Usage |
| --- | --- |
| **Analyse de message** | Saisie d'un SMS/WhatsApp et calcul du risque en temps réel |
| **Jauge de risque** | Graphique SVG dynamique (Vert, Jaune, Rouge) indiquant la dangerosité |
| **Explications (Badges)** | Affichage des signaux détectés (ex: `[LIEN]`, `[MONTANT]`, `[URGENCE]`) |
| **Expéditeur certifié** | Option simulant un message officiel pour réduire le risque (gestion des pièges) |
| **Exemples rapides** | Boutons interactifs (Faux gain, Faux agent, Piège, Légitime) pour tester en 1 clic |

---

## Architecture NLP & Modules

Le code est séparé en modules étanches pour garantir la testabilité et la reproductibilité :

*   `src/data_io.py` : Chargement des données UCI, génération des corpus locaux et vérification du Hash du test.
*   `src/features.py` : Extraction des indices (URL, montants, codes secrets, ratio de majuscules).
*   `src/rules.py` : Moteur de règles (Baseline B1) avec score additif et explicabilité.
*   `src/models.py` : Entraînement des modèles B2 (TF-IDF mots), B3 (TF-IDF caractères) et M1 (Embeddings).
*   `src/cost.py` : Calcul du seuil métier optimal selon le coût des erreurs (FN/FP).
*   `notebooks/main.py` : Notebook principal (jupytext) exécutable de haut en bas.
*   `app/gradio_app.py` : Interface web de démonstration.

### Protocole d'Évaluation (Test Gelé)

Pour garantir l'honnêteté scientifique, le jeu de test (150 messages, dont 10 "pièges") a été
**gelé** en fin de semaine 1. Son empreinte numérique (`cb97cbd5...`) est vérifiée à chaque
exécution. Si le fichier est modifié manuellement, le script lève une erreur `RuntimeError`.

---

## Modèles et Résultats

Nous avons comparé quatre approches, avec une gestion stricte du déséquilibre des classes.

1.  **B1 (Règles)** : Score additif basé sur les Regex.
2.  **B2 (TF-IDF Mots + LR)** : N-grammes de mots (1-2). F1-macro = 0.976.
3.  **B3 (TF-IDF Caractères + LR)** : N-grammes de caractères (2-5). F1-macro = 0.990.
4.  **M1 (Embeddings + LR)** : `paraphrase-multilingual-MiniLM-L12-v2`. **Précision = 75.0 %, Rappel = 96.0 %**.

### Seuil par Coût Métier
Plutôt qu'un seuil arbitraire, le système minimise le coût espéré :
*   Faux Négatif (FN) : 20 (rater une fraude est critique).
*   Faux Positif (FP) : 1 (fausse alerte = temps d'analyste).
*   **Seuil optimal retenu** : **0.26**.

### Test d'Évasion (Robustesse)
Sur 30 messages frauduleux déguisés (`g@gné`, `W.a.v.e`, espaces) :
*   Les modèles TF-IDF (B2, B3) maintiennent un **rappel de 100 %**.
*   Le modèle d'embeddings (M1) atteint **93.3 %**.

---

## Démarrage rapide

### Prérequis
*   Python 3.11 (un environnement conda `projet3` est recommandé).
*   Aucun service externe (base de données, Redis) n'est requis.

### 1. Installation
```bash
git clone <votre-lien-github>  # ou accédez à votre dossier local
cd Projet_3_NLP_Devoir

# Créer et activer l'environnement
conda create -n projet3 python=3.11 -y
conda activate projet3

# Installer les dépendances
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .