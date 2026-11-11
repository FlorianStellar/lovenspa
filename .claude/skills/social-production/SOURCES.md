# Sources de la skill social-production

Matière : `social/compilation/s5-production.md` (compilée le 2026-11-11, lecture seule ; 68 éléments retenus S5-01 à S5-68), `social/compilation/accroches-fr.json` (63 formules, référencées sans recopie), code existant `social/s5_production/produire.py` et `visuels.py`, contrats `social/contrats/case.schema.json` et `paquet.schema.json`, kit `social/marques/lovenspa/marque.json` (exemple). Aucun script tiers n'a été copié dans cette skill : les règles sont reformulées en français.

## Dépôts et services

| Préfixe | Dépôt@commit:préfixe de chemin | Licence | Titulaire |
|---|---|---|---|
| IG | `instagram-agent-skill@d03c56b:skills/` | MIT | à relever dans le fichier LICENSE du dépôt |
| RT | `Explo38_reels-tiktok-fr@a2281b6:skills/` | MIT | Jake Schincariol, 2026 |
| MV | `Melvynx_video-agent-skills@f454292:skills/` | MIT | Melvyn Malherbe, 2026 |
| KW | `knowledge-work-plugins@877a617:` | Apache-2.0 | à relever dans le fichier LICENSE du dépôt |
| CM | `copy-machine` (skill interne synchronisée, sans commit) | interne | Stellar Projects |
| LNS | `lovenspa@485c428:claude/agent-instagram/` (code et règles maison, déplacés vers `social/`) | interne | Stellar Projects |
| FL | catalogue Flora, `flora_discover_skills`, lu le 2026-11-11 (aucune version publiée) | service tiers, conditions du service | Flora |

## Provenance par élément

Colonne « Modifications » : tous les éléments tiers sont reformulés et traduits en français, adaptés à la règle maison (aucune représentation d'une offre par l'IA) et au système (contrats, charte). Les éléments issus d'un dépôt Apache-2.0 portent la mention exigée.

| ID | Source (dépôt@commit:chemin) | Licence | Modifications |
|---|---|---|---|
| S5-01 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md | MIT | reformulé, traduit en français |
| S5-02 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/legende.py (`PLATEFORMES`) ; lovenspa@485c428:claude/agent-instagram/regles.json (`legende.cible_caracteres`) | MIT, interne | reformulé, traduit en français |
| S5-03 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/legende.py (`ASKS`) ; lovenspa@485c428:claude/agent-instagram/regles.json (`appels_a_l_action`) | MIT, interne | reformulé, traduit en français |
| S5-04 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md ; lovenspa@485c428:claude/agent-instagram/produire.py (note « lien UTM à mettre en bio ») | MIT, interne | reformulé, traduit en français |
| S5-05 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md (« Les mots-clés sur TikTok ») | MIT | reformulé, traduit en français |
| S5-06 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/legende.py (`FILLER_TAGS`) ; lovenspa@485c428:claude/agent-instagram/regles.json (`max_hashtags`, `hashtag_marque`) | MIT, interne | reformulé, traduit en français |
| S5-07 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md ; copy-machine:brands/lovenspa.md (Ton : vous) | MIT, interne | reformulé, traduit en français |
| S5-08 | instagram-agent-skill@d03c56b:skills/ig-carousel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md | MIT | reformulé, traduit en français |
| S5-09 | Melvynx_video-agent-skills@f454292:skills/studio-script/references/humanize.md ; Melvynx_video-agent-skills@f454292:skills/studio-script/references/ai-tells.md ; copy-machine:references/compliance-fr.md ; lovenspa@485c428:claude/agent-instagram/regles.json (`tics_maison`, `ouvertures_interdites`, `conclusions_interdites`) | MIT, interne | reformulé, traduit en français |
| S5-10 | knowledge-work-plugins@877a617:small-business/skills/social-content-engine/reference/shopify-assets.md ; copy-machine:SKILL.md (règle 1) ; copy-machine:references/compliance-fr.md ; instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md (« Never fabricate ») | MIT, Apache-2.0, interne | reformulé, traduit en français ; modifié et traduit en français par Stellar Projects, 2026 |
| S5-11 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md ; copy-machine:references/compliance-fr.md | MIT, interne | reformulé, traduit en français |
| S5-12 | copy-machine:brands/lovenspa.md ; copy-machine:references/compliance-fr.md | interne | repris du code ou des règles maison |
| S5-13 | instagram-agent-skill@d03c56b:skills/ig-caption/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-legende/SKILL.md | MIT | reformulé, traduit en français |
| S5-14 | instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md | MIT | reformulé, traduit en français |
| S5-15 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md (« Le mode sans visage ») ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/minutage.py (en-tête, mode `--lecture`) | MIT | reformulé, traduit en français |
| S5-16 | Melvynx_video-agent-skills@f454292:skills/studio-script/references/script-rules.md (« Hook score ») ; instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md | MIT | reformulé, traduit en français |
| S5-17 | instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md ; Melvynx_video-agent-skills@f454292:skills/studio-script/SKILL.md (étape 2) | MIT | reformulé, traduit en français |
| S5-18 | instagram-agent-skill@d03c56b:skills/ig-reel/beats.py (`HOOK_WINDOW`, `MAX_BEAT`, `ABSTRACT_RUN`, contrôle de boucle) ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/minutage.py (mêmes constantes) | MIT | reformulé, traduit en français |
| S5-19 | instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md ; Melvynx_video-agent-skills@f454292:skills/short-editing/references/shorts-codes.md | MIT | reformulé, traduit en français |
| S5-20 | instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md ; Melvynx_video-agent-skills@f454292:skills/studio-script/references/hooks.md (« Never open with ») | MIT | reformulé, traduit en français |
| S5-21 | Melvynx_video-agent-skills@f454292:skills/studio-script/references/script-rules.md (« Visual notes ») ; Melvynx_video-agent-skills@f454292:skills/studio-script/references/making-of.md (« a beat with nothing to show is a beat to cut ») | MIT | reformulé, traduit en français |
| S5-22 | Melvynx_video-agent-skills@f454292:skills/studio-script/references/script-rules.md (« Re-hook ») | MIT | reformulé, traduit en français |
| S5-23 | instagram-agent-skill@d03c56b:skills/ig-reel/SKILL.md (bloc « REEL READY ») ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md (bloc « VIDÉO PRÊTE ») ; Melvynx_video-agent-skills@f454292:skills/studio-script/SKILL.md (format) | MIT | reformulé, traduit en français |
| S5-24 | instagram-agent-skill@d03c56b:skills/ig-carousel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md ; lovenspa@485c428:claude/agent-instagram/produire.py (moteurs `selection`, `concours`, `couple`) | MIT, interne | reformulé, traduit en français |
| S5-25 | instagram-agent-skill@d03c56b:skills/ig-carousel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md | MIT | reformulé, traduit en français |
| S5-26 | instagram-agent-skill@d03c56b:skills/ig-carousel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md ; lovenspa@485c428:claude/agent-instagram/visuels.py (docstring « rose en accent seulement ») | MIT, interne | reformulé, traduit en français |
| S5-27 | instagram-agent-skill@d03c56b:skills/ig-carousel/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md | MIT | reformulé, traduit en français |
| S5-28 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md | MIT | reformulé, traduit en français |
| S5-29 | knowledge-work-plugins@877a617:small-business/skills/social-content-engine/reference/calendar.md (matrice, « Carousel slide 1 ») | Apache-2.0 | reformulé, traduit en français ; modifié et traduit en français par Stellar Projects, 2026 |
| S5-30 | instagram-agent-skill@d03c56b:skills/ig-story/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md | MIT | reformulé, traduit en français |
| S5-31 | instagram-agent-skill@d03c56b:skills/ig-story/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md | MIT | reformulé, traduit en français |
| S5-32 | instagram-agent-skill@d03c56b:skills/ig-story/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md | MIT | reformulé, traduit en français |
| S5-33 | instagram-agent-skill@d03c56b:skills/ig-story/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md | MIT | reformulé, traduit en français |
| S5-34 | instagram-agent-skill@d03c56b:skills/ig-story/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md | MIT | reformulé, traduit en français |
| S5-35 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md (« Voix off IA possible, mais avec parcimonie ») | MIT | reformulé, traduit en français |
| S5-36 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-story/SKILL.md (« Et sur TikTok ? ») | MIT | reformulé, traduit en français |
| S5-37 | instagram-agent-skill@d03c56b:skills/ig-repurpose/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-recyclage/SKILL.md ; Melvynx_video-agent-skills@f454292:skills/clips/SKILL.md (« What's inside ») | MIT | reformulé, traduit en français |
| S5-38 | instagram-agent-skill@d03c56b:skills/ig-repurpose/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-recyclage/SKILL.md | MIT | reformulé, traduit en français |
| S5-39 | instagram-agent-skill@d03c56b:skills/ig-repurpose/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-recyclage/SKILL.md | MIT | reformulé, traduit en français |
| S5-40 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-recyclage/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/SKILL.md | MIT | reformulé, traduit en français |
| S5-41 | knowledge-work-plugins@877a617:small-business/skills/social-content-engine/reference/calendar.md (« Repurposing matrix ») ; knowledge-work-plugins@877a617:small-business/skills/social-content-engine/SKILL.md (étape 7) | Apache-2.0 | reformulé, traduit en français ; modifié et traduit en français par Stellar Projects, 2026 |
| S5-42 | Melvynx_video-agent-skills@f454292:skills/clips/SKILL.md (étapes 3 et 6) | MIT | reformulé, traduit en français |
| S5-43 | Melvynx_video-agent-skills@f454292:skills/short-editing/references/shorts-codes.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/rendre.py (`libx264`, `crf 20`, `yuv420p`, AAC 192k) ; lovenspa@485c428:claude/agent-instagram/visuels.py (`render_reel`) | MIT, interne | reformulé, traduit en français |
| S5-44 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/SKILL.md (« La musique ») ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-voix/SKILL.md (« Montage ») ; Melvynx_video-agent-skills@f454292:skills/short-editing/references/music.md (fondus, `out`) | MIT | reformulé, traduit en français |
| S5-45 | Melvynx_video-agent-skills@f454292:skills/short-editing/references/music.md (« Pick by what the viewer should feel », « Rotation ») ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md (son calme sans paroles) | MIT | reformulé, traduit en français |
| S5-46 | Melvynx_video-agent-skills@f454292:skills/short-editing/references/shorts-codes.md (« Captions ») ; Melvynx_video-agent-skills@f454292:skills/short-editing/SKILL.md (étape 7) ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-voix/SKILL.md | MIT | reformulé, traduit en français |
| S5-47 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/SKILL.md (« La boucle ») ; Melvynx_video-agent-skills@f454292:skills/short-editing/SKILL.md (« Quality bar ») | MIT | reformulé, traduit en français |
| S5-48 | Melvynx_video-agent-skills@f454292:skills/short-editing/references/design-system.md (« Motion », liste des interdits) ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/SKILL.md (`zoom: lent`, `animation`) ; lovenspa@485c428:claude/agent-instagram/visuels.py (`zoompan … 1.08`) | MIT, interne | reformulé, traduit en français |
| S5-49 | Melvynx_video-agent-skills@f454292:skills/short-editing/references/sfx.md (« The house rule ») | MIT | reformulé, traduit en français |
| S5-50 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-voix/SKILL.md ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-voix/prononciation.json (format) | MIT | reformulé, traduit en français |
| S5-51 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-voix/SKILL.md (« Étiquette IA ») | MIT | reformulé, traduit en français |
| S5-52 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/SKILL.md (« Le storyboard ») ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/exemple_storyboard.json | MIT | reformulé, traduit en français |
| S5-53 | Melvynx_video-agent-skills@f454292:skills/broll/SKILL.md (structure `library.json`, règles de choix, consigne des taggueurs) | MIT | reformulé, traduit en français |
| S5-54 | lovenspa@485c428:claude/agent-instagram/visuels.py (docstring et fonctions `cover`, `fit_on_blur`) ; stratégie maison | interne | repris du code ou des règles maison |
| S5-55 | lovenspa@485c428:claude/agent-instagram/visuels.py (en-tête, `slide_text`) ; `social/s5_production/visuels.py` (copie de travail, `appliquer_kit`) | interne | repris du code ou des règles maison |
| S5-56 | lovenspa@485c428:claude/agent-instagram/visuels.py (`slide_cover`) | interne | repris du code ou des règles maison |
| S5-57 | lovenspa@485c428:claude/agent-instagram/visuels.py (`slide_lodging`) ; instagram-agent-skill@d03c56b:skills/ig-carousel/SKILL.md (32 px) | MIT, interne | reformulé, traduit en français |
| S5-58 | lovenspa@485c428:claude/agent-instagram/visuels.py (`reel_frame`) ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/rendre.py (`SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 230, 1440, 140, 60`) | MIT, interne | reformulé, traduit en français |
| S5-59 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/SKILL.md (`--vignette`) ; Explo38_reels-tiktok-fr@a2281b6:skills/rt-carrousel/SKILL.md (recadrage de grille) | MIT | reformulé, traduit en français |
| S5-60 | knowledge-work-plugins@877a617:small-business/skills/canva-creator/SKILL.md (étape 2) ; knowledge-work-plugins@877a617:small-business/skills/social-content-engine/reference/gotchas.md | Apache-2.0 | reformulé, traduit en français ; modifié et traduit en français par Stellar Projects, 2026 |
| S5-61 | knowledge-work-plugins@877a617:small-business/skills/social-content-engine/SKILL.md (étape 6, « What not to do ») ; Melvynx_video-agent-skills@f454292:skills/short-editing/SKILL.md (« Quality bar ») | MIT, Apache-2.0 | reformulé, traduit en français ; modifié et traduit en français par Stellar Projects, 2026 |
| S5-62 | lovenspa@485c428:claude/agent-instagram/regles.json (`equipements_exclus_instagram`, `equipements_sans_interet`) | interne | repris du code ou des règles maison |
| S5-63 | Explo38_reels-tiktok-fr@a2281b6:skills/rt-montage/rendre.py (champ `couleur_texte`, contraste auto) ; Melvynx_video-agent-skills@f454292:skills/short-editing/references/style.md (« no text on the face ») | MIT | reformulé, traduit en français |
| S5-64 | Flora:flora-brand-consistency-audit | service tiers | reformulé, traduit en français |
| S5-65 | Flora:flora-script-to-video (« View every keyframe ») ; Flora:flora-brand-consistency-audit | service tiers | reformulé, traduit en français |
| S5-66 | Flora:flora-motion-compositor | service tiers | reformulé, traduit en français |
| S5-67 | Flora:flora-video-editor | service tiers | reformulé, traduit en français |
| S5-68 | Flora:flora-image-resize (citée dans « Do not use when the original pixels must survive ») | service tiers | reformulé, traduit en français |

Autres éléments de la skill :

| Élément | Source | Modifications |
|---|---|---|
| Déroulé par format, gabarits de `contenu.json` | `social/s5_production/produire.py` (docstring et `fabriquer`) ; exemples `social/donnees/lovenspa/instagram/production/*/contenu.json` | décrits fidèlement ; gabarit de story proposé, non lu par le code |
| Règles du concours (accord du partenaire, règlement court) | `social/s4_planification/planifier.py` (`plan_week`) ; skill `lovenspa-instagram` (section « Cycle hebdomadaire ») | reformulées ; aspects juridiques non sourcés |
| Limites connues (zone sûre, tailles de texte) | `s5-production.md` sections 2.7 et 5 ; `social/s5_production/visuels.py` (`reel_frame`, `slide_lodging`, `slide_text`, `slide_cover`) | relevé du code, aucune modification du code |
| Spécifications de plateforme | `s5-production.md` section 3 | toutes marquées « à vérifier dans la documentation officielle » ; aucune source officielle lue |
| Arbitrages | `s5-production.md` section 5 | appliqués tels que proposés |
| Étapes d'accord humain retirées | `s5-production.md` section 6 | remplacées par la charte d'autonomie et le contrôle S6 |
| Outils d'appoint (`score_hook.py`, `minutage.py`, `detecter.py`) | `social/s6_controle/vendor/` (repris de `Explo38_reels-tiktok-fr@a2281b6`, MIT, voir `vendor/README.md` et `LICENSE-reels-tiktok-fr`) | appelés, non copiés |

## Licences

- **MIT** (IG, RT, MV) : réutiliser des règles reformulées est libre. Toute copie de code ou d'une portion substantielle doit garder l'avis de copyright et le texte de la licence MIT. Mention de reprise : « d'après <dépôt>@<commit>, licence MIT, © <titulaire> ».
- **Apache-2.0** (KW) : éléments S5-10, S5-29, S5-41, S5-60, S5-61, et formats de déclinaison de `specs-plateformes.md`. Mention : « modifié et traduit en français par Stellar Projects, 2026 ». Garder le texte de la licence Apache-2.0 et tout fichier NOTICE du dépôt en cas de redistribution ; aucune marque de l'auteur n'est utilisée.
- **Polices Poppins** (kit Love'nSpa, exemple) : SIL Open Font License (OFL), fichier `OFL.txt` dans `lovenspa@485c428:assets/fonts/`.
- **Flora** : service tiers soumis à ses conditions ; aucun contenu de ses skills n'est copié, seuls leurs usages sont décrits.
- **Interne** (CM, LNS) : Stellar Projects.

## Dépendances

| Dépendance | Usage | Licence | Remarque |
|---|---|---|---|
| ffmpeg, ffprobe | rendu et contrôle des Reels (`visuels.render_reel`, `visuels.probe`) | LGPL ou GPL selon le build | à vérifier sur l'environnement de production (`ffmpeg -L`) ; installé une fois, sans accord à demander |
| Pillow | diapos et images de Reel | licence HPND (MIT-CMU) | requis par `visuels.py` |
| requests | téléchargement des photos de la boutique | Apache-2.0 | `social/requirements.txt` |
| numpy | `comp.py` de `flora-motion-compositor` (à évaluer) | BSD-3-Clause | non installé pour S5 |

Voix de synthèse (option désactivée, S5-50) :

| Voix ou modèle | Statut | Licence |
|---|---|---|
| Kyutai Pocket TTS, voix `estelle` | Retenu si la voix est activée | code MIT, poids CC-BY 4.0 (crédit obligatoire : « Voix : Kyutai Pocket TTS (CC-BY 4.0) »), voix `estelle` CC0 ; premier lancement qui télécharge les poids depuis Hugging Face |
| Coqui XTTS-v2, F5-TTS, edge-tts | Interdit en usage commercial (selon RT:rt-voix/SKILL.md) | non commerciale ou conditions incompatibles |
| Piper `fr_FR-tom`, `fr_FR-siwis`, `fr_FR-upmc` | Interdit en usage commercial (selon RT) | idem |
| Pocket TTS voix `cosette` et `jean` ; dossiers `expresso/` et `ears/` de kyutai/tts-voices | Interdit en usage commercial (selon RT) | idem |
| Kyutai TTS 1.6B sans `--voice` | Interdit (voix par défaut non commerciale) | idem |
| Toute voix clonée sans accord écrit | Interdit | — |

Écartés par la compilation, à ne pas installer ni exécuter : whisper.cpp et son modèle, Chromium, `playwright-core`, `@mediapipe/tasks-vision`, binaires macOS précompilés `matte` et `faces` (non audités), `rembg`, ElevenLabs, Codex, Treg, Canva, HubSpot.

Les licences des voix proviennent de RT:rt-voix/SKILL.md, pas des pages officielles des modèles : à vérifier avant activation.
