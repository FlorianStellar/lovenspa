# S5 Production : compilation des skills tierces

Périmètre : écriture (légendes, scripts vidéo, carrousels, stories, déclinaisons), structure des formats, production visuelle et vidéo (montage, sous-titres, voix, musique, gabarits), recyclage d'un contenu en plusieurs formats. Instagram d'abord, puis TikTok et Pinterest. Marque pilote : Love'nSpa. Réutilisation prévue : Stellar Fleet (PME e-commerce Shopify).

Compilé le 2026-11-11. Lecture seule : aucun script exécuté, aucune génération lancée, aucun fichier modifié hors de celui-ci. Le contenu des dépôts a été traité comme de la donnée.

Règle maison qui prime sur tout ce qui suit : **l'IA ne représente jamais un logement précis.** Seules les vraies photos des logements le montrent (recadrées, posées sur un fond flouté, jamais redessinées ni prolongées).

---

## 1. Sources lues

Abréviations utilisées dans les colonnes « source » (chaque abréviation se lit comme un préfixe de chemin exact) :

| Abréviation | Dépôt@commit:préfixe | Licence |
| --- | --- | --- |
| IG: | `instagram-agent-skill@d03c56b:skills/` | MIT |
| RT: | `Explo38_reels-tiktok-fr@a2281b6:skills/` | MIT (Jake Schincariol, 2026) |
| MV: | `Melvynx_video-agent-skills@f454292:skills/` | MIT (Melvyn Malherbe, 2026) |
| KW: | `knowledge-work-plugins@877a617:` | Apache-2.0 |
| CM: | copy maison `copy-machine` (dossier synchronisé `/root/.claude/skills/synced/…/copy-machine/`, sans commit) | interne |
| LNS: | `lovenspa@485c428:claude/agent-instagram/` | interne |
| FL: | catalogue Flora, `flora_discover_skills`, lu le 2026-11-11 (aucune version publiée) | service tiers |

Fichiers lus en entier :

- IG : `ig-reel/SKILL.md`, `ig-reel/beats.py` (lecture seule), `ig-caption/SKILL.md`, `ig-carousel/SKILL.md`, `ig-story/SKILL.md`, `ig-repurpose/SKILL.md`. Survolés : `ig-reel/hooks.json` (liste des 26 formules), `ig-caption/caption.py` (non lu en détail).
- RT : `rt-video/SKILL.md`, `rt-legende/SKILL.md`, `rt-carrousel/SKILL.md`, `rt-story/SKILL.md`, `rt-montage/SKILL.md`, `rt-montage/exemple_storyboard.json`, `rt-voix/SKILL.md`, `rt-voix/prononciation.json`, `rt-recyclage/SKILL.md`, `rt-studio/SKILL.md`, `rt-studio/modele_campagne.json`. Survolés pour les constantes : `rt-montage/rendre.py` (en-tête, zone sûre, encodage), `rt-video/minutage.py` (en-tête, constantes), `rt-legende/legende.py` (constantes), `rt-voix/generer_voix.py` et `preparer_texte.py` (constantes).
- MV : `studio-script/SKILL.md` et `references/` (script-rules, hooks, humanize, ai-tells, viral, viral-research, funnel, making-of), `broll/SKILL.md`, `short-editing/SKILL.md` et `references/` (shorts-codes, music, style, sfx, looks, performance, design-system, sub-agents ; scene-library et style-schema survolés par titres et lignes clés), `short-editing/examples/README.md`, `short-editing/engine/package.json`, `editing/SKILL.md`, `clips/SKILL.md`, `short-translate/SKILL.md`, `vox/SKILL.md`, `vox/README.md`, `vox/references/look.md` (début), `codex-images/SKILL.md`. Moteur JS (`engine/lib/*.js`, `short.mjs`) non lu : code exécutable hors périmètre de lecture utile.
- KW : `marketing/skills/content-creation/SKILL.md`, `marketing/skills/draft-content/SKILL.md`, `small-business/skills/social-content-engine/SKILL.md` et `reference/` (calendar, shopify-assets, publishing, gotchas), `small-business/skills/canva-creator/SKILL.md` et `reference/canva-api.md` (tableau des formats), `small-business/skills/brand-style/SKILL.md`.
- CM : `SKILL.md`, `brands/lovenspa.md`, `references/canon.md`, `references/compliance-fr.md`, `references/diagnostic.md`, `formats/meta-ad.md`. Aucun format « social », « Reel » ou « légende » n'existe dans CM : seul `meta-ad.md` touche Instagram (hook de 125 caractères).
- FL : liste complète du catalogue, puis détail de 5 skills : `flora-image-resize`, `flora-motion-compositor`, `flora-video-editor`, `flora-brand-consistency-audit`, `flora-script-to-video`.
- LNS : `visuels.py`, `produire.py`, `regles.json`. Ces fichiers sont supprimés de l'arbre de travail et en cours de déplacement vers `social/s5_production/` (non suivi par git). Ils ont été lus dans le commit `485c428`. La copie de travail `social/s5_production/visuels.py` diffère seulement par le chargement du kit de marque (`appliquer_kit`) : la charte y est lue dans `marques/<marque>/marque.json` au lieu d'être codée en dur.

---

## 2. Éléments retenus

Légende des plateformes : IG = Instagram, TT = TikTok, PI = Pinterest. Aucune source lue ne traite Pinterest : la mention PI signifie « règle générique applicable », jamais « spécification Pinterest ».

### 2.1 Écriture de légende

| ID | Type | Élément (tel qu'on l'écrira) | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-01 | Règle | Avant d'écrire, fixer le rôle de la légende. Cas A : la vidéo porte déjà l'accroche ; la légende donne le contexte, la demande et les mots de recherche, sans seconde accroche. Cas B (photo, carrousel) : la ligne 1 est l'accroche, concrète, coupée sur un suspense. Le rôle choisi est écrit dans la fiche du post. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md | Évite la légende qui concurrence la vidéo. |
| S5-02 | Gabarit | Ligne 1 : 125 caractères maximum sur IG ; 90 maximum si le post part aussi sur TikTok. Jamais de salutation, de hashtag ou d'emoji en premier caractère. Corps : 2 à 6 paragraphes courts séparés par une ligne vide. Une seule demande. Hashtags sur la dernière ligne. Longueur cible Love'nSpa : 300 à 700 caractères. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/legende.py (`PLATEFORMES`) ; LNS:regles.json (`legende.cible_caracteres`) | Gabarit déjà cohérent avec `regles.json`. |
| S5-03 | Règle | Une seule demande par légende, prise dans une catégorie : lien en bio, commentaire, enregistrement, partage, message. Deux demandes = échec du contrôle. | IG, TT, PI | IG:ig-caption/SKILL.md ; RT:rt-legende/legende.py (`ASKS`) ; LNS:regles.json (`appels_a_l_action`) | Le contrôle maison compte déjà les demandes par catégorie. |
| S5-04 | Règle | Aucun lien dans la légende. Le lien UTM va en bio ou en message, et la fiche le signale. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md ; LNS:produire.py (note « lien UTM à mettre en bio ») | Les liens de légende ne sont pas cliquables. |
| S5-05 | Règle | Mettre 2 à 3 expressions de recherche dans le texte, en phrase naturelle (« love room avec spa privatif près de Disneyland Paris »), pas en hashtag. Sur TikTok, l'expression est aussi affichée sur un carton (pas de voix par défaut). | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md ; RT:rt-video/SKILL.md (« Les mots-clés sur TikTok ») | La recherche lit la légende ; TikTok lit aussi l'écran et l'audio. |
| S5-06 | Règle | Cinq hashtags maximum, dont `#lovenspa`, comme étiquettes de sujet. Interdits : `#fyp`, `#pourtoi`, `#viral`, `#explore`, `#foryou`, `#trending`, `#reels`, `#love`, `#instagood` et la liste de remplissage du linter RT. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/legende.py (`FILLER_TAGS`) ; LNS:regles.json (`max_hashtags`, `hashtag_marque`) | Plafond IG de 5 depuis le 18/12/2025, déjà sourcé dans `regles.json`. |
| S5-07 | Règle | Une demande de commentaire porte un seul mot, sans espace, sans emoji, sans accent si possible, en capitales, au vouvoiement : « Commentez SPA ». Le même mot est affiché dans la vidéo. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md ; CM:brands/lovenspa.md (Ton : vous) | Un mot qu'on peut taper ; vouvoiement de marque. |
| S5-08 | Règle | Texte alternatif obligatoire sur la couverture d'un carrousel et sur chaque photo seule. Il décrit la vraie photo (pièce, équipement, lumière), sans promesse ni prix. | IG, PI | IG:ig-carousel/SKILL.md ; RT:rt-legende/SKILL.md | Accessibilité et lecture par la plateforme. |
| S5-09 | Règle | Passe d'humanisation sur toute légende, tout carton et tout script : retirer les caractères invisibles (U+200B, U+200C, U+200D hors emoji, U+2060, U+FEFF, U+00AD, U+E0000 à U+E007F) ; garder les espaces insécables françaises ; remplacer les tics (listes FR de MV, de CM et `tics_maison` de LNS) ; une seule fausse opposition « ce n'est pas X, c'est Y » au plus ; pas de question-révélation (« Le résultat ? »), pas de triplet d'adjectifs, pas de récapitulatif final. Note sur 10 (propre, mots, formes, rythme, faits) ; seuil 9 avec « faits » à 2. | IG, TT, PI | MV:studio-script/references/humanize.md ; MV:studio-script/references/ai-tells.md ; CM:references/compliance-fr.md ; LNS:regles.json (`tics_maison`, `ouvertures_interdites`, `conclusions_interdites`) | Une grille notée remplace l'avis. Les listes maison restent prioritaires. |
| S5-10 | Règle | Aucun fait inventé. Prix, équipements, ville et nom du logement viennent de Shopify au moment de la production, jamais d'une session précédente. « Dès X € la nuit » seulement avec la valeur renvoyée. Pas de « était / maintenant » sans prix de référence réel. Un chiffre manquant s'écrit `{{à remplir}}` et bloque la publication. | IG, TT, PI | KW:small-business/skills/social-content-engine/reference/shopify-assets.md ; CM:SKILL.md (règle 1) ; CM:references/compliance-fr.md ; IG:ig-reel/SKILL.md (« Never fabricate ») | Une erreur de prix publique ne se corrige pas. |
| S5-11 | Règle | Emojis comme ponctuation uniquement : 4 pour 100 caractères au plus, jamais en puce, jamais en série. Pas de tiret cadratin. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md ; CM:references/compliance-fr.md | Les deux marqueurs IA les plus visibles. |
| S5-12 | Règle | Ton Love'nSpa : vouvoiement, complice, sensuel, élégant, suggestif jamais explicite, couple au centre. Interdits : alcool mis en avant, « N°1 » sans justificatif, promesse de disponibilité d'une date, urgence ou rareté fictive. | IG, TT, PI | CM:brands/lovenspa.md ; CM:references/compliance-fr.md | Ton et conformité déjà validés en interne. |
| S5-13 | Gabarit | Premier commentaire écrit à part s'il y a un complément ; 150 caractères maximum s'il part sur TikTok. Signalé dans la fiche. | IG, TT | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md | Garde la légende propre. |

### 2.2 Script vidéo courte (Reel, TikTok, épingle vidéo)

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-14 | Gabarit | Forme en cinq temps. 0 à 2 s : accroche, carton visible dès l'image 1, mouvement dès l'image 1. 2 à 7 s : l'enjeu en une ligne. Corps : une idée par temps, l'image change à chaque temps. 3 dernières secondes : on tient la promesse, puis la seule demande. Dernière ligne : reprendre un mot de l'accroche pour la boucle. | IG, TT | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md | Forme commune aux deux sources, testable. |
| S5-15 | Règle | Mode par défaut Love'nSpa : sans visage et sans voix. Les vraies photos du logement portent l'image, les cartons portent le sens, la musique donne le rythme. Chaque carton reste au moins 1,5 s, environ 3 mots par seconde plus 0,5 s. | IG, TT | RT:rt-video/SKILL.md (« Le mode sans visage ») ; RT:rt-video/minutage.py (en-tête, mode `--lecture`) | Correspond au moteur actuel (`reel_lignes` sur photos). |
| S5-16 | Règle | Écrire 3 accroches de 3 formules différentes, les noter, garder la meilleure, archiver les deux autres dans la fiche. Note sur 10 : précise, tension, spectateur, rapide (12 mots ou moins, sujet dans les 5 premiers), vraie (le corps tient la promesse) ; 2 points chacun ; seuil 7. | IG, TT | MV:studio-script/references/script-rules.md (« Hook score ») ; IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md | Grille lisible, sans script à exécuter. |
| S5-17 | Règle | Le texte à l'écran est un script à part : 6 mots maximum pour le carton d'accroche ; il complète la phrase, ne la recopie pas ; un seul mot en accent. | IG, TT | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md ; MV:studio-script/SKILL.md (étape 2) | Lu avant d'être entendu, souvent sans le son. |
| S5-18 | Règle | Contrôle du minutage : accroche en 3 s au plus ; aucun temps de plus de 4 s sans changement d'image ; jamais 3 temps d'affilée sans rien de concret (nom, chiffre, lieu) ; la dernière ligne partage un mot avec la première. Durée totale à 10 % de la cible. | IG, TT | IG:ig-reel/beats.py (`HOOK_WINDOW`, `MAX_BEAT`, `ABSTRACT_RUN`, contrôle de boucle) ; RT:rt-video/minutage.py (mêmes constantes) | Règles à porter dans notre contrôle, sans dépendre du script tiers. |
| S5-19 | Règle | Durée : 15 à 45 s, cible par défaut 20 à 30 s. Pas de vidéo de moins de 7 s. | IG, TT | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md ; MV:short-editing/references/shorts-codes.md | Plage commune aux trois sources. |
| S5-20 | Règle | Une idée par vidéo. Pas d'introduction, pas de logo animé, pas de « bonjour ». Une seule demande finale. Pas de script écrit autour d'un son tendance indisponible pour un compte professionnel. | IG, TT | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md ; MV:studio-script/references/hooks.md (« Never open with ») | Règles de coupe simples. |
| S5-21 | Gabarit | Notes visuelles séparées des lignes : `ligne N → montrer : photo k du logement <handle>` ou `ligne N → carton : 1 à 4 mots`. En mode sans voix, chaque ligne a une note « montrer ». Une ligne sans vraie photo à montrer est coupée. | IG, TT | MV:studio-script/references/script-rules.md (« Visual notes ») ; MV:studio-script/references/making-of.md (« a beat with nothing to show is a beat to cut ») | Garantit que l'image vient toujours d'une vraie photo. |
| S5-22 | Règle | Au-delà de 25 s, une relance entre 40 et 60 % de la vidéo (un chiffre, un équipement, une bascule). | IG, TT | MV:studio-script/references/script-rules.md (« Re-hook ») | Évite le creux du milieu. |
| S5-23 | Gabarit | Fiche de sortie d'un script : plateforme, mode, formule d'accroche, note, durée estimée, nombre de cartons, note d'humanisation, éléments à remplir. | IG, TT | IG:ig-reel/SKILL.md (bloc « REEL READY ») ; RT:rt-video/SKILL.md (bloc « VIDÉO PRÊTE ») ; MV:studio-script/SKILL.md (format) | Format de traçabilité réutilisable par S6 et S8. |

### 2.3 Carrousel

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-24 | Gabarit | 6 à 10 diapos. 1 : couverture, 6 mots maximum, une ligne de promesse. 2 : l'enjeu en une phrase, lisible seule (seconde couverture). 3 à N : une idée par diapo, titre de 3 à 7 mots, 25 mots maximum dessous. N+1 : récapitulatif autonome. Dernière : une seule demande. Pour le moteur « sélection » : couverture, une diapo par logement, diapo de fin. | IG, TT, PI | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md ; LNS:produire.py (moteurs `selection`, `concours`, `couple`) | Structure compatible avec nos trois moteurs. |
| S5-25 | Règle | Numéroter chaque diapo (3/8) et porter la mention de la marque (`@lovenspa.fr` ou `lovenspa.fr`) en petit sur chaque diapo, pas seulement sur la dernière. | IG, TT | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md | Les captures circulent sans contexte. Le code ne met la mention que sur la diapo finale. |
| S5-26 | Règle | Texte de couverture à plus de 120 px de chaque bord. Aucun texte sous 32 px. Une seule couleur d'accent (le rose de la charte). | IG | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md ; LNS:visuels.py (docstring « rose en accent seulement ») | Lisible en vignette et après recadrage de grille. |
| S5-27 | Règle | La légende d'un carrousel est en cas B (S5-01). | IG | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md | La couverture a déjà utilisé ses six mots. |
| S5-28 | Règle | Version TikTok mode photo : refaire la mise en page en 1080x1920, texte dans la zone sûre, pseudo en haut à gauche de la zone sûre. Ne jamais centrer une diapo 4:5 sur un fond 9:16. Son calme, sans paroles. | TT | RT:rt-carrousel/SKILL.md | Même texte, deux mises en page. |
| S5-29 | Règle | La diapo 1 doit pouvoir être publiée seule (elle sert de base à la déclinaison en post simple et en épingle). | IG, PI | KW:small-business/skills/social-content-engine/reference/calendar.md (matrice, « Carousel slide 1 ») | Évite une couverture qui dépend des diapos suivantes. |

### 2.4 Story

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-30 | Gabarit | 3 à 7 images par jour. 1 : un vrai moment (vraie photo ou vidéo d'un logement, une main, un détail). 2 à 3 : le contenu. 4 : la demande, un seul sticker. 5 : la réponse ou l'annonce du lendemain. | IG | IG:ig-story/SKILL.md ; RT:rt-story/SKILL.md | La demande arrive avant la chute d'audience. |
| S5-31 | Règle | Texte entre y=250 et y=1600 sur 1080x1920. Une idée par image. Pas de texte sur fond uni en ouverture. | IG | IG:ig-story/SKILL.md ; RT:rt-story/SKILL.md | Zone propre aux stories, différente des Reels. |
| S5-32 | Règle | Choix du sticker selon le rôle : sondage (volume), questions (récolter les mots exacts du public, réutilisés comme accroches), quiz (idée reçue), lien (seule surface cliquable avec la bio), compte à rebours (échéance réelle uniquement). | IG | IG:ig-story/SKILL.md ; RT:rt-story/SKILL.md | Table directement réutilisable. |
| S5-33 | Règle | Ne jamais repartager un post en story sans commentaire. Pour vendre : 3 images de contexte, 1 d'offre, 1 de preuve. | IG | IG:ig-story/SKILL.md ; RT:rt-story/SKILL.md | Repartage brut = image la plus ignorée. |
| S5-34 | Règle | Entonnoir honnête : la personne agit d'abord (vote, réponse, commentaire), on répond ensuite. Réponses automatiques uniquement par les outils officiels. Jamais de message en masse. | IG, TT | IG:ig-story/SKILL.md ; RT:rt-story/SKILL.md | Conformité aux conditions des plateformes. |
| S5-35 | Règle | Pas de voix de synthèse en story. | IG | RT:rt-story/SKILL.md (« Voix off IA possible, mais avec parcimonie ») | Une voix de synthèse sonne faux sur un format intime. |
| S5-36 | Règle | Sur TikTok, ne pas produire de stories. L'équivalent : la réponse vidéo à un commentaire (commentaire en sticker, réponse en cartons sur vraies photos). | TT | RT:rt-story/SKILL.md (« Et sur TikTok ? ») | Effort placé là où il porte. |

### 2.5 Recyclage et déclinaisons

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-37 | Règle | Extraire, ne pas résumer. D'une source longue (article du magazine Love'nSpa, fiche détaillée, avis, vidéo d'un propriétaire), relever : affirmations, chiffres, histoires, mécanismes, erreurs, phrases citables, avec les comptes. Moins de 4 éléments : la source est maigre, le dire. | IG, TT, PI | IG:ig-repurpose/SKILL.md ; RT:rt-recyclage/SKILL.md ; MV:clips/SKILL.md (« What's inside ») | Méthode commune à trois sources. |
| S5-38 | Règle | Format par extrait : affirmation, histoire → vidéo ; mécanisme, liste → carrousel ; phrase citable → image de story. | IG, TT, PI | IG:ig-repurpose/SKILL.md ; RT:rt-recyclage/SKILL.md | Tout ne devient pas un Reel. |
| S5-39 | Règle | Chaque publication tient seule, sans « comme on le disait ». Formules d'accroche variées sur une même source. Ordre de semaine : l'affirmation la plus forte d'abord, le mécanisme en dernier. | IG, TT | IG:ig-repurpose/SKILL.md ; RT:rt-recyclage/SKILL.md | Évite l'effet usine à contenu. |
| S5-40 | Règle | Une vidéo, deux plateformes : export propre sans filigrane, publié nativement sur chaque application, zone sûre commune, une légende par plateforme. | IG, TT | RT:rt-recyclage/SKILL.md ; RT:rt-video/SKILL.md | Jamais une vidéo téléchargée avec le filigrane de l'autre plateforme. |
| S5-41 | Gabarit | Matrice de déclinaison à partir d'un visuel validé (recadrage des vraies photos, jamais regénération) : diapo 1 de carrousel → post simple ; couverture → couverture de Reel et image de story 1080x1920 (une ligne, un sticker) ; épingle verticale (format à vérifier, voir section 3). Ce qui voyage : la photo, le traitement de marque, l'affirmation centrale. Ce qui change : longueur de légende, nombre de hashtags, registre. | IG, TT, PI | KW:small-business/skills/social-content-engine/reference/calendar.md (« Repurposing matrix ») ; KW:small-business/skills/social-content-engine/SKILL.md (étape 7) | Déclinaison économe et cohérente. |
| S5-42 | Règle | Découpe d'une vidéo longue existante (vidéo d'un propriétaire, droits obtenus) : un extrait commence sur une phrase compréhensible sans contexte, tient une idée en 20 à 60 s, finit sur une phrase complète, sans référence au reste. Note sur 10, seuil 7. Marge de 0,5 s avant et après pour la coupe. | IG, TT | MV:clips/SKILL.md (étapes 3 et 6) | Utile quand un hôte fournit une vidéo réelle. |

### 2.6 Montage, sous-titres, voix, musique

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-43 | Spécification | Export vidéo : 1080x1920, 30 i/s, H.264, `yuv420p`, AAC 48 kHz, `+faststart`. Sonie intégrée -14 LUFS, crête vraie à -1 dBTP au plus. | IG, TT | MV:short-editing/references/shorts-codes.md ; RT:rt-montage/rendre.py (`libx264`, `crf 20`, `yuv420p`, AAC 192k) ; LNS:visuels.py (`render_reel`) | Notre rendu fait déjà H.264 et `faststart` ; il manque 48 kHz et la sonie. |
| S5-44 | Règle | Musique : uniquement un fichier dont la licence couvre l'usage commercial, ou aucune musique et « son à ajouter dans l'application » noté dans la fiche. Un compte professionnel n'a accès qu'à une partie de la bibliothèque. Volume sous une voix : 0,15 (environ -18 à -20 dB) ; sans voix : 0,9. Fondu d'entrée et de sortie. | IG, TT | RT:rt-montage/SKILL.md (« La musique ») ; RT:rt-voix/SKILL.md (« Montage ») ; MV:short-editing/references/music.md (fondus, `out`) | Aucun risque de son coupé ou réclamé. |
| S5-45 | Règle | Le choix de musique suit l'émotion du premier carton (calme, sensuel, sans paroles pour laisser lire). Ne jamais reprendre la musique du Reel précédent. | IG, TT | MV:short-editing/references/music.md (« Pick by what the viewer should feel », « Rotation ») ; RT:rt-carrousel/SKILL.md (son calme sans paroles) | Rotation simple à contrôler par l'historique. |
| S5-46 | Règle | Sous-titres incrustés dès qu'il y a une voix : 1 à 3 mots par segment, chiffres en chiffres, masqués quand un carton affiche les mêmes mots. Fichier `.srt` livré à côté : 7 mots maximum par entrée, nouvelle entrée à chaque phrase. | IG, TT | MV:short-editing/references/shorts-codes.md (« Captions ») ; MV:short-editing/SKILL.md (étape 7) ; RT:rt-voix/SKILL.md | 80 % des vues commencent sans le son (selon MV, non officiel). |
| S5-47 | Règle | Contrôle avant rendu final : rendu brouillon 540x960, extraire 4 à 5 images (accroche, chaque temps, dernière seconde) et les regarder : texte lisible, rien hors zone sûre, pas de texte sur une zone chargée de la photo, pas de visage couvert. | IG, TT | RT:rt-montage/SKILL.md (« La boucle ») ; MV:short-editing/SKILL.md (« Quality bar ») | Une image coûte des secondes, un rendu des minutes. |
| S5-48 | Règle | Mouvement sobre : zoom lent sur chaque photo (8 % au plus), un changement de plan toutes les 2 à 4 s, entrées de texte en fondu ou montée, sans rebond, sans dépassement, sans halo, sans tremblement, sans confettis. | IG, TT | MV:short-editing/references/design-system.md (« Motion », liste des interdits) ; RT:rt-montage/SKILL.md (`zoom: lent`, `animation`) ; LNS:visuels.py (`zoompan … 1.08`) | Cohérent avec un ton élégant ; notre zoom est déjà conforme. |
| S5-49 | Règle | Bruitages : aucun bruit de mouvement (whoosh, clic, glissement). Par défaut aucun bruitage sur Love'nSpa. | IG, TT | MV:short-editing/references/sfx.md (« The house rule ») | Les bruitages cassent l'ambiance. |
| S5-50 | Option | Voix off de synthèse (désactivée par défaut, à décider plus tard) : Kyutai Pocket TTS, voix `estelle`, crédit « Voix : Kyutai Pocket TTS (CC-BY 4.0) » en bio ou en mentions. Écrire pour la synthèse : une phrase par ligne, 15 mots au plus, chiffres en lettres, pas de parenthèse, de tiret ni de barre oblique, pas d'emoji, de hashtag ni de lien. Vitesse 1,15 au plus. Dictionnaire de prononciation de marque (« Love'nSpa », « Last Love Minute », « spa », « jacuzzi »). | IG, TT | RT:rt-voix/SKILL.md ; RT:rt-voix/prononciation.json (format) | Option gratuite et locale, licence commerciale si crédit. |
| S5-51 | Règle | Étiquette « contenu généré par IA » activée sur IG et TT dès qu'un audio ou un visuel réaliste est généré. Jamais de voix qui imite une personne réelle. | IG, TT | RT:rt-voix/SKILL.md (« Étiquette IA ») | Protège le compte. |
| S5-52 | Gabarit | Storyboard JSON par vidéo : `format` (largeur, hauteur, fps), `charte`, `audio` (voix, sous_titres, musique, volume_musique), `scenes[]` avec `duree`, `image` (chemin d'une vraie photo), `titre` (un mot en `*accent*`), `sous_titre`, `position` (haut, centre, bas dans la zone sûre), `animation` (monte, fondu, aucune), `zoom` (lent, aucun). Une scène par temps du minutage. | IG, TT | RT:rt-montage/SKILL.md (« Le storyboard ») ; RT:rt-montage/exemple_storyboard.json | Prolonge `contenu.json` (`reel_lignes`) vers un format décrivant chaque scène. |
| S5-53 | Gabarit | Bibliothèque de médias réels : chaque photo Shopify (et chaque vidéo fournie par un hôte) reçoit une fiche taguée une fois (pièce, équipement visible, moment de la journée, ambiance, cadrage, défauts : flou, sombre, filigrane, personne identifiable) et un compteur d'usage. Le choix d'une photo : correspond à la ligne, puis non utilisée récemment, puis bonne orientation. Pas de bon plan : un carton texte, jamais une photo au hasard. Le tag décrit seulement ce qui est visible. | IG, TT, PI | MV:broll/SKILL.md (structure `library.json`, règles de choix, consigne des taggueurs) | Réduit les répétitions de photos d'un post à l'autre. |

### 2.7 Visuels et gabarits

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-54 | Règle maison | Un logement n'est montré que par ses vraies photos : recadrage centré (`cover`) ou photo entière sur fond flouté de la même photo (`fit_on_blur`). Aucune regénération, aucun prolongement génératif, aucun détourage avec fond inventé, aucune génération de « décor » qui pourrait passer pour un logement. | IG, TT, PI | LNS:visuels.py (docstring et fonctions `cover`, `fit_on_blur`) ; stratégie maison | Non négociable. |
| S5-55 | Charte | Polices Poppins (OFL) Bold, SemiBold, Regular ; encre #222222 ; crème #FBF6F2 ; rose #E83F4E en accent seulement (filet, prix, bouton), jamais en aplat. En cours : lecture depuis le kit de marque pour Stellar Fleet. | IG, TT, PI | LNS:visuels.py (en-tête, `slide_text`) ; `social/s5_production/visuels.py` (copie de travail, `appliquer_kit`) | Charte déjà en production. |
| S5-56 | Gabarit | Couverture de carrousel 1080x1350 : photo réelle 1080x860 en haut, filet rose 120x8 à y=910, titre Bold 64, sous-titre Regular 34, compteur en bas à droite. | IG | LNS:visuels.py (`slide_cover`) | Gabarit existant conservé. |
| S5-57 | Gabarit | Diapo logement 1080x1350 : photo réelle 1080x900, nom Bold 52, lieu Regular 32, « dès X € la nuit » SemiBold 34 en rose, 3 équipements phares, compteur. À corriger : équipements et compteur passent de 28 et 26 px à 32 px minimum (S5-26). | IG | LNS:visuels.py (`slide_lodging`) ; IG:ig-carousel/SKILL.md (32 px) | Lisibilité sur téléphone. |
| S5-58 | Gabarit | Image de Reel 1080x1920 : photo entière sur fond flouté, carton blanc arrondi. Carton d'accroche à y=260. Cartons suivants à corriger : bas du carton à y=1440 au plus (aujourd'hui il descend à y=1500). Rien dans les 140 px de droite. | IG, TT | LNS:visuels.py (`reel_frame`) ; RT:rt-montage/rendre.py (`SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 230, 1440, 140, 60`) | Le bas du cadre est couvert par la légende et le son. |
| S5-59 | Gabarit | Couverture de Reel : image de la scène 1 avec le carton d'accroche, texte centré pour survivre au recadrage de la grille. | IG, TT | RT:rt-montage/SKILL.md (`--vignette`) ; RT:rt-carrousel/SKILL.md (recadrage de grille) | La couverture est vue dans la grille du profil. |
| S5-60 | Règle | Inventaire emplacement par emplacement : chaque emplacement d'image d'un gabarit est relié à une photo précise (`handle`, rang de la photo). Moins de photos que d'emplacements : changer de gabarit ; ne jamais répéter une photo sans décision explicite dans la fiche. | IG, TT, PI | KW:small-business/skills/canva-creator/SKILL.md (étape 2) ; KW:small-business/skills/social-content-engine/reference/gotchas.md | Évite les cases vides ou répétées. |
| S5-61 | Règle | Ne jamais présenter ni publier un visuel non regardé. Après rendu, vérifier chaque image (bonne photo, bon logement, texte complet, rien de coupé). Un échec se refait seul, pas tout le lot. | IG, TT, PI | KW:small-business/skills/social-content-engine/SKILL.md (étape 6, « What not to do ») ; MV:short-editing/SKILL.md (« Quality bar ») | Un rendu réussi techniquement peut être faux. |
| S5-62 | Règle | Équipements exclus d'Instagram (BDSM, croix de Saint-André, barre de pole dance, sofa tantrique, TV adulte, secret room, balançoire) et équipements sans intérêt jamais affichés. | IG, TT, PI | LNS:regles.json (`equipements_exclus_instagram`, `equipements_sans_interet`) | Règle maison existante. |
| S5-63 | Règle | Contraste automatique du texte (clair sur fond sombre, encre sur fond clair) ; jamais de texte sur un visage ni sur la zone la plus chargée de la photo. | IG, TT | RT:rt-montage/rendre.py (champ `couleur_texte`, contraste auto) ; MV:short-editing/references/style.md (« no text on the face ») | Lisibilité. |

### 2.8 Outils Flora à appeler

| ID | Type | Élément | Plateformes | Source | Pourquoi |
| --- | --- | --- | --- | --- | --- |
| S5-64 | Méthode | Audit de cohérence d'une série avant publication : écrire d'abord les règles vérifiables (photo, palette, cadrage, logo et texte, fond, format de sortie), puis regarder la série entière (dérive entre les premiers et les derniers visuels, groupes d'échecs), puis un échantillon stratifié (premier, milieu, dernier, signalés, quelques tirés au hasard). Constats : Rejet, Correction, Signalement, avec la preuve et la portée. Applicable sans Flora ; avec Flora, environ 0,005 à 0,006 $ par image regardée. | IG, TT, PI | FL:flora-brand-consistency-audit | Détecte une série d'images correctes une à une mais incohérentes ensemble. |
| S5-65 | Outil | Juge image-texte gratuit pour vérifier un visuel rendu : modèles `i2t-gemini-3-x-flash-i2t` (0 $), paramètre `image_urls` au pluriel, description et transcription du texte exigées avant le verdict, réponse JSON. Sert à vérifier qu'un carton contient le bon texte et qu'aucune zone n'est coupée. | IG, TT, PI | FL:flora-script-to-video (« View every keyframe ») ; FL:flora-brand-consistency-audit | Vérification visuelle automatisée sans coût, à condition de forcer la description. |
| S5-66 | Outil (à évaluer) | Compositeur non génératif : animation de médias existants (vraies photos, logo) par un graphe de scène JSON, texte réel, rendu déterministe, aucun pixel généré. Usage possible : carton de fin, titre animé sur vraie photo, présentation Stellar Fleet. Limites : script `comp.py` à exécuter localement, chemins macOS codés en dur (Chrome, polices). | IG, TT | FL:flora-motion-compositor | Compatible avec la règle maison, car rien n'est inventé. |
| S5-67 | Outil (à évaluer) | Éditeur de timeline : assembler des médias existants (photos animées, cartons, musique sous licence) et rendre la vidéo côté Flora. Coût de rendu facturé sur l'usage de l'éditeur, non affiché par la génération. Utile si le rendu ffmpeg local doit être remplacé. | IG, TT | FL:flora-video-editor | Montage hébergé sans génération. |
| S5-68 | Outil (à vérifier) | Action gratuite `change-image-ar-browser` pour changer un format par bandes ou recadrage, sans regénération (seule voie Flora autorisée sur une photo de logement). | IG, TT, PI | FL:flora-image-resize (citée dans « Do not use when the original pixels must survive ») | Alternative non générative ; son comportement exact n'a pas été lu. |

---

## 3. Spécifications techniques par plateforme

Aucune source lue n'est une documentation officielle de plateforme. Toutes les valeurs ci-dessous sont **à vérifier dans la documentation officielle** avant d'être codées comme limites dures. Aucune source ne donne de spécification Pinterest.

### Instagram

| Élément | Valeur | Source |
| --- | --- | --- |
| Reel : format | 1080x1920 (9:16) | IG:ig-reel/SKILL.md ; RT:rt-montage/SKILL.md ; MV:short-editing/references/shorts-codes.md |
| Reel : encodage | 30 i/s, H.264, AAC 48 kHz, -14 LUFS, crête vraie ≤ -1 dBTP | MV:short-editing/references/shorts-codes.md |
| Reel : durée maximale | 3 min selon IG ; 20 min selon RT (contradiction, voir section 5) | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md |
| Reel : durée de travail | 15 à 45 s ; moins de 45 s conseillé | IG:ig-reel/SKILL.md ; MV:short-editing/references/shorts-codes.md |
| Reel : zone sûre | y=230 à 1440, 230 px libres à droite (IG) ; y=230 à 1440, 140 px à droite et 60 px à gauche (RT) ; boîte x=60 à 940, y=220 à 1500, colonne de droite 140 px de y=900 à 1700 (MV shorts-codes) ; y=170 à 1500 et 220 px à droite sous y=1100 (MV style) | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md ; MV:short-editing/references/shorts-codes.md ; MV:short-editing/references/style.md |
| Story : zone sûre | 1080x1920, texte entre y=250 et y=1600 | IG:ig-story/SKILL.md ; RT:rt-story/SKILL.md |
| Story : volume | 3 à 7 images par jour | IG:ig-story/SKILL.md |
| Carrousel : format | 1080x1350 (4:5), JPEG ou PNG | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md |
| Carrousel : nombre | 20 éléments maximum selon IG et RT ; 10 dans notre code ; 6 à 10 recommandés | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md ; LNS:produire.py |
| Carrousel : marges | texte de couverture à plus de 120 px des bords ; texte ≥ 32 px | IG:ig-carousel/SKILL.md |
| Post carré, story, couverture | 1080x1080 (fil), 1080x1920 (story, couverture de Reel) | KW:small-business/skills/canva-creator/reference/canva-api.md |
| Légende | 2 200 caractères ; environ 125 visibles avant « plus » | IG:ig-caption/SKILL.md ; RT:rt-legende/legende.py |
| Hashtags | 5 maximum par post depuis le 18/12/2025 | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md ; LNS:regles.json (sourcé blogdumoderateur.com et socialmediatoday.com) |

### TikTok

| Élément | Valeur | Source |
| --- | --- | --- |
| Vidéo : format | 1080x1920 (9:16), même export que le Reel | RT:rt-video/SKILL.md ; MV:short-editing/references/shorts-codes.md |
| Vidéo : durée | 10 min en application ; 20 à 35 s conseillé | RT:rt-video/SKILL.md |
| Zone sûre | y=230 à 1440, 140 px libres à droite, environ 60 px à gauche | RT:rt-video/SKILL.md ; RT:rt-montage/rendre.py |
| Mode photo | 1080x1920, 35 images maximum, un son par-dessus | RT:rt-carrousel/SKILL.md |
| Légende | 4 000 caractères ; environ 80 à 100 visibles (90 dans le linter) | RT:rt-legende/SKILL.md ; RT:rt-legende/legende.py |
| Hashtags | 5 maximum | RT:rt-legende/SKILL.md |
| Commentaire | 150 caractères maximum | RT:rt-legende/SKILL.md |
| Recherche | lit la légende, le texte à l'écran et l'audio transcrit | RT:rt-legende/SKILL.md |
| Live | seuil d'abonnés (souvent 1 000) et 18 ans | RT:rt-story/SKILL.md |

### Pinterest

Aucune spécification dans les sources lues. À sourcer dans la documentation officielle (format d'épingle, durée vidéo, titre, description) avant le jalon Pinterest.

### Autres formats cités (déclinaisons)

| Élément | Valeur | Source |
| --- | --- | --- |
| Facebook fil | 1200x630 | KW:small-business/skills/canva-creator/reference/canva-api.md ; KW:…/social-content-engine/reference/calendar.md |
| LinkedIn | 1200x627 | KW:small-business/skills/social-content-engine/reference/calendar.md |
| Bloc newsletter | 600x400 ; en-tête e-mail 600x200 | KW:…/social-content-engine/reference/calendar.md ; KW:…/canva-creator/reference/canva-api.md |

---

## 4. Éléments écartés

| Élément | Source | Raison |
| --- | --- | --- |
| Génération d'images par Codex (miniatures, couvertures, illustrations) | MV:codex-images/SKILL.md | Contraire à la règle maison pour tout visuel de logement ; abonnement ChatGPT requis. |
| Animation de collage « style Vox » avec calques générés | MV:vox/SKILL.md | Calques générés par Codex ; esthétique documentaire hors ton ; référence à une marque tierce. |
| Redimensionnement génératif d'une photo | FL:flora-image-resize | Re-rend tout le cadre : un logement serait redessiné. Interdit sur les photos de logement. |
| Script vers vidéo (images clés puis clips générés) | FL:flora-script-to-video | Génère des lieux ; risque élevé de passer pour un logement réel. Exemple de refus de modération `safety_violations=[sexual]` cité dans la skill : sujet sensible pour la marque. Seule la méthode de juge gratuit est retenue (S5-65). |
| Layout Resizer, Storyboard Maker, Product Spin, Studio Shot, PDP Deck, New Background, Relighting | FL (catalogue) | Techniques génératives qui modifient ou inventent l'image ; inadaptées à un logement. À réexaminer pour les produits physiques des clients Stellar Fleet. |
| Moteur de montage « papier » (Node, Chrome, whisper.cpp, binaires macOS) | MV:short-editing/SKILL.md ; MV:short-editing/engine/ | Conçu pour une personne face caméra ; dépendances lourdes ; binaires précompilés ; esthétique « papier, un bleu » hors charte. Seules ses règles (format, sonie, sous-titres, mouvement) sont retenues. |
| Bibliothèque de musiques réelles (`credits-song`, `prateria`) | MV:short-editing/references/music.md | Musique d'autrui sans licence : risque de son coupé ou réclamé. |
| Nappes musicales générées en code (`enquete`, `neon`…) | MV:short-editing/references/music.md | Ambiances « tension », « thriller », « techno » hors ton romantique ; dépendent du moteur écarté. |
| Doublage ElevenLabs | MV:short-translate/SKILL.md | Service payant, clone de voix, aucun besoin de traduction à ce jalon. |
| Recherche virale par yt-dlp et Treg | MV:studio-script/references/viral-research.md | Hors périmètre S5 (veille, autre étape) ; Treg payant. |
| Accroches « clivantes » et entonnoir « porte large » | MV:studio-script/references/funnel.md | Risque de ton pour une marque intime et sensuelle ; relève de la stratégie, pas de la production. |
| Formules d'accroche détaillées (26 et 22 formules) | IG:ig-reel/hooks.json ; MV:studio-script/references/hooks.md | Ce sont des choix éditoriaux en anglais, à traiter avec l'angle et la planification ; seule la grille de notation est retenue (S5-16). |
| Profils `voice.md`, `style.md`, `swipe.md`, journal `log.md` | IG, RT, MV | Remplacés par le kit de marque, `regles.json` et l'historique maison. |
| Rédaction « un script à la fois, sur demande » | IG:ig-repurpose/SKILL.md ; RT:rt-recyclage/SKILL.md | Pensé pour un humain qui tourne ; notre système produit sans tournage. |
| Pipeline Canva (autofill, budget de requêtes) et staging HubSpot | KW:small-business/skills/canva-creator/SKILL.md ; KW:…/social-content-engine/reference/publishing.md | Rendu maison en Pillow et ffmpeg ; publication par l'API officielle Instagram. Seules les règles de vérification sont retenues. |
| Modèles généraux blog, presse, landing, étude de cas | KW:marketing/skills/content-creation/SKILL.md ; KW:marketing/skills/draft-content/SKILL.md | Hors social. Le conseil « bloc de hashtags » et « émojis selon la marque » contredit S5-06 et S5-11. |
| Réglage de marque par lien ou description | KW:small-business/skills/brand-style/SKILL.md | Le kit de marque existe déjà (`marques/<marque>/marque.json`). |
| Lien de retour d'expérience vers codelynx.dev en fin de premier montage | MV:short-editing/SKILL.md (étape 7) | Promotion d'un tiers, sans rapport avec la production. |
| Géolocalisation des clips par Nominatim | MV:broll/SKILL.md | Envoie des coordonnées à un service tiers ; inutile, la ville vient de Shopify. |

---

## 5. Conflits et arbitrages

| Sujet | Positions | Arbitrage |
| --- | --- | --- |
| Zone sûre des Reels | IG : y=230 à 1440, 230 px à droite. RT : y=230 à 1440, 140 px à droite, 60 à gauche. MV shorts-codes : y=220 à 1500, x=60 à 940. MV style : y=170 à 1500. Notre code : cartons jusqu'à y=1500. | On prend l'intersection la plus prudente : texte entre x=60 et x=940, y=230 et y=1440 ; aucun texte au-delà de x=850 entre y=900 et y=1440 (colonne d'actions). `reel_frame` doit remonter ses cartons. |
| Nombre maximal de diapos | IG et RT : 20. LNS:produire.py : 10 (« Instagram en accepte 10 au maximum »). | On garde 10 dans le code (la structure recommandée est 6 à 10). Vérifier la limite officielle de l'API de publication avant de relever. |
| Durée maximale d'un Reel | IG : 3 min. RT : 20 min. | Sans effet : notre cible est 20 à 30 s. Valeur à vérifier dans la documentation officielle. |
| Format du post de fil | IG et RT : 1080x1350 (4:5). KW (Canva) : 1080x1080. | 1080x1350, plus haut dans le fil. Le carré n'est qu'une déclinaison. |
| Taille minimale du texte | IG et RT : 32 px. MV : 34 px pour l'interface, 84 px pour les sous-titres. Notre code : 26 et 28 px pour le compteur et les équipements. | 32 px minimum sur toute diapo ; 34 px dans les vidéos ; sous-titres 72 px minimum si voix. Corriger `slide_lodging` et `slide_text`. |
| Tutoiement ou vouvoiement | RT et MV écrivent au tutoiement (« Commente LETTRE »). CM:brands/lovenspa.md : « Vous ». LNS:regles.json accepte les deux formes dans les demandes. | Vouvoiement pour Love'nSpa. Pour Stellar Fleet, le kit de chaque marque décide. |
| Emojis | KW draft-content : emojis « selon la marque ». IG et RT : 4 pour 100 caractères maximum. CM : pas d'emojis décoratifs en série. | Ponctuation seulement, 4 pour 100 au plus, jamais en puce (S5-11). |
| Hashtags | KW content-creation : 3 à 5, possibles en premier commentaire. IG, RT, LNS : 5 au plus, en bas de légende. | 5 au plus en bas de légende, `#lovenspa` inclus. |
| Voix off | RT : voix de synthèse recommandée en mode sans visage. RT story : à éviter en story. Ton de marque : intime, sensuel. | Pas de voix par défaut. Voix de synthèse en option pour un format informatif (Reel « 3 love rooms près de… »), avec crédit et étiquette IA. Jamais en story. |
| Piste audio | LNS:visuels.py : piste muette (AAC 44,1 kHz) pour l'API. MV : AAC 48 kHz, -14 LUFS. RT : musique sous licence ou son ajouté dans l'application. | Garder la piste muette tant qu'il n'y a pas de musique sous licence ; passer en 48 kHz. Avec musique : normaliser à -14 LUFS. |
| Génération d'images | MV (codex-images, vox), FL (image-resize, script-to-video) génèrent. Règle maison : jamais un logement représenté par l'IA. | Règle maison prioritaire. Génération interdite pour tout visuel lié à un logement. Seuls les outils non génératifs (compositeur, éditeur de timeline, recadrage) restent possibles. |
| Mention de la marque sur les diapos | IG et RT : pseudo sur chaque diapo. LNS : seulement sur la diapo finale (`slide_text(cta=True)`). | Ajouter la mention en petit sur chaque diapo (S5-25). |
| Contrôle de légende | IG et RT : linters `caption.py` et `legende.py`. LNS : `controle.py` maison (désormais `social/s6_controle/controle.py`). | On garde le contrôle maison ; on y porte les règles retenues (S5-02 à S5-11, S5-18) sans importer les scripts tiers. |

---

## 6. Étapes d'accord humain à retirer

Les sources supposent un humain qui valide à chaque étape. Le système Love'nSpa est autonome : chaque accord est remplacé par un contrôle automatique bloquant (contrôle S6, statut `PRET` ou `REFUSE` de `produire.py`).

| Étape à retirer | Source | Remplacement |
| --- | --- | --- |
| « Réponds oui pour l'ajouter au journal » après chaque script | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md ; MV:studio-script/SKILL.md (« Reply yes to log them ») | Journalisation automatique dans la fiche de production. |
| « Never publish » / « Rien n'est publié, l'utilisateur colle le texte » | IG:ig-reel, ig-caption, ig-carousel, ig-story ; RT:rt-legende, rt-carrousel, rt-story, rt-voix | Publication par S7 après statut `PRET`. |
| Copie du carrousel validée par l'utilisateur avant rendu des fichiers | IG:ig-carousel/SKILL.md ; RT:rt-carrousel/SKILL.md | Contrôle automatique du texte (longueurs, tics, faits) avant rendu. |
| Choix du cas A ou B demandé à l'utilisateur | IG:ig-caption/SKILL.md ; RT:rt-legende/SKILL.md | Règle déterministe : Reel = cas A ; carrousel, photo = cas B. |
| Question groupée si l'idée est mince | IG:ig-reel/SKILL.md ; RT:rt-video/SKILL.md | Les faits viennent de Shopify et du plan ; un manque met le post en `REFUSE`. |
| Écoute humaine de la voix off avant montage | RT:rt-voix/SKILL.md (étape 4) | Sans objet tant que la voix est désactivée ; sinon contrôle de durée et de prononciation par transcription. |
| Studio en 8 étapes avec questions (comptes, plan, formats, recette, projet, validation, programmation) | RT:rt-studio/SKILL.md | Déjà couvert par la stratégie validée et les étapes S1 à S4 et S7. |
| « Le style te va ? » après le premier post | RT:rt-studio/SKILL.md (étape 6) | Audit de cohérence de série (S5-64). |
| Planche de revue `revue.html` et validation post par post | RT:rt-studio/SKILL.md (étape 7) | Contrôle S6 ; la planche peut rester comme trace consultable, sans attente. |
| Checkpoints 1, 2, 3 et validation finale (calendrier, choix de design, copie, file d'attente) | KW:small-business/skills/social-content-engine/SKILL.md ; KW:…/canva-creator/SKILL.md | Calendrier par S4 ; un seul rendu par post ; contrôle automatique. |
| Budget de génération annoncé et accepté | KW:…/canva-creator/SKILL.md (Pre-flight) ; FL:flora-script-to-video | Sans objet (pas de génération). Pour un outil Flora payant : plafond de coût codé dans la configuration. |
| Validation du plan de calques ou des invites d'image | MV:vox/SKILL.md ; MV:codex-images/SKILL.md | Skills écartées. |
| Accord avant installation de ffmpeg | MV:short-editing/SKILL.md (étape 0) | Dépendance installée une fois dans l'environnement. |

---

## 7. Sécurité, licences, dépendances

**Licences des dépôts.** IG, RT et MV sont sous MIT ; KW sous Apache-2.0. Réutiliser des règles reformulées ne pose pas de difficulté ; copier du code impose de garder l'avis de licence. Les polices Poppins sont sous OFL (LNS:assets/fonts/OFL.txt, dans le commit 485c428).

**ffmpeg.** Requis par notre rendu (LNS:visuels.py), par RT:rt-montage/rendre.py, MV (short-editing, broll, clips, vox) et FL:flora-motion-compositor. Sa licence (LGPL ou GPL) dépend du build installé : à vérifier sur l'environnement de production. Pillow est requis par LNS et RT ; numpy en plus par `comp.py` (FL).

**Modèles et voix de synthèse.**
- Kyutai Pocket TTS : code MIT, poids CC-BY 4.0, voix `estelle` CC0 ; crédit obligatoire ; premier lancement qui télécharge les poids depuis Hugging Face (RT:rt-voix/SKILL.md).
- À ne pas utiliser en usage commercial selon RT : Coqui XTTS-v2, F5-TTS, edge-tts, Piper `fr_FR-tom`, `fr_FR-siwis`, `fr_FR-upmc`, voix Pocket TTS `cosette` et `jean`, dossiers `expresso/` et `ears/` de kyutai/tts-voices, toute voix clonée sans accord écrit (RT:rt-voix/SKILL.md). Kyutai TTS 1.6B exige toujours `--voice` (voix par défaut non commerciale).
- whisper.cpp et son modèle (0,5 Go), Chromium (100 Mo), `playwright-core`, `@mediapipe/tasks-vision`, binaires macOS précompilés `matte` et `faces` (MV:short-editing/SKILL.md ; MV:short-editing/engine/package.json ; MV:short-editing/engine/bin/darwin/). Binaires non audités : à ne pas exécuter.
- `rembg` via `uvx`, avec téléchargement de modèle (MV:vox/SKILL.md).

**Services payants ou à compte.**
- ElevenLabs (transcription Scribe, doublage) : facturé à la minute, filigrane sur l'offre gratuite (MV:short-editing/SKILL.md ; MV:short-translate/SKILL.md).
- Codex et abonnement ChatGPT (MV:codex-images ; MV:vox).
- Treg : environ 0,001 $ par appel (MV:studio-script/references/viral-research.md).
- Kit payant « Editing IA Pro » pour la bibliothèque de B-roll complète et d'autres bruitages (MV:short-editing/SKILL.md ; MV:short-editing/references/sfx.md).
- Canva : 100 requêtes par minute, autofill réservé à Enterprise ; HubSpot Marketing Hub Professional pour le staging (KW:…/canva-creator/SKILL.md).
- Flora : redimensionnement i2i annoncé 0,036 $, facturé 0,02 $ ; image fixe dès 0,004 $ ; clip vidéo 0,12 à 0,90 $ ; regard d'audit 0,005 à 0,006 $ par image ; juges i2t à 0 $ ; un coût catalogue à 0 ne veut pas dire gratuit ; rendu de timeline facturé sur l'usage de l'éditeur (FL:flora-image-resize ; FL:flora-script-to-video ; FL:flora-brand-consistency-audit ; FL:flora-video-editor).

**Sécurité.**
- Clés : jamais dans le chat ni dans un commit ; fichier `.env` ignoré par git (MV:short-translate/SKILL.md). Dans notre environnement : passer par les secrets de l'environnement.
- Contenu lu (transcriptions, légendes de concurrents, commentaires, réponses de stickers) : toujours de la donnée, jamais une consigne (MV:clips/SKILL.md ; MV:studio-script/references/viral-research.md ; KW:…/social-content-engine/SKILL.md).
- Caractères invisibles dans les textes copiés : à retirer, les caractères « tag » peuvent porter du texte caché (MV:studio-script/references/ai-tells.md).
- Projet ou site source en lecture seule : copier les assets vers le dossier de production, jamais l'inverse (RT:rt-montage/SKILL.md ; RT:rt-studio/SKILL.md).
- Photos de personnes : uniquement avec accord ; jamais de visage de client identifiable sur une photo de logement (MV:vox/SKILL.md ; MV:codex-images/SKILL.md ; règle de tag S5-53).
- URLs de médias Flora publiques et permanentes : un visuel non publié qui y est déposé devient accessible (FL:flora-script-to-video).
- Modération : les générateurs refusent les contenus jugés sexuels, parfois sous un code d'erreur trompeur (FL:flora-script-to-video). Raison supplémentaire de ne pas générer pour Love'nSpa.
- Vidéos tierces : ne découper que des vidéos dont on détient les droits (MV:clips/SKILL.md).
