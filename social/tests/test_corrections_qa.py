"""Cas relevés par l'agent de contrôle qualité du 11/11/2026, et fonctions qui n'avaient pas de test direct."""
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from unittest import mock

from social.s8_mesure import audit
from social.s6_controle import controle
from social.connecteurs import instagram as ig_client
from social.s8_mesure import instantane
from social.s3_catalogue import offres as logements
from social.marque import charger
from social.tests.test_controle import BONNE, FICHE
from social.tests.test_ig_client import FakeResp, FakeSession

RULES = controle.load_rules()


def codes(r):
    return {x["code"] for x in r["resultats"]}


class TestCtaFalsePositives(unittest.TestCase):
    def test_reservez_lien_en_bio_is_one(self):
        self.assertEqual(controle.count_ctas("Réservez via le lien en bio.", RULES), ["lien"])

    def test_ordinary_words_are_not_ctas(self):
        self.assertEqual(controle.count_ctas("Sans réserve, on s'identifie à ce lieu.", RULES), [])


class TestLogementName(unittest.TestCase):
    def test_city_only_is_refused(self):
        text = BONNE.replace("L'Escale, ", "un gîte, ")
        self.assertIn("LOGEMENT", codes(controle.check(text, FICHE)))

    def test_short_name_accepted(self):
        self.assertNotIn("LOGEMENT", codes(controle.check(BONNE, FICHE)))

    def test_name_variants(self):
        self.assertEqual(controle.name_variants("L'Escale Dinard - L'Escale Spa"), ["l'escale dinard", "l'escale"])
        self.assertEqual(controle.name_variants("Le Lien"), ["le lien"])  # « Le » seul ne suffit pas

    def test_word_boundary(self):
        self.assertFalse(controle.word_in("brest", "brestoise"))
        self.assertTrue(controle.word_in("brest", "a brest, le soir"))


class TestPrices(unittest.TestCase):
    def test_thousands(self):
        self.assertEqual(controle.prices_in("dès 1 290 € la nuit", RULES), [(1290.0, True)])

    def test_small_amount(self):
        self.assertEqual(controle.prices_in("dès 9 €", RULES), [(9.0, True)])

    def test_gift_card_is_not_lodging_price(self):
        r = controle.check(BONNE.replace("de décembre.", "de décembre. Carte cadeau possible : 50 €."), FICHE)
        self.assertIn("AUTRE_MONTANT", codes(r))
        self.assertNotIn("PRIX", codes(r))


class TestWarnings(unittest.TestCase):
    def test_tics_word_boundary(self):
        self.assertEqual(controle.tics_in("C'est essentiellement quotidiennement", RULES), {})
        self.assertEqual(controle.tics_in("L'essentiel du quotidien", RULES), {"quotidien": 1, "essentiel": 1})

    def test_conclusion_before_cta(self):
        text = BONNE.replace("Commentez", "Parce que vous le valez bien.\n\nCommentez")
        self.assertIn("CONCLUSION", codes(controle.check(text, FICHE)))

    def test_opening(self):
        self.assertIn("OUVERTURE", codes(controle.check("Parfois " + BONNE, FICHE)))

    def test_length(self):
        self.assertIn("LONGUEUR", codes(controle.check(BONNE.replace("\n\nLe sauna", "\n\n" + "Le sauna. " * 60), FICHE)))

    def test_repetition_two_shared_tics(self):
        hist = ["Le quotidien, la parenthèse.\n#lovenspa"] * 4
        self.assertEqual(controle.repetition("Notre quotidien et cette parenthèse.", hist, RULES), 1.0)
        self.assertEqual(controle.repetition("Notre quotidien seulement.", hist, RULES), 0.0)


class TestControleIO(unittest.TestCase):
    def test_report(self):
        r = controle.check(BONNE, None)
        out = controle.report(r)
        self.assertTrue(out.startswith("STATUT REFUSE"))
        self.assertIn("BLOQUE  LOGEMENT", out)

    def test_history_from_snapshot_sorted(self):
        snap = {"publications": [{"timestamp": "2026-10-01", "caption": "ancienne"},
                                 {"timestamp": "2026-11-01", "caption": "récente"}, {"timestamp": "2026-10-15"}]}
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "s.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(snap, f)
            self.assertEqual(controle.history_from_snapshot(p), ["récente", "", "ancienne"])


class TestAuditFixes(unittest.TestCase):
    def test_zero_is_shown(self):
        self.assertEqual(audit.show(0), 0)
        self.assertEqual(audit.show(None), "-")

    def test_ranking_withheld_when_incomplete(self):
        posts = [{"id": str(i), "timestamp": "2026-10-01T00:00:00", "media_type": "IMAGE", "insights": {}}
                 for i in range(4)]
        posts[0]["insights"] = {"views": 10}
        md = audit.to_markdown(audit.enrich(posts), 4, today=date(2026, 11, 11))
        self.assertIn("Classement par multiple sur la médiane : non publié", md)

    def test_cadence(self):
        posts = [{"timestamp": d, "media_product_type": "REELS"} for d in ("2026-10-13", "2026-10-20", "2026-11-09")]
        c = audit.cadence(posts, weeks=4, today=date(2026, 11, 11))
        self.assertEqual((c["debut"], c["fin"]), ("2026-10-12", "2026-11-08"))
        self.assertEqual(c["par_semaine"], {"REELS": 0.5})

    def test_markdown_has_cadence_target(self):
        md = audit.to_markdown(audit.enrich([]), 0, today=date(2026, 11, 11), reels_cible=3)
        self.assertIn("pour une cible de 3 (non atteinte)", md)


class TestShopFake(unittest.TestCase):
    class Post:
        def __init__(self, nodes):
            self.nodes = nodes
            self.headers = {}
            self.sent = []

        def post(self, url, json=None, timeout=None):
            self.sent.append(json)
            return mock.Mock(status_code=200, raise_for_status=lambda: None,
                             json=lambda: {"data": {"products": {"nodes": self.nodes}}})

    NODE = {"handle": "x", "title": "Le Nid", "status": "ACTIVE", "tags": ["Equipements|Spa"],
            "priceRangeV2": {"minVariantPrice": {"amount": "120", "currencyCode": "EUR"}}}

    def cat(self, s):
        return logements.Catalogue(charger("lovenspa"), logements.Shopify(charger("lovenspa"), token="t", session=s))

    def test_logement_exact_handle(self):
        s = self.Post([self.NODE])
        self.assertEqual(self.cat(s).une("x")["nom"], "Le Nid")
        self.assertEqual(s.sent[0]["variables"], {"q": "handle:x"})

    def test_logement_other_handle_is_none(self):
        self.assertIsNone(self.cat(self.Post([dict(self.NODE, handle="y")])).une("x"))

    def test_chercher(self):
        s = self.Post([self.NODE, dict(self.NODE, handle="z")])
        res = self.cat(s).chercher("tag:'region|Bretagne'")
        self.assertEqual([r["handle"] for r in res], ["x", "z"])
        self.assertTrue(s.sent[0]["variables"]["q"].startswith("status:active "))


class TestIGClientMore(unittest.TestCase):
    def setUp(self):
        p = mock.patch.object(ig_client.time, "sleep", lambda s: None)
        p.start()
        self.addCleanup(p.stop)

    def test_retry_on_5xx(self):
        seq = [FakeResp(503, {}), FakeResp(200, {"id": "1"})]
        s = FakeSession([(lambda u, p: True, lambda u, p: seq.pop(0))])
        self.assertEqual(ig_client.IGClient("1", session=s, version="").get("1"), {"id": "1"})

    def test_snapshot_complete(self):
        routes = [
            (lambda u, p: u.endswith("/1") and "fields" in p, FakeResp(200, {"username": "lovenspa.fr", "followers_count": 7950})),
            (lambda u, p: u.endswith("1/media"), FakeResp(200, {"data": [{"id": "m1", "media_product_type": "FEED"}]})),
            (lambda u, p: u.endswith("m1/insights"), FakeResp(200, {"data": [{"name": "reach", "values": [{"value": 5}]}]})),
            (lambda u, p: u.endswith("/1/insights"), FakeResp(400, {"error": {"code": 100, "message": "breakdown non dispo"}})),
        ]
        snap = ig_client.IGClient("1", session=FakeSession(routes), version="").snapshot()
        self.assertEqual(snap["profil"]["followers_count"], 7950)
        self.assertIn("erreur", snap["profil"]["portee_30j_par_type"])
        self.assertEqual(snap["publications"][0]["insights"], {"reach": 5})

    def test_check_cli_clean_error(self):
        with mock.patch.object(ig_client.IGClient, "profile", side_effect=ig_client.IGError("Invalid OAuth", 190)):
            with self.assertRaises(SystemExit) as ctx:
                instantane.main(["--check"])
        self.assertIn("ÉCHEC connexion Instagram", str(ctx.exception.code))

    def test_check_cli_ok(self):
        with mock.patch.object(ig_client.IGClient, "profile", return_value={"username": "lovenspa.fr", "followers_count": 1,
                                                                             "media_count": 2}), \
                redirect_stdout(io.StringIO()) as out:
            self.assertEqual(instantane.main(["--check"]), 0)
        self.assertIn("OK @lovenspa.fr", out.getvalue())

if __name__ == "__main__":
    unittest.main()
