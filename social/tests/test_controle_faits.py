import unittest

from social.s6_controle import controle

OFFRE = {"nom": "Le Nid de l'Erdre", "description": "Piscine intérieure chauffée à 32 °C, lit 180 cm", "equipements": ["Spa"],
         "ville": "Nantes"}


class TestFaits(unittest.TestCase):
    def test_numbers_must_be_sourced(self):
        self.assertEqual(controle.chiffres_non_sources(["Une piscine à 32 °C", "Un lit de 180 cm"], [OFFRE]), [])
        self.assertEqual(controle.chiffres_non_sources(["Un écran de 3 mètres", "à 20 min de Nantes"], [OFFRE]),
                         ["3 mètres", "20 min"])

    def test_temps_fort(self):
        theme = "Offrir une nuit : la carte cadeau qui ne finit pas dans un tiroir"
        self.assertTrue(controle.evoque_temps_fort(theme, ["Une nuit à offrir avant Noël"]))
        self.assertFalse(controle.evoque_temps_fort(theme, ["Une piscine rien qu'à vous"]))
        self.assertTrue(controle.evoque_temps_fort(None, ["x"]))

    def test_empreinte_ignores_review(self):
        c = {"legende": "a"}
        self.assertEqual(controle.empreinte(c), controle.empreinte({**c, "revue_visuelle": {"statut": "OK"}}))
        self.assertNotEqual(controle.empreinte(c), controle.empreinte({"legende": "b"}))

    def test_verdict_blocks_unsourced_figure(self):
        case = {"moteur": "lieu", "offres": [dict(OFFRE, prix_a_partir_de=225.0)]}
        v = controle.verdict({"case": case, "legende": "Le Nid de l'Erdre, dès 225 € la nuit. Lien en bio.",
                              "medias": ["a"], "textes_ecran": ["Un écran de 3 mètres"]})
        self.assertTrue(any("3 mètres" in b for b in v["bloquants"]))
        v = controle.verdict({"case": dict(case, moteur="couple"), "legende": "Le Nid de l'Erdre. Lien en bio.",
                              "medias": ["a"], "textes_ecran": ["Un message à 15 h"]})
        self.assertFalse(any("15 h" in b for b in v["bloquants"]))


if __name__ == "__main__":
    unittest.main()
