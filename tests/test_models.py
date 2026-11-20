import numpy as np
from src.models import build_b2, build_b3, predict_scores

def test_b2_reproducible():
    m1 = build_b2()
    m2 = build_b2()
    X = ["test 1", "test 2"]
    y = [0, 1]
    m1.fit(X, y)
    m2.fit(X, y)
    # Les scores doivent être identiques (même random_state)
    assert np.allclose(m1.predict_proba(X), m2.predict_proba(X))

def test_b3_fit_predict():
    m = build_b3()
    X = ["bonjour", "gain 5000", "test"]
    y = [0, 1, 0]
    m.fit(X, y)
    scores = predict_scores("B3", m, X)
    assert len(scores) == 3
    assert np.all(scores >= 0) and np.all(scores <= 1)