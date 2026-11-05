from temoin import is_temoin
def test_deterministic(): assert is_temoin("01ABC") == is_temoin("01ABC")
def test_ratio_close_to_10pct():
    n = sum(is_temoin(f"p{i}") for i in range(20000)); assert 1800 <= n <= 2200
