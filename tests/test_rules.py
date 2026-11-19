from src.rules import rule_score


def test_fraud_scores_high():
    score, reasons = rule_score(
        "Félicitations ! Vous avez gagné 500 000 FCFA. "
        "Envoyez 5 000 FCFA au 77 111 22 33."
    )
    assert score >= 0.4
    assert "felicitations" in reasons
    assert "montant" in reasons


def test_legit_conversation_scores_low():
    score, _ = rule_score("Salut, on se voit à 19h ce soir ?")
    assert score < 0.3


def test_code_request_dominates():
    score, reasons = rule_score("Envoyez votre code PIN au 77 111 22 33")
    assert "demande_code" in reasons
    assert score >= 0.30


def test_score_bounded():
    score, _ = rule_score(
        "URGENT ! Félicitations ! Envoyez votre code PIN au 77 XX XX XX XX. "
        "Cliquez http://bit.ly/xx et payez 5 000 FCFA."
    )
    assert 0.0 <= score <= 1.0