"""Constructeurs de modèles pour les baselines et l'approche moderne."""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from src.preprocess import normalize_light

def build_b2() -> Pipeline:
    """B2 : TF-IDF mots (1-2) + Régression Logistique."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True,
                                  preprocessor=normalize_light)),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, C=1.0, random_state=42)),
    ])

def build_b3() -> Pipeline:
    """B3 : TF-IDF caractères (2-5) + Régression Logistique."""
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True,
                                  preprocessor=normalize_light)),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, C=1.0, random_state=42)),
    ])

def build_m1(texts_train, y_train):
    """M1 : Plongements multilingues + Régression Logistique.
    Retourne (embedder, clf)."""
    from sentence_transformers import SentenceTransformer
    print("Chargement du modèle SentenceTransformer...")
    embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    print("Encodage des textes d'entraînement...")
    E_train = embedder.encode(list(texts_train), batch_size=64, show_progress_bar=False)
    print("Entraînement de la Régression Logistique...")
    clf = LogisticRegression(class_weight="balanced", max_iter=2000, C=1.0, random_state=42)
    clf.fit(E_train, y_train)
    return embedder, clf

def predict_scores(model_name: str, model_obj, texts) -> np.ndarray:
    """Retourne les scores de probabilité pour la classe 1 (fraude)."""
    if model_name == "M1":
        embedder, clf = model_obj
        E_test = embedder.encode(list(texts), batch_size=64, show_progress_bar=False)
        return clf.predict_proba(E_test)[:, 1]
    else:
        return model_obj.predict_proba(texts)[:, 1]