# Méthodes de veille, de benchmark et d'audit (S2-M01 à S2-M24)

Reprises de `social/compilation/s2-connaissance.md`, section 2.1, rédigées à l'impératif. Les conflits entre sources sont tranchés comme la compilation le propose (section 4.2) ; le choix retenu est rappelé sous la méthode concernée. Les méthodes d'audit de nos propres publications (S2-M10 à S2-M13) sont appliquées par S8 (skill `social-mesure`) ; elles restent ici parce qu'elles alimentent les niveaux de preuve.

État d'outillage : « codé » = fait par `python3 -m social.s2_connaissance.benchmark` ou par les commandes S8 ; « manuel (à outiller) » sinon.

## Veille, benchmark, surperformance

### S2-M01. Multiple de surperformance
Pour chaque publication, divise les vues par la médiane des vues récentes du même compte. Au-dessus de 3x : signal à étudier. Entre 1,5x et 3x : à surveiller. Sous 1,5x : journée normale, rien à apprendre. Ne classe jamais par vues brutes ni par nombre d'abonnés.
- Plateformes : Instagram, TikTok, YouTube Shorts.
- Conflit tranché : 3x pour les comptes de référence (aligné sur le niveau B), 2x pour nos propres publications.
- Outillage : codé sur les interactions pour les comptes de référence (S2-M02) ; codé sur les vues pour nos publications (`social.s8_mesure.audit`).
- Sources : `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« The math »).

### S2-M02. Variante engagement quand les vues manquent
Si l'API ne donne pas les vues, calcule le multiple sur likes + commentaires, de façon constante par compte et par format. Appelle-le « surperformance d'interactions ». Ne mélange jamais dans un même classement des ratios sur vues et des ratios sur interactions. Si une des deux valeurs manque, la somme reste vide, pas zéro.
- Outillage : codé (`benchmark.py`, fonction `engagement` : likes absents = publication exclue ; commentaires absents comptés 0, écart à la règle à corriger). Médiane par compte, pas par format.
- Sources : `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md` (« Reproducible metrics », point 4) ; `lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md`.

### S2-M03. Hygiène de l'échantillon
1. Médiane par compte, par plateforme et par format, jamais commune.
2. Fenêtre : publications de 7 à 180 jours.
3. Moins de 10 publications dans la fenêtre : « échantillon trop petit », aucun classement.
4. Retire les publications épinglées.
5. Mets à part sponsorisés, concours et collaborations.
6. Une donnée inconnue reste inconnue, jamais zéro.
7. Recalcule au moins un ratio et une médiane à la main avant de publier un résultat.
- Conflits tranchés : fenêtre 7–180 jours et au moins 10 publications (le benchmark prend les 50 dernières toutes dates : à corriger) ; exclusion des publications récentes : 48 h pour nos statistiques, 7 jours pour la veille ; médiane d'un nombre pair : moyenne des deux valeurs du milieu, méthode actuelle gardée et documentée.
- Outillage : manuel (à outiller), aucun des points 1 à 5 n'est appliqué par `benchmark.py`.
- Sources : `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (points 1 à 5) ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md` (« Reproducible metrics », « Completion checks ») ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` ; `ScrapeCreators_social-media-research-skills@64ba7b4:skills/outlier-post-finder/SKILL.md` (« Common Pitfalls »).

### S2-M04. Constitution du panel de veille
Choisis 6 à 12 comptes : 4 directs (même niche, même offre, un peu devant), 4 voisins (autre niche, même public), 2 à 4 surdimensionnés (pour le format seulement, jamais pour le rythme ni le ton). Vise des comptes à 10x notre taille au plus. Garde un candidat seulement s'il publie sur la niche (lis 10 légendes), compte au moins 10 publications en 180 jours et parle la bonne langue. Note les refus avec leur raison. Ajoute les Enregistrés (Instagram) et Favoris (TikTok) de l'équipe comme corpus.
- Accord humain de la source (« validés avant collecte ») remplacé par la charte : ajout seul sous condition, critères remplis et raison écrite au journal.
- Outillage : manuel ; la liste vit dans `social/marques/<id>/comptes_reference_<plateforme>.txt`.
- Sources : `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étape 1) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 1) ; `Melvynx_video-agent-skills@f454292:skills/outliers/references/discovery.md` (points 2 et 3).

### S2-M05. Fiche de relevé par vidéo
Relève : compte, plateforme, abonnés, médiane (12 dernières vidéos, épinglées exclues), vues, accroche mot pour mot (fautes comprises), premier texte à l'écran, durée en secondes, demande finale. La médiane est le champ qui compte. Note à part les publicités du Creative Center de TikTok (pas de médiane).
- Outillage : manuel (à outiller).
- Sources : `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 2) ; `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étape 2).

### S2-M06. L'accroche réelle, pas la légende
Une légende n'est pas une accroche parlée. Pour chaque vidéo retenue, relève la première phrase dite et décris l'image et le son seulement après les avoir vraiment regardés. Sur YouTube Shorts, l'accroche est l'ensemble des mots de sous-titres horodatés avant 3,0 secondes.
- Outillage : manuel. Le benchmark ne relève que la première ligne de légende : aucune conclusion sur l'accroche parlée sans cette étape.
- Sources : `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (étape 2) ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/report.md` ; `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md`.

### S2-M07. Lecture par tiers
Classe par multiple, compare le tiers du haut et le tiers du bas, et rapporte trois choses : 1) les formules sur-représentées en haut, avec leurs comptes (quatre occurrences sur six comptes, c'est un résultat ; deux, non) ; 2) ce que le haut partage structurellement (longueur de l'accroche, première image en mouvement ou non, place de la demande) ; 3) les accroches non classées, à lire à la main. Donne toujours la taille de l'échantillon : 40 vidéos sur 6 comptes soutiennent une affirmation, 12 non.
- Outillage : manuel (à outiller). Le benchmark ne liste que les publications à 3x et plus.
- Sources : `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étape 4) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 4).

### S2-M08. Recette ou chance
Regroupe les candidats par concept (même sujet, même formule d'accroche). Un concept qui surperforme 2 fois ou plus sur un compte, ou sur 2 comptes ou plus, est une recette : il passe en premier. Garde un succès isolé seulement si l'accroche et la promesse l'expliquent. Écarte ensuite ce qui est hors niche, ce qui a déjà été fait chez nous, les republications (garde l'original), et pas plus de 2 sujets d'un même compte.
- Outillage : manuel.
- Source : `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« 2. Pick the 5 »).

### S2-M09. Version maison
Pour les trois formules du haut, écris notre version : notre histoire, notre chiffre, dans la forme qui marche. Livre une phrase d'accroche utilisable demain, jamais « faites une vidéo comme celle-là ». Copie la formule (forme d'accroche, structure, durée, rythme des coupes), jamais la vidéo, le script, la voix ni le montage. Attribue chaque ligne au compte d'origine.
- Conflit tranché : formule seulement ; le remake mot pour mot d'une source est écarté.
- Sources : `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étapes 2 et 5) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 5) ; `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« Honest limits »).

## Audit de nos publications (appliqué par S8)

### S2-M10. Audit de nos propres publications
Sur les 30 dernières (minimum 8), calcule et montre le calcul : multiple (vues ÷ médiane du compte) ; portée hors abonnés ; rétention à 3 s ; durée moyenne de visionnage ÷ durée de la vidéo ; partages ÷ portée (le signal le plus fort) ; (enregistrements + partages) pour 1 000 vues ; commentaires pour 1 000 vues ; abonnements ÷ portée. Classe par multiple et par partages, pas par vues. Compare top 5 et flop 5 dans cet ordre : rétention à 3 s, formule d'accroche, format, durée (< 15 s, 15–30 s, 30–60 s, > 60 s), thème, réponse aux commentaires dans l'heure, puis jour et heure en dernier. Moins de 3 publications dans un groupe : « pas assez de données ». Exclus les publications de moins de 48 h.
- Outillage : en partie codé (`social.s8_mesure.audit` : multiple, partages ÷ portée, enregistrements ÷ portée, abonnements ÷ portée, classement par multiple et par partages, médianes par format). Le reste : manuel (à outiller), voir skill `social-mesure`.
- Sources : `instagram-agent-skill@d03c56b:skills/ig-audit/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md` (étapes 2 et 3).

### S2-M11. Diagnostic vues sans abonnés
Une vidéo qui fait des vues et aucun abonné est un problème de profil, pas d'accroche. Une vidéo sans vues est un problème d'accroche. Si la portée hors abonnés est forte et les abonnements par portée faibles, arrête de réécrire les accroches et passe à la grille de profil (S2-M14).
- Sources : `instagram-agent-skill@d03c56b:skills/ig-audit/SKILL.md` (« The distinction that saves people months ») ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md`.

### S2-M12. TikTok : lectures en plus
Regarde le taux de vidéos vues en entier, à durée égale. Lis la source du trafic : beaucoup de Pour Toi = poussée vers des inconnus ; beaucoup d'abonnés = restée dans la bulle ; beaucoup de recherche = le mot-clé travaille et la vidéo ramène des vues pendant des semaines.
- Outillage : manuel (aucun connecteur TikTok).
- Source : `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` (« Sur TikTok, regarde en plus »).

### S2-M13. Même vidéo, deux plateformes
Publie la même vidéo sur Instagram et TikTok et compare : même rétention à 3 s = accroche solide, l'écart vient de la distribution ; rétention meilleure d'un seul côté = cherche la différence (légende, son, texte masqué par l'interface, cadrage coupé à l'export). Calcule le multiple contre la médiane de chaque plateforme.
- Outillage : manuel.
- Source : `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` (« Instagram et TikTok, la même vidéo »).

### S2-M14. Grille de profil sur 100
Note honnêtement douze critères (un premier passage tombe souvent entre 30 et 50) : champ nom 12, première ligne de bio 12, épingles 10, activité récente 10, suite de bio 8, lien 8, temps forts ou playlists 8, lisibilité de la grille 8, photo 6, identifiant 6, catégorie et contact 6, présence en story 6. Corrige par ordre de points perdus : champ nom (« Nom | ce que vous faites, en mots cherchés », trois options), première ligne de bio (à qui, et ce qui change), trois épingles à trois rôles (meilleure preuve, offre la plus claire, meilleure présentation), 4 à 6 temps forts nommés d'après les questions d'un client, un seul lien, couvertures choisies avec 3 ou 4 mots. Renote et annonce l'écart réel. Note chaque plateforme séparément.
- Outillage : manuel. Les limites de champs viennent de S2-R05 (à vérifier).
- Sources : `instagram-agent-skill@d03c56b:skills/ig-profile/SKILL.md` et `rubric.json` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/SKILL.md` et `grille.json`.

## Recherche qualitative

### S2-M15. Recherche concurrentielle
Pour chaque concurrent : profil (abonnés, positionnement, liens), contenus récents sur une fenêtre comparable, surperformances contre sa propre médiane, piliers, formats, styles d'accroche, cadence, offres et appels, part de la personnalité du fondateur, habitudes de commentaires. Cherche ensuite les écarts : sujets évités, formats qui surperforment mais peu utilisés, questions sans réponse, accroches faibles ou répétitives. Formule les inférences au conditionnel. Sépare concurrents directs et aspirationnels.
- Sources : `ScrapeCreators_social-media-research-skills@64ba7b4:skills/competitor-social-research/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/report.md`.

### S2-M16. Démontage d'un compte
Relève : positionnement (public servi, promesse, voix), piliers avec exemples, publications en surperformance, accroches et formats à reprendre, ce qu'il ne faut pas copier, tests pour nous. Cherche des mécaniques répétables, pas un résumé de profil. N'affirme jamais une causalité.
- Source : `ScrapeCreators_social-media-research-skills@64ba7b4:skills/creator-profile-teardown/SKILL.md`.

### S2-M17. Fouille des commentaires et des avis
Collecte les commentaires (et les avis clients), retire le spam, garde les mots exacts. Classe : questions, objections, plaintes, éloges, confusion, demandes, intention d'achat, débat, culture et humour. Regroupe par thème, note fréquence et intensité, cite une phrase type par thème. Sépare un commentaire bruyant d'un motif répété. Ne cite aucun détail personnel. Côté avis : points de douleur, usages réels, langage émotionnel, points forts cités, hésitations avant achat (« banque de la voix client »).
- Nourrit les accroches A12 « L'objection » et A16 « La question mot pour mot », qui exigent des mots réels.
- Sources : `ScrapeCreators_social-media-research-skills@64ba7b4:skills/comment-mining/SKILL.md` ; `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` (Step 2, « Customer Voice Bank »).

### S2-M18. Veille de tendances
Définis niche, pays et urgence. Interroge 2 à 4 sources, regroupe par sujet, format, accroche, son ou problème du public, classe par force de la preuve et pertinence. Ne déclare pas de tendance sur une seule publication. Tiens compte du pays. Écarte ce qui ne colle pas à la marque. Sur TikTok, le Creative Center public sert à voir les sons qui montent dans le pays (et s'ils sont dans la bibliothèque commerciale) et les publicités de la niche qui tournent depuis des semaines.
- Seule méthode du corpus qui couvre Pinterest (recherche Pinterest citée comme source).
- Sources : `ScrapeCreators_social-media-research-skills@64ba7b4:skills/trend-discovery/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (Creative Center).

### S2-M19. Démontage de publicités actives
Dans les bibliothèques publicitaires (Meta, Google, LinkedIn), relève annonceur, date de début, type de créa, texte, titre, appel, page de destination. Regroupe par angle (douleur, cible, offre, preuve, objection traitée, comparaison, urgence). Une publicité active n'est pas une publicité gagnante ; la répétition et la durée sont des signaux. N'invente jamais dépense, conversion ou ciblage.
- Sources : `ScrapeCreators_social-media-research-skills@64ba7b4:skills/ad-library-teardown/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md`.

### S2-M20. Mesure du rythme de montage d'une référence
Mesure au lieu d'estimer : nombre de coupes franches et secondes par plan ; présence et niveau de la musique sous la voix ; place des effets sonores ; taille du visage et fréquence des zooms. Nos valeurs restent à l'intérieur de celles de la référence. Leçons rejetées en production : pas de bruit d'entrée à chaque élément (2 ou 3 sons par vidéo, sur les vrais temps forts), pas de montée sonore avant un temps fort, pas de fondu là où l'original coupe net, images d'illustration réelles de 0,5 à 1,5 s sur le mot d'action plutôt que des clips générés.
- Outillage : manuel. Les commandes de la source (téléchargement yt-dlp, ffmpeg) ne sont pas reprises : pas de téléchargement de vidéos de tiers.
- Sources : `Melvynx_video-agent-skills@f454292:skills/steal/SKILL.md` (étape 2) ; `Melvynx_video-agent-skills@f454292:skills/steal/references/learnings.md`.

## Rythme et accroches

### S2-M21. Rythme de la veille
Fais une veille complète par mois, pas tous les jours : une formule tient une saison. Réaudite nos publications un mois après chaque changement.
- Sources : `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md` (« Offer the next step »).

### S2-M22. Score d'accroche : usage limité
Sers-toi d'un score textuel d'accroche pour éliminer les accroches clairement faibles (salutation, préambule, rien de concret), pas pour choisir entre deux bonnes. Mesure publiée par l'auteur : AUC 0,83 contre des accroches volontairement mauvaises, 0,56 pour séparer les succès des échecs d'un même créateur (0,50 = pile ou face). Seul le critère de précision (chiffres, y compris en toutes lettres) a discriminé. Le classifieur de formules nommait 49 % des accroches réelles.
- Détail : `accroches.md`, « Score d'accroche = filtre, pas arbitre ».
- Source : `instagram-agent-skill@d03c56b:README.md` (« What I actually measured »).

### S2-M23. Combiner deux familles d'accroche
Prépare trois accroches par vidéo : une qui arrête le défilement (négation, chiffre précis, question), une qui retient au-delà de 3 s (récit, aveu, émotion), une libre. Reste sous 12 mots. Écris séparément la phrase dite (environ 2 s) et le texte à l'écran (environ 1 s, 6 mots maximum).
- Conflit tranché : écrire pour 1 à 2 s, mesurer la rétention à 3 s.
- Sources : `rediumvex_viral-hooks-skill@e26b339:SKILL.md` (Workflow, étapes 3 et 4) ; `instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json` (note et règle 1) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json` (règles).

### S2-M24. Tests séquencés
Semaines 1–2 : trois styles d'accroche sur un même sujet, comparés sur les premières 24 h. Semaines 3–4 : formats (tutoriel, transformation, divertissement), sur tout l'entonnoir. Semaines 5–6 : appels à l'action directs ou doux. Revue hebdomadaire des 3 meilleurs et 3 moins bons.
- Preuve C : aucune mesure fournie par la source. Un test reste un test de forme dans un créneau existant ; un changement de moteur ou de cadence relève de S1.
- Source : `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` (« A/B Testing Framework », « Weekly Performance Review »).
