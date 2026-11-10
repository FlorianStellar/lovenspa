from dispos_weekend import choisir
def c(h, v, libres): return {"handle": h, "ville": v, "libres": libres}
def test_ignore_sans_nuit_libre(): assert [x["handle"] for x in choisir([c("a", "Paris", {}), c("b", "Lyon", {"d": 1})])] == ["b"]
def test_max_deux_par_ville(): assert len(choisir([c(str(i), "Paris", {"d": 1}) for i in range(5)])) == 2
def test_limite_six(): assert len(choisir([c(str(i), f"V{i}", {"d": 1}) for i in range(10)])) == 6
