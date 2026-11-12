"""Moteur Reel v2 (revue J4) : plein cadre, plans courts, cartons courts, musique intégrée."""
import json
import os
import subprocess
import tempfile
import unittest
from types import SimpleNamespace

from PIL import Image

from social.marque import charger
from social.s5_production import produire, visuels

visuels.appliquer_kit(charger("lovenspa"))
PHOTO = Image.new("RGB", (1536, 1024), (120, 60, 90))


def plans(n=12, d=1.25, texte="Une piscine rien qu'à vous"):
    return [{"photo": 1, "texte": texte if i == 0 else None, "duree": d} for i in range(n)]


class TestVerifier(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(produire.verifier_plans(plans()), [])

    def test_rules(self):
        e = produire.verifier_plans(plans(n=12, d=2.5))
        self.assertTrue(any("hors de" in x for x in e))
        e = produire.verifier_plans(plans(texte="Une piscine à 32 °C rien qu'à vous deux"))
        self.assertTrue(any("mots" in x for x in e))
        e = produire.verifier_plans(plans(texte=None))
        self.assertTrue(any("accroche" in x for x in e))
        e = produire.verifier_plans(plans(n=8))
        self.assertTrue(any("15 s au moins" in x for x in e))


class TestMusique(unittest.TestCase):
    def marque(self, d, lib):
        os.makedirs(os.path.join(d, "musique"))
        if lib is not None:
            with open(os.path.join(d, "musique", "licences.json"), "w") as f:
                json.dump(lib, f)
        return SimpleNamespace(dossier=d)

    def test_choice_and_errors(self):
        lib = [{"id": "a", "fichier": "a.mp3", "licence": "CC0"}, {"id": "b", "fichier": "b.mp3", "licence": "CC0"}]
        with tempfile.TemporaryDirectory() as d:
            m = self.marque(d, lib)
            c = {"case": {"date": "2026-11-22"}}
            self.assertEqual(produire.choisir_musique(c, m), produire.choisir_musique(c, m))  # stable
            self.assertEqual(produire.choisir_musique({**c, "musique": "b"}, m)[0]["id"], "b")
            with self.assertRaises(RuntimeError):
                produire.choisir_musique({**c, "musique": "z"}, m)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(RuntimeError):  # jamais de Reel muet
                produire.choisir_musique({"case": {"date": "2026-11-22"}}, self.marque(d, None))


class TestRendu(unittest.TestCase):
    def test_pan_moves_from_first_frame(self):
        f = visuels.pan_filtre(1300, 2300, 1.2, "droite")
        self.assertIn("x='56.0+108.0*t/1.2'", f)  # trajet plafonné à 90 px/s, centré, mouvement dès t=0
        self.assertIn("crop=1080:1920", f)

    def test_pan_speed_capped_on_wide_photos(self):
        import re
        for largeur in (1300, 2500, 3400):
            f = visuels.pan_filtre(largeur, 2266, 1.5, "droite")
            x0, tx = map(float, re.search(r"x='([\d.]+)\+([\d.]+)\*t", f).groups())
            self.assertLessEqual(tx / 1.5, visuels.VITESSE_PAN + 0.01)
            self.assertAlmostEqual(x0 + tx / 2, (largeur - 1080) / 2, delta=0.1)  # trajet centré

    def test_plan_image_covers_frame(self):
        im = visuels.plan_image(PHOTO)
        self.assertGreaterEqual(im.width, round(1080 * visuels.SURDIMENSION))
        self.assertGreaterEqual(im.height, round(1920 * visuels.SURDIMENSION))

    def test_cadrage_zone_excludes_corner(self):
        p = Image.new("RGB", (1536, 1024), (0, 0, 0))
        p.paste((255, 0, 0), (1400, 900, 1536, 1024))  # « logo » en bas à droite
        im = visuels.plan_image(p, "gauche")
        self.assertNotIn((255, 0, 0), list(im.getdata())[::97])
        self.assertIn((255, 0, 0), list(visuels.plan_image(p, "droite").getdata())[::97])

    def test_render_with_music(self):
        with tempfile.TemporaryDirectory() as d:
            son = os.path.join(d, "s.mp3")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "sine=f=440:d=5", "-ac", "2", son],
                           check=True)
            out = visuels.render_reel_plans([{"image": PHOTO, "texte": "Accroche", "duree": 1.0, "haut": True},
                                             {"image": PHOTO, "texte": None, "duree": 0.8}],
                                            os.path.join(d, "r.mp4"), musique=son)
            info = visuels.probe(out)
            vol = subprocess.run(["ffmpeg", "-i", out, "-af", "volumedetect", "-f", "null", "-"],
                                 capture_output=True, text=True).stderr
        v = next(s for s in info["streams"] if s["codec_type"] == "video")
        self.assertEqual((v["width"], v["height"]), (1080, 1920))
        self.assertAlmostEqual(float(info["format"]["duration"]), 1.8, delta=0.15)
        moyenne = float(vol.split("mean_volume:")[1].split("dB")[0])
        self.assertGreater(moyenne, -40)  # son audible, pas une piste muette
        a = next(s for s in info["streams"] if s["codec_type"] == "audio")
        self.assertEqual(a.get("sample_rate"), "48000")  # IG-R13


if __name__ == "__main__":
    unittest.main()
