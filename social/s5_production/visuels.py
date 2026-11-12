#!/usr/bin/env python3
"""
S5 Production : visuels générés à partir des photos réelles des offres (boutique).

Règle de la stratégie : l'IA ne représente jamais un logement précis. Ici les photos sont
recadrées ou posées sur un fond flouté, jamais redessinées.

  carrousel : diapositives 1080x1350 (couverture, une par logement, diapositive finale)
  reel      : vidéo 1080x1920, un plan de 2,5 s par photo avec zoom lent et texte à l'écran

Charte : lue dans le kit de la marque (marques/<marque>/marque.json) via appliquer_kit(marque) :
couleurs (accent, encre, fond, blanc, secondaire), polices, mention du site.
"""
import io
import json
import os
import subprocess
import sys
import tempfile

import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Dimensions Instagram (à déplacer dans les règles de plateforme de S2 au jalon J3)
CAROUSEL, REEL = (1080, 1350), (1080, 1920)
# Zone sûre des Reels (décision du 12/11/2026, IG-R15 : zone sûre publicitaire Meta, seule référence publiée) :
# 14 % en haut, 35 % en bas, 6 % sur les côtés d'un 1080x1920.
ZONE_SURE_HAUT, ZONE_SURE_BAS, MARGE_LATERALE = 270, 1248, 65
# Images envoyées par l'API (IG-R09) : JPEG seulement, ratio entre 4:5 et 1,91:1, 8 Mo au plus.
RATIO_MIN, RATIO_MAX, POIDS_MAX = 4 / 5, 1.91, 8 * 1024 * 1024
TAILLE_TEXTE_MIN = 32  # px, lisibilité mobile (compilation S5)

# Kit courant : défini par appliquer_kit(marque) avant tout rendu.
KIT = {}
ROSE = INK = CREME = BLANC = GRIS = None
_POIDS = {"Bold": "titre", "Regular": "texte", "SemiBold": "accent"}


def appliquer_kit(marque):
    """Charge couleurs, polices et mention du site de la marque."""
    global ROSE, INK, CREME, BLANC, GRIS
    ROSE, INK, CREME = marque.couleur("accent"), marque.couleur("encre"), marque.couleur("fond")
    BLANC, GRIS = marque.couleur("blanc"), marque.couleur("secondaire")
    KIT.clear()
    KIT.update({"polices": {p: marque.police(r) for p, r in _POIDS.items()},
                "mention": marque.config["mention_site"], "unite_prix": marque.catalogue["unite_prix"]})


def font(weight, size):
    if not KIT:
        raise RuntimeError("kit de marque non chargé : appeler appliquer_kit(marque)")
    return ImageFont.truetype(KIT["polices"][weight], size)


def fetch(url, session=None):
    r = (session or requests).get(url, timeout=60)
    r.raise_for_status()
    return Image.open(io.BytesIO(r.content)).convert("RGB")


def cover(img, size):
    """Recadrage centré qui remplit `size` (aucune déformation)."""
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    im = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (im.width - tw) // 2, (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def fit_on_blur(img, size):
    """Photo entière centrée sur un fond flouté de la même photo (format vertical)."""
    bg = cover(img, size).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new("RGB", size, INK), 0.35)
    scale = min(size[0] / img.width, size[1] / img.height)
    fg = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    bg.paste(fg, ((size[0] - fg.width) // 2, (size[1] - fg.height) // 2))
    return bg


def wrap(draw, text, fnt, width):
    """Coupe le texte en lignes qui tiennent dans `width` pixels."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=fnt) <= width or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(img, lines_spec, x, y, width, color=INK, gap=12):
    d = ImageDraw.Draw(img)
    for txt, fnt in lines_spec:
        for line in wrap(d, txt, fnt, width):
            d.text((x, y), line, font=fnt, fill=color)
            y += fnt.size + gap
        y += gap
    return y


def slide_cover(photo, title, subtitle, counter=None):
    im = Image.new("RGB", CAROUSEL, CREME)
    im.paste(cover(photo, (1080, 860)), (0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((80, 910, 200, 918), fill=ROSE)
    text_block(im, [(title, font("Bold", 64)), (subtitle, font("Regular", 34))], 80, 950, 920)
    if counter:
        d.text((960, 1270), counter, font=font("SemiBold", 32), fill=INK, anchor="ra")
    return im


def order_equipements(equipements, phares):
    """Équipements phares d'abord (ordre de la stratégie), puis les autres."""
    first = [e for e in phares if e in equipements]
    return first + [e for e in equipements if e not in first]


def slide_lodging(photo, nom, lieu, prix, equipements, counter):
    im = Image.new("RGB", CAROUSEL, CREME)
    im.paste(cover(photo, (1080, 900)), (0, 0))
    d = ImageDraw.Draw(im)
    y = text_block(im, [(nom, font("Bold", 52))], 80, 945, 920)
    d.text((80, y), lieu, font=font("Regular", 32), fill=INK)
    d.text((80, y + 50), f"dès {prix:g} € " + KIT["unite_prix"].replace(" ", "\u00a0"), font=font("SemiBold", 34), fill=ROSE)
    d.text((80, y + 100), " · ".join(equipements[:3]), font=font("Regular", 32), fill=GRIS)
    d.text((1000, 1290), counter, font=font("SemiBold", 32), fill=INK, anchor="ra")
    return im


def slide_text(title, body, counter=None, cta=False):
    """Diapositive de texte. Charte : le rose reste un accent (filet, bouton), jamais un aplat."""
    im = Image.new("RGB", CAROUSEL, CREME)
    color = INK
    d = ImageDraw.Draw(im)
    d.rectangle((80, 200, 200, 208), fill=ROSE)
    if cta:
        d.rounded_rectangle((80, 1120, 560, 1200), radius=40, fill=ROSE)
        d.text((320, 1160), KIT["mention"], font=font("SemiBold", 34), fill=BLANC, anchor="mm")
    y = text_block(im, [(title, font("Bold", 68))], 80, 250, 920, color)
    text_block(im, [(body, font("Regular", 38))], 80, y + 30, 920, color, gap=14)
    if counter:
        d.text((1000, 1290), counter, font=font("SemiBold", 32), fill=color, anchor="ra")
    return im


def reel_frame(photo, line, first=False):
    im = fit_on_blur(photo, REEL)
    if line:
        d = ImageDraw.Draw(im)
        fnt = font("Bold", 64 if first else 54)
        lines = wrap(d, line, fnt, REEL[0] - 2 * MARGE_LATERALE - 80)
        h = len(lines) * (fnt.size + 14) + 60
        y0 = ZONE_SURE_HAUT if first else ZONE_SURE_BAS - h
        d.rounded_rectangle((MARGE_LATERALE, y0, REEL[0] - MARGE_LATERALE, y0 + h), radius=28, fill=(255, 255, 255))
        y = y0 + 30
        for ln in lines:
            d.text((540, y), ln, font=fnt, fill=INK, anchor="ma")
            y += fnt.size + 14
    return im


def render_reel(frames, out, seconds=2.5, fps=30):
    """Assemble les images en MP4 H.264 1080x1920 avec un zoom lent (ffmpeg)."""
    n = int(seconds * fps)
    with tempfile.TemporaryDirectory() as d:
        parts = []
        for i, fr in enumerate(frames):
            p = os.path.join(d, f"f{i}.png")
            fr.save(p)
            clip = os.path.join(d, f"c{i}.mp4")
            vf = (f"scale=1188:2112,zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={n}:s=1080x1920:fps={fps},format=yuv420p")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", p, "-vf", vf, "-frames:v", str(n),
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", clip], check=True)
            parts.append(clip)
        lst = os.path.join(d, "l.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{c}'\n" for c in parts)
        # piste audio muette : l'API refuse certaines vidéos sans piste audio
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                        "-c:v", "copy", "-c:a", "aac", "-movflags", "+faststart", out], check=True)
    return out


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height:format=duration",
                        "-of", "json", path], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def save_slides(slides, outdir, prefix):
    os.makedirs(outdir, exist_ok=True)
    paths = []
    for i, s in enumerate(slides, 1):
        if not RATIO_MIN - 1e-3 <= s.width / s.height <= RATIO_MAX:
            raise ValueError(f"diapositive {i} : ratio {s.width}x{s.height} refusé par l'API (4:5 à 1,91:1)")
        p = os.path.join(outdir, f"{prefix}-{i:02d}.jpg")
        s.convert("RGB").save(p, "JPEG", quality=92)
        if os.path.getsize(p) > POIDS_MAX:
            s.convert("RGB").save(p, "JPEG", quality=80)
        paths.append(p)
    return paths


if __name__ == "__main__":
    sys.exit("Module appelé par produire.py")
