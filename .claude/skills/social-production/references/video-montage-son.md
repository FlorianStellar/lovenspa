# Vidéo, montage, son

Matière tirée de `social/compilation/s5-production.md` (sections 2.6, 2.7, 5 et 7). Spécifications de plateforme : `specs-plateformes.md` (toutes à vérifier dans la documentation officielle).

## 1. Ce que fait le code aujourd'hui

`social/s5_production/visuels.py`, appelé par `produire.py` pour le moteur `lieu` :
1. `fit_on_blur` : chaque vraie photo est posée entière, centrée, sur un fond flouté de la même photo (flou gaussien 40, voile d'encre à 35 %). Aucun pixel inventé.
2. `reel_frame` : carton blanc arrondi. Ligne 1 en Bold 64 à y=260 ; lignes suivantes en Bold 54, placées à `y0 = 1920 - 420 - h` (bas du carton à y=1500 : trop bas, voir section 6).
3. `render_reel` : un plan de 2,5 s par image, zoom lent jusqu'à 1,08 (`zoompan`), 30 i/s, H.264 (`libx264`, `veryfast`, `crf 20`), `yuv420p` ; concaténation ; piste audio muette AAC 44,1 kHz ajoutée (« l'API refuse certaines vidéos sans piste audio ») ; `+faststart`.
4. `probe` (ffprobe) : `produire.py` refuse une vidéo qui n'est pas en 1080x1920 et note sa durée.

## 2. Export (S5-43)

| Paramètre | Valeur retenue | Code actuel |
|---|---|---|
| Dimensions | 1080x1920 | conforme |
| Images par seconde | 30 | conforme |
| Codec vidéo | H.264, `yuv420p` | conforme |
| Audio | AAC 48 kHz | 44,1 kHz : à corriger |
| Diffusion | `+faststart` | conforme |
| Sonie | -14 LUFS intégrés, crête vraie ≤ -1 dBTP | non mesurée, non normalisée |

Toutes ces valeurs sont à vérifier dans la documentation officielle. Avec une musique, normaliser à -14 LUFS ; sans musique, garder la piste muette en 48 kHz.

## 3. Mouvement et rythme (S5-48, S5-18, S5-19, S5-22)

- Zoom lent sur chaque photo, 8 % au plus (le code : 1,08, conforme).
- Un changement de plan toutes les 2 à 4 s (le code : 2,5 s, conforme) ; aucun temps de plus de 4 s sans changement d'image.
- Entrées de texte en fondu ou en montée. Interdits : rebond, dépassement, halo, tremblement, confettis.
- Durée 15 à 45 s, cible 20 à 30 s ; relance entre 40 et 60 % au-delà de 25 s.

## 4. Musique et bruitages (S5-44, S5-45, S5-49)

- Uniquement un fichier dont la licence couvre l'usage commercial ; licence et provenance notées dans le journal. Sinon aucune musique, et « son à ajouter dans l'application » noté dans le paquet. Un compte professionnel n'a accès qu'à une partie de la bibliothèque de la plateforme.
- Volume : 0,15 sous une voix (environ -18 à -20 dB) ; 0,9 sans voix. Fondu d'entrée et de sortie.
- Choix selon l'émotion du premier carton : calme, sensuel, sans paroles pour laisser lire. Jamais la musique du Reel précédent (vérifier le journal).
- Aucun bruit de mouvement (whoosh, clic, glissement). Par défaut aucun bruitage (exemple Love'nSpa).
- Écartés par la compilation : bibliothèques de musiques réelles sans licence, nappes générées en code aux ambiances « tension », « thriller », « techno ».

## 5. Voix et sous-titres (S5-46, S5-50, S5-51, S5-35)

Voix : désactivée par défaut (arbitrage « voix off »). Option possible pour un format informatif, jamais en story, avec crédit et étiquette IA. Activation : proposition dans le journal (charte).

Si la voix est un jour activée (S5-50) :
- Moteur retenu : Kyutai Pocket TTS, voix `estelle`. Crédit : « Voix : Kyutai Pocket TTS (CC-BY 4.0) » en bio ou en mentions.
- Écrire pour la synthèse : une phrase par ligne, 15 mots au plus, chiffres en lettres, ni parenthèse, ni tiret, ni barre oblique, ni emoji, ni hashtag, ni lien. Vitesse 1,15 au plus.
- Dictionnaire de prononciation de la marque, au format de `rt-voix/prononciation.json` (exemple Love'nSpa : « Love'nSpa », « Last Love Minute », « spa », « jacuzzi »).
- Contrôle de durée et de prononciation par transcription (remplace l'écoute humaine).
- Étiquette « contenu généré par IA » activée sur la plateforme (S5-51) ; jamais de voix qui imite une personne réelle.

Sous-titres dès qu'il y a une voix (S5-46) : incrustés, 1 à 3 mots par segment, chiffres en chiffres, masqués quand un carton affiche les mêmes mots ; taille 72 px minimum ; fichier `.srt` livré à côté (7 mots au plus par entrée, nouvelle entrée à chaque phrase).

Licences des voix : voir `../SOURCES.md` (liste des voix interdites en usage commercial).

## 6. Zone sûre et texte (S5-58, S5-63, conflits)

Zone de texte retenue pour Reel et vidéo TikTok : x=60 à 940, y=230 à 1440 ; aucun texte au-delà de x=850 entre y=900 et y=1440 (colonne d'actions). Story : y=250 à 1600.

Taille : 34 px minimum en vidéo ; 72 px minimum pour des sous-titres.

Contraste : clair sur fond sombre, encre sur fond clair (le carton blanc du code y répond) ; jamais de texte sur un visage ni sur la zone la plus chargée de la photo.

Correction à faire dans `reel_frame` (non appliquée) : bas des cartons à y=1440 au plus (aujourd'hui y=1500) ; carton entre x=60 et x=940 (aujourd'hui x=60 à 1020).

## 7. Couverture de Reel (S5-59)

Image de la scène 1 avec le carton d'accroche, texte centré pour survivre au recadrage de la grille du profil. Non produite par le code : manuel (à outiller).

## 8. Contrôle avant rendu final (S5-47, S5-61)

1. Rendu brouillon en 540x960 (manuel, à outiller : `render_reel` rend directement en 1080x1920).
2. Extraire 4 à 5 images : l'accroche, une par temps, la dernière seconde.
3. Les regarder : texte lisible, rien hors zone sûre, pas de texte sur une zone chargée, pas de visage couvert, bonne photo du bon logement.
4. Un échec se refait seul ; ne jamais passer à S6 une vidéo non regardée.

Juge automatique possible : `flora.md` (S5-65).

## 9. Storyboard (S5-52)

Gabarit proposé pour décrire chaque scène (non lu par le code ; prolonge `reel_lignes` de `contenu.json`) :

```json
{
  "format": { "largeur": 1080, "hauteur": 1920, "fps": 30 },
  "charte": "<id de marque>",
  "audio": { "voix": null, "sous_titres": false, "musique": null, "volume_musique": 0.9 },
  "scenes": [
    {
      "duree": 2.5,
      "image": "<handle>#1",
      "titre": "Une piscine *rien* qu'à vous",
      "sous_titre": "",
      "position": "haut",
      "animation": "fondu",
      "zoom": "lent"
    }
  ]
}
```

Règles : une scène par temps du minutage ; `image` désigne toujours une vraie photo (`handle` et rang) ; un mot au plus en `*accent*` ; `position` (haut, centre, bas) toujours dans la zone sûre ; `animation` : monte, fondu ou aucune ; `zoom` : lent ou aucun.

## 10. Bibliothèque de médias réels (S5-53, S5-60)

Fiche par photo (une fois) : pièce, équipement visible, moment de la journée, ambiance, cadrage, défauts (flou, sombre, filigrane, personne identifiable), compteur d'usage. Le tag décrit seulement ce qui est visible.

Choix d'une photo : d'abord la correspondance à la ligne, puis non utilisée récemment, puis bonne orientation. Pas de bon plan : un carton texte, jamais une photo au hasard. Chaque emplacement de gabarit est relié à une photo précise ; moins de photos que d'emplacements : changer de gabarit.

Non codé : manuel (à outiller). Le code prend aujourd'hui les photos dans l'ordre de la boutique.

## 11. Vidéos tierces (S5-42)

Ne découper que des vidéos dont la marque détient les droits (accord écrit enregistré). Extrait de 20 à 60 s, compréhensible seul, marge de 0,5 s avant et après.
