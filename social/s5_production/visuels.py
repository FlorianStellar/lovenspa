#!/usr/bin/env python3
"""
S5 Production : visuels générés à partir des photos réelles des offres (boutique).

Règle de la stratégie : l'IA ne représente jamais un logement précis. Ici les photos sont
recadrées ou posées sur un fond flouté, jamais redessinées.

  carrousel : diapositives 1080x1350 (couverture, une par logement, diapositive finale)
  reel      : vidéo 1080x1920 en plein cadre, plans courts (0,8 à 1,5 s) en mouvement dès la première image,
              coupes franches, cartons de 6 mots au plus, musique intégrée (render_reel_plans) ;
              l'ancien rendu photo entière sur fond flouté (reel_frame, render_reel) reste le secours

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
# Reels (fiche F01, preuve B, benchmark du 12/11/2026) : plans de 0,5 à 1,5 s, 6 mots au plus par carton.
PLAN_MIN, PLAN_MAX, MOTS_CARTON_MAX = 0.5, 1.5, 6
SURDIMENSION = 1.18  # marge de l'image au-delà du cadre, parcourue par le panoramique

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
    """Coupe le texte en lignes qui tiennent dans `width` pixels. Un nombre reste collé à son unité
    (150 €, 32 °C, 3 m) et les signes doubles à leur mot (insécables de la typographie française)."""
    import re
    text = re.sub(r"(\d) (?=€|%|°|cm\b|m\b|h\b|min\b)", "\\1\u00a0", text or "")
    text = re.sub(r" (?=[:;!?»])", "\u00a0", text).replace("« ", "«\u00a0")
    words, lines, cur = text.split(" "), [], ""
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


def text_block(img, lines_spec, x, y, width, color=None, gap=12):
    # couleur lue à l'appel : INK n'existe qu'après appliquer_kit (une valeur par défaut figée vaudrait None = blanc)
    color = color or INK
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


def slide_lodging(photo, nom, lieu, prix, equipements, counter, badge=None):
    im = Image.new("RGB", CAROUSEL, CREME)
    im.paste(cover(photo, (1080, 900)), (0, 0))
    d = ImageDraw.Draw(im)
    if badge:  # ex. « Notre favori » (structure F03)
        fb = font("SemiBold", 34)
        w = d.textlength(badge, font=fb)
        d.rounded_rectangle((60, 60, 60 + w + 56, 124), radius=32, fill=ROSE)
        d.text((88 + w / 2, 92), badge, font=fb, fill=BLANC, anchor="mm")
    y = text_block(im, [(nom, font("Bold", 52))], 80, 945, 920)
    d.text((80, y), lieu, font=font("Regular", 32), fill=INK)
    d.text((80, y + 50), f"dès {prix:g} € " + KIT["unite_prix"].replace(" ", "\u00a0"), font=font("SemiBold", 34), fill=ROSE)
    d.text((80, y + 100), " · ".join(equipements[:3]), font=font("Regular", 32), fill=GRIS)
    d.text((1000, 1290), counter, font=font("SemiBold", 32), fill=INK, anchor="ra")
    return im


def slide_photo(photo, texte, counter):
    """Photo plein cadre 4:5 avec une ligne de texte en bas (concours : montrer le lot)."""
    im = cover(photo, CAROUSEL)
    d = ImageDraw.Draw(im)
    if texte:
        fnt = font("SemiBold", 44)
        lines = wrap(d, texte, fnt, 880)
        h = len(lines) * (fnt.size + 12) + 48
        d.rounded_rectangle((60, 1250 - h, 1020, 1250), radius=24, fill=CREME)
        y = 1250 - h + 24
        for ln in lines:
            d.text((100, y), ln, font=fnt, fill=INK)
            y += fnt.size + 12
    d.text((1000, 40), counter, font=font("SemiBold", 32), fill=BLANC, anchor="ra")
    return im


def slide_grand_texte(title, body="", counter=None, cta=None):
    """Diapositive de texte lisible au premier regard (revue J4, F07) : grand corps, bloc centré verticalement."""
    im = Image.new("RGB", CAROUSEL, CREME)
    d = ImageDraw.Draw(im)
    ft, fb = font("Bold", 84), font("Regular", 50)
    lt = wrap(d, title, ft, 920)
    lb = wrap(d, body, fb, 920) if body else []
    h = len(lt) * (ft.size + 16) + (40 + len(lb) * (fb.size + 16) if lb else 0)
    y = max(160, (CAROUSEL[1] - h) // 2 - 40)
    d.rectangle((80, y - 50, 200, y - 42), fill=ROSE)
    for ln in lt:
        d.text((80, y), ln, font=ft, fill=INK)
        y += ft.size + 16
    y += 40
    for ln in lb:
        d.text((80, y), ln, font=fb, fill=INK)
        y += fb.size + 16
    if cta:
        fc = font("SemiBold", 34)
        w = d.textlength(cta, font=fc)
        d.rounded_rectangle((80, 1150, 80 + w + 80, 1230), radius=40, fill=ROSE)
        d.text((120 + w / 2, 1190), cta, font=fc, fill=BLANC, anchor="mm")
    if counter:
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


def carton(texte, haut=False):
    """Calque transparent 1080x1920 : texte sur cartouche blanc, dans la zone sûre (IG-R15)."""
    im = Image.new("RGBA", REEL, (0, 0, 0, 0))
    if not texte:
        return im
    d = ImageDraw.Draw(im)
    fnt = font("Bold", 64 if haut else 58)
    lines = wrap(d, texte, fnt, REEL[0] - 2 * MARGE_LATERALE - 80)
    h = len(lines) * (fnt.size + 14) + 60
    y0 = ZONE_SURE_HAUT if haut else ZONE_SURE_BAS - h
    d.rounded_rectangle((MARGE_LATERALE, y0, REEL[0] - MARGE_LATERALE, y0 + h), radius=28, fill=(255, 255, 255, 240))
    y = y0 + 30
    for ln in lines:
        d.text((540, y), ln, font=fnt, fill=INK, anchor="ma")
        y += fnt.size + 14
    return im


def plan_image(photo, cadrage="auto"):
    """Image source d'un plan, plus grande que le cadre pour permettre un panoramique.
    cadrage : "auto" (plein cadre), "entier" (photo entière sur fond flouté, secours quand le recadrage
    couperait l'essentiel), ou "gauche"/"centre"/"droite" (point de départ du recadrage)."""
    if cadrage == "entier":
        base = fit_on_blur(photo, REEL)
        return base.resize((round(REEL[0] * SURDIMENSION), round(REEL[1] * SURDIMENSION)), Image.LANCZOS)
    zones = {"gauche": (0.0, 0.62), "centre": (0.19, 0.81), "droite": (0.38, 1.0)}
    if cadrage in zones and photo.width > photo.height:
        # panoramique limité à une zone de la photo (ex. exclure un logo ou un équipement non citable)
        a0, a1 = zones[cadrage]
        photo = photo.crop((round(photo.width * a0), 0, round(photo.width * a1), photo.height))
    tw, th = round(REEL[0] * SURDIMENSION), round(REEL[1] * SURDIMENSION)
    scale = max(tw / photo.width, th / photo.height)
    im = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.LANCZOS)
    return im


def pan_filtre(src_w, src_h, duree, sens):
    """Recadrage 1080x1920 qui glisse à vitesse constante dès t=0 (mouvement à la première image)."""
    w, h = REEL
    dx, dy = src_w - w, src_h - h
    if sens == "gauche":
        x, y = f"{dx}*(1-t/{duree})", f"{dy}/2"
    elif sens == "haut":
        x, y = f"{dx}/2", f"{dy}*(1-t/{duree})"
    elif sens == "bas":
        x, y = f"{dx}/2", f"{dy}*t/{duree}"
    else:
        x, y = f"{dx}*t/{duree}", f"{dy}/2"
    return f"crop={w}:{h}:x='{x}':y='{y}'"


def render_reel_plans(plans, out, musique=None, fps=30):
    """plans : [{"image": PIL, "texte": str|None, "duree": s, "cadrage": str, "haut": bool}].
    Coupes franches (concaténation sans fondu), panoramique alterné, musique coupée à la durée avec fondu."""
    with tempfile.TemporaryDirectory() as d:
        parts = []
        for i, p in enumerate(plans):
            src = plan_image(p["image"], p.get("cadrage", "auto"))
            sp, cp = os.path.join(d, f"s{i}.png"), os.path.join(d, f"t{i}.png")
            src.save(sp)
            carton(p.get("texte"), haut=p.get("haut", False)).save(cp)
            portrait = src.width - REEL[0] < src.height - REEL[1]
            sens = ("bas" if i % 2 else "haut") if portrait else ("gauche" if i % 2 else "droite")
            n = round(p["duree"] * fps)
            clip = os.path.join(d, f"c{i}.mp4")
            fc = f"[0]{pan_filtre(src.width, src.height, p['duree'], sens)},format=rgba[v];[v][1]overlay=0:0,format=yuv420p"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(fps), "-i", sp,
                            "-loop", "1", "-framerate", str(fps), "-i", cp, "-filter_complex", fc, "-frames:v", str(n),
                            "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", clip], check=True)
            parts.append(clip)
        lst = os.path.join(d, "l.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{c}'\n" for c in parts)
        total = sum(p["duree"] for p in plans)
        audio = (["-i", musique] if musique else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])
        af = f"atrim=0:{total:.2f},afade=t=out:st={max(total - 1, 0):.2f}:d=1" if musique else f"atrim=0:{total:.2f}"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, *audio,
                        "-filter_complex", f"[1:a]{af}[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "128k", "-ar", "44100", "-shortest", "-movflags", "+faststart", out],
                       check=True)
    return out


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
