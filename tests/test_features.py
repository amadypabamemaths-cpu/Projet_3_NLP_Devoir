from src.features import extract_indices


def test_url_http():
    assert extract_indices("cliquez http://bit.ly/xx")["has_url"] == 1


def test_url_obfuscated_domain():
    assert extract_indices("voir wave-secure-verif.xyz/update")["has_url"] == 1


def test_money_fcfa():
    assert extract_indices("vous avez reçu 25 000 FCFA")["has_money"] == 1


def test_money_no_false_positive():
    # Un nombre sans devise ne doit PAS déclencher has_money
    assert extract_indices("nous sommes 25 personnes")["has_money"] == 0


def test_code_request():
    assert extract_indices("envoyez votre code PIN")["has_code_request"] == 1


def test_urgency():
    assert extract_indices("compte suspendu dans 24h")["has_urgency"] == 1


def test_upper_ratio():
    assert extract_indices("URGENT STOP")["upper_ratio"] > 0.8


def test_empty_string_safe():
    idx = extract_indices("")
    assert idx["has_url"] == 0 and idx["len"] == 0