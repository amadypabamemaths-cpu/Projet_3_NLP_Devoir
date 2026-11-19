from src.preprocess import normalize_light, remove_zero_width


def test_lowercases():
    assert normalize_light("BONJOUR") == "bonjour"


def test_removes_zero_width():
    assert "\u200b" not in normalize_light("ga\u200bgné")


def test_preserves_numbers_and_urls():
    out = normalize_light("Cliquez http://bit.ly/xx et payez 5 000 FCFA")
    assert "bit.ly" in out and "5 000" in out


def test_remove_zero_width_direct():
    assert remove_zero_width("a\u200bb\u200cc") == "abc"