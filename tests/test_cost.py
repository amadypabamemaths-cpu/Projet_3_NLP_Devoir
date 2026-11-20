from src.cost import expected_cost, choose_threshold

def test_fn_costs_more_than_fp():
    y_true = [1, 0]
    # Cas 1 : FN (prédit 0 pour un vrai 1)
    y_score_fn = [0.0, 0.0]
    # Cas 2 : FP (prédit 1 pour un vrai 0)
    y_score_fp = [1.0, 1.0]
    cost_fn = expected_cost(y_true, y_score_fn, threshold=0.5, cost_fn=20, cost_fp=1)
    cost_fp = expected_cost(y_true, y_score_fp, threshold=0.5, cost_fn=20, cost_fp=1)
    assert cost_fn > cost_fp  # 20 * 1 > 1 * 1

def test_choose_threshold_range():
    y_true = [0, 1, 0, 1]
    y_score = [0.1, 0.9, 0.2, 0.8]
    t = choose_threshold(y_true, y_score)
    assert 0.0 <= t <= 1.0