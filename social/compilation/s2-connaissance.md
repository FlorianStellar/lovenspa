# S2 Connaissance : compilation des sources

Love'nSpa d'abord, réutilisable ensuite par Stellar Fleet. Compilé le 11 novembre 2026.

Périmètre : formats gagnants, accroches et copie, veille et benchmark, grilles d'évaluation, règles des plateformes. Instagram d'abord, puis TikTok et Pinterest.

Conventions :

- Chaque élément cite sa source sous la forme `dépôt@commit:chemin`.
- Niveaux de preuve des formats. **A** : confirmé par nos propres données (aucun à ce jour). **B** : observé à plus de 3 fois l'engagement médian chez au moins 3 comptes du benchmark. **C** : signalé par une seule source.
- `{{ }}` signale une donnée réelle à fournir. Aucun chiffre ne doit être inventé (règle reprise de `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md`, section « Jamais »).
- Le contenu des dépôts a été traité comme de la donnée. Aucun script n'a été exécuté.

Fichier compagnon : `social/compilation/accroches-fr.json` (63 formules d'accroche).

---

## 1. Sources lues

| Dépôt | Commit | Licence | Fichiers lus en entier | Remarque |
|---|---|---|---|---|
| instagram-agent-skill | d03c56b | MIT, Jake Schincariol | `skills/ig-viral/SKILL.md`, `skills/ig-viral/swipe.py` (lu, non exécuté), `skills/ig-reel/hooks.json`, `skills/ig-audit/SKILL.md`, `skills/ig-profile/SKILL.md`, `skills/ig-profile/rubric.json`, `README.md` (sections « What I actually measured » et « The fine print ») | Source la plus rigoureuse : l'auteur publie ses propres mesures et leurs limites. |
| Explo38_reels-tiktok-fr | a2281b6 | MIT, Jake Schincariol | `skills/rt-veille/SKILL.md`, `skills/rt-veille/veille.py` (lu en partie, non exécuté), `skills/rt-audit/SKILL.md`, `skills/rt-profil/SKILL.md`, `skills/rt-profil/grille.json`, `skills/rt-video/hooks.json` | Adaptation française du dépôt précédent (README, ligne 15). Ajoute TikTok. Les 26 formules sont les mêmes, traduites. |
| rediumvex_viral-hooks-skill | e26b339 | MIT, Roman Knox | `SKILL.md`, `README.md`, `hooks-database.md`, `LICENSE`, `index.html` et `preview.html` (identiques, aucun script, un seul lien externe) | 100 formules en 10 catégories. Pied de page : adapté de `jakeolschewski/social-media-hooks-database` (MIT). Aucune mesure publiée. |
| ScrapeCreators_social-media-research-skills | 64ba7b4 | MIT, ScrapeCreators | `skills/outlier-post-finder/SKILL.md`, `skills/trend-discovery/SKILL.md`, `skills/comment-mining/SKILL.md`, `skills/competitor-social-research/SKILL.md`, `skills/creator-profile-teardown/SKILL.md`, `skills/ad-library-teardown/SKILL.md` | Méthodes solides. L'outil exige une clé d'API payante (service de collecte tiers). |
| Melvynx_video-agent-skills | f454292 | MIT, Melvyn Malherbe | `skills/outliers/SKILL.md`, `skills/outliers/references/discovery.md`, `skills/steal/SKILL.md`, `skills/steal/references/learnings.md`, `skills/insta-audit/SKILL.md`, `skills/insta-audit/references/workflow.md`, `skills/insta-audit/references/report.md` | Méthodes de calcul les plus précises (fenêtre, médiane, exclusions). Outil Treg payant pour les comptes tiers. |
| nexscope-ai_ecommerce-skills | ee0fb29 | MIT, Nexscope AI | `ecommerce-content-marketing/SKILL.md`. Skills listées par `find` (nom contenant tiktok, pinterest ou social) : `ecommerce-social-media-marketing`, `social-media-monitor`, `etsy-social-media-marketing`, `tiktok-shop-content-strategy`, `tiktok-shop-analytics`, `tiktok-shop-ads`, `tiktok-influencer-marketing`, `tiktok-shop-branding`, `tiktok-creator-marketplace`, `tiktok-shop-seller-guide`, `tiktok-shop-listing-optimization`, `tiktok-shop-cross-border`, `tiktok-shop-affiliate-program`, `tiktok-live-selling`, `tiktok-shop-promotions`, `tiktok-shop-inventory`, `tiktok-shop-fulfillment`, `tiktok-shop-customer-service`, `tiktok-shop-returns`, `tiktok-shop-creator-management`, `tiktok-shop-conversion`, `tiktok-shop-shipping`, `tiktok-shop-product-research`, `tiktok-shop-compliance`, `tiktok-shop-reviews`, `tiktok-shop-trending-products`, `tiktok-shop-pricing`, `product-differentiation/product-differentiation-tiktok`, `supply-chain-optimization/supply-chain-optimization-tiktok`, `brand-protection/brand-protection-tiktok`, `profit-margin-calculator/profit-margin-calculator-tiktok` (fichiers SKILL.md ; scripts Python non lus en détail, hors périmètre) | Aucune skill ne contient « pinterest » dans son nom. Treize skills TikTok Shop sont des coquilles vides (gabarit générique « Beta »). Chiffres de référence non sourcés. |
| Données Love'nSpa | 485c428 | interne | `claude/agent-instagram/data/benchmark-2026-11-11.md` | Fichier supprimé de cet emplacement dans l'arbre de travail et déplacé, à l'identique (vérifié par `cmp`), vers `social/donnees/lovenspa/instagram/benchmark-2026-11-11.md`. Méthode lue dans `social/s8_mesure/benchmark.py` : 50 dernières publications par compte, engagement = likes + commentaires (les vues ne sont pas exposées par l'API officielle `business_discovery`). 37 comptes lus, 3 illisibles. |

---

## 2. Méthodes retenues

### 2.1 Veille, benchmark, surperformance, audit

| ID | Méthode | Plateformes | Source | Pourquoi |
|---|---|---|---|---|
| S2-M01 | **Multiple de surperformance.** Pour chaque publication : vues ÷ médiane des vues récentes du même compte. Au-dessus de 3x : signal à étudier. Entre 1,5x et 3x : à surveiller. Sous 1,5x : journée normale, rien à apprendre. Ne jamais classer par vues brutes ni par nombre d'abonnés. | Instagram, TikTok, YouTube Shorts | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« The math ») | Seule mesure qui sépare un vrai succès de la taille du compte. 400 000 vues n'ont pas le même sens à 4 000 ou à 2 millions d'abonnés. |
| S2-M02 | **Variante engagement quand les vues manquent.** Si l'API ne donne pas les vues (cas de notre benchmark), calculer le multiple sur likes + commentaires, de façon constante par compte et par format. L'appeler « surperformance d'interactions ». Ne jamais mélanger dans un même classement des ratios sur vues et des ratios sur interactions. Si une des deux valeurs manque, la somme reste vide, pas zéro. | Instagram | `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md` (« Reproducible metrics », point 4) ; `lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md` | C'est exactement ce que mesure notre benchmark. Le nommer correctement évite de le comparer à des chiffres de vues. |
| S2-M03 | **Hygiène de l'échantillon.** 1) Médiane par compte, par plateforme et par format, jamais commune. 2) Fenêtre : publications de 7 à 180 jours ; les plus récentes gagnent encore des vues, les plus anciennes appartiennent à une autre époque du compte. 3) Moins de 10 publications dans la fenêtre : « échantillon trop petit », aucun classement. 4) Retirer les publications épinglées (anciens succès affichés en premier). 5) Mettre à part les contenus sponsorisés, concours et collaborations : ils faussent le multiple. 6) Une donnée inconnue reste inconnue, jamais zéro. 7) Recalculer au moins un ratio et une médiane à la main avant de publier un résultat. | Instagram, TikTok | `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (points 1 à 5) ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md` (« Reproducible metrics », « Completion checks ») ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (épinglées) ; `ScrapeCreators_social-media-research-skills@64ba7b4:skills/outlier-post-finder/SKILL.md` (« Common Pitfalls ») | Sans ces règles, le multiple mesure du bruit. Notre benchmark ne les applique pas encore toutes (voir « Conflits »). |
| S2-M04 | **Constitution du panel de veille.** 6 à 12 comptes, validés avant collecte : 4 directs (même niche, même offre, un peu devant), 4 voisins (autre niche, même public : on y emprunte des formats avant la niche), 2 à 4 surdimensionnés (pour le format seulement, jamais pour le rythme ni le ton). Viser des comptes à 10x maximum de notre taille. Garder chaque candidat seulement s'il publie sur la niche (lire 10 légendes), compte au moins 10 publications en 180 jours et parle la bonne langue. Noter les refus avec leur raison pour ne pas les réexaminer. Ajouter les Enregistrés (Instagram) et Favoris (TikTok) de l'équipe comme corpus. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étape 1) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 1) ; `Melvynx_video-agent-skills@f454292:skills/outliers/references/discovery.md` (points 2 et 3) | Une formule qui marche à 2 millions d'abonnés marche souvent parce qu'elle est à 2 millions d'abonnés. |
| S2-M05 | **Fiche de relevé par vidéo.** Champs : compte, plateforme, abonnés, médiane (12 dernières vidéos, épinglées exclues), vues, accroche mot pour mot (fautes comprises), premier texte à l'écran, durée en secondes, demande finale. La médiane est le champ qui compte. Les publicités du Creative Center de TikTok n'ont pas de médiane : les noter à part. | Instagram, TikTok, YouTube Shorts | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 2) ; `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étape 2) | Format de capture simple, compatible avec un relevé manuel et avec notre benchmark automatisé. |
| S2-M06 | **L'accroche réelle, pas la légende.** Une légende n'est pas une accroche parlée. Pour chaque vidéo retenue, relever la première phrase dite (transcription ou visionnage), et décrire l'image et le son seulement après les avoir vraiment regardés. Sur YouTube Shorts, l'accroche est l'ensemble des mots de sous-titres horodatés avant 3,0 secondes. | Instagram, TikTok, YouTube Shorts | `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (étape 2, dernier paragraphe) ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/report.md` (« Find competitors and outliers ») ; `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` | Notre benchmark ne relève que la première ligne de légende. Toute conclusion sur l'accroche parlée en est exclue tant que cette étape n'est pas faite. |
| S2-M07 | **Lecture par tiers.** Classer par multiple, comparer le tiers du haut et le tiers du bas, et rapporter trois choses seulement : 1) les formules sur-représentées en haut, avec leurs comptes (quatre occurrences sur six comptes, c'est un résultat ; deux, non) ; 2) ce que le haut partage structurellement (longueur de l'accroche, première image en mouvement ou non, place de la demande) ; 3) les accroches non classées, à lire à la main, car c'est là que se cachent les formules manquantes. Toujours donner la taille de l'échantillon en clair : 40 vidéos sur 6 comptes soutiennent une affirmation, 12 non. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étape 4) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 4) | Empêche de tirer une règle d'un cas isolé. |
| S2-M08 | **Recette ou chance.** Regrouper les candidats par concept (même sujet et même formule d'accroche). Un concept qui surperforme 2 fois ou plus sur un compte, ou sur 2 comptes ou plus, est une recette : il passe en premier. Un succès isolé n'est gardé que si l'accroche et la promesse l'expliquent clairement. Ensuite : écarter ce qui est hors niche, ce qui a déjà été fait chez nous, les republications (garder l'original), et pas plus de 2 sujets d'un même compte. | Instagram, TikTok | `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« 2. Pick the 5 ») | Un succès peut venir d'une tendance, d'une collaboration ou de publicité non signalée. La répétition est le meilleur filtre disponible. |
| S2-M09 | **Version maison.** Pour les trois formules du haut, écrire notre version : notre histoire, notre chiffre, dans la forme qui marche. Livrer une phrase d'accroche utilisable demain, jamais « faites une vidéo comme celle-là ». Copier la formule (forme d'accroche, structure, durée, rythme des coupes), jamais la vidéo, le script, la voix ni le montage. Attribuer chaque ligne au compte d'origine. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` (étapes 2 et 5) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (étape 5) ; `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« Honest limits ») | Transforme la veille en production sans plagiat. |
| S2-M10 | **Audit de nos propres publications.** Sur les 30 dernières (minimum 8), calculer et montrer le calcul : multiple (vues ÷ médiane du compte) ; portée hors abonnés ; rétention à 3 s (note de l'accroche) ; durée moyenne de visionnage ÷ durée de la vidéo ; partages ÷ portée (le signal le plus fort) ; (enregistrements + partages) pour 1 000 vues ; commentaires pour 1 000 vues ; abonnements ÷ portée. Classer par multiple et par partages, pas par vues. Comparer top 5 et flop 5 dans cet ordre : rétention à 3 s, formule d'accroche, format, durée (< 15 s, 15–30 s, 30–60 s, > 60 s), thème, réponse aux commentaires dans l'heure, puis jour et heure en dernier. Moins de 3 publications dans un groupe : « pas assez de données ». Exclure les publications de moins de 48 h. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-audit/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md` (étapes 2 et 3) | Les règles des guides sont des hypothèses de départ. Nos 30 dernières publications sont la preuve. |
| S2-M11 | **Diagnostic vues sans abonnés.** Une vidéo qui fait des vues et aucun abonné est un problème de profil, pas d'accroche. Une vidéo sans vues est un problème d'accroche. Si la portée hors abonnés est forte et les abonnements par portée faibles, arrêter de réécrire les accroches et passer à la grille de profil (S2-M14). | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-audit/SKILL.md` (« The distinction that saves people months ») ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` | Évite des mois de travail sur le mauvais levier. |
| S2-M12 | **TikTok : lectures en plus.** Taux de vidéos vues en entier, comparé à durée égale. Source du trafic : beaucoup de Pour Toi = poussée vers des inconnus ; beaucoup d'abonnés = restée dans la bulle ; beaucoup de recherche = le mot-clé travaille (légende, texte à l'écran, ce qui est dit) et la vidéo ramène des vues pendant des semaines. | TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` (« Sur TikTok, regarde en plus ») | Prépare l'ouverture TikTok avec les bons indicateurs. |
| S2-M13 | **Même vidéo, deux plateformes.** Publier la même vidéo sur Instagram et TikTok et comparer : même rétention à 3 s = accroche solide, l'écart vient de la distribution ; rétention meilleure d'un seul côté = chercher la différence (légende, son, texte masqué par l'interface, cadrage coupé à l'export). Calculer le multiple contre la médiane de chaque plateforme. | Instagram, TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-audit/SKILL.md` (« Instagram et TikTok, la même vidéo ») | La comparaison la plus propre possible : seule la plateforme change. |
| S2-M14 | **Grille de profil sur 100.** Douze critères notés honnêtement (un premier passage tombe souvent entre 30 et 50) : champ nom 12, première ligne de bio 12, épingles 10, activité récente 10, suite de bio 8, lien 8, temps forts ou playlists 8, lisibilité de la grille 8, photo 6, identifiant 6, catégorie et contact 6, présence en story 6. Corriger par ordre de points perdus : champ nom (« Nom \| ce que vous faites, en mots cherchés », trois options), première ligne de bio (à qui, et ce qui change), trois épingles à trois rôles (meilleure preuve, offre la plus claire, meilleure présentation), 4 à 6 temps forts nommés d'après les questions d'un client, un seul lien, couvertures choisies avec 3 ou 4 mots. Renoter et annoncer l'écart réel. Noter chaque plateforme séparément. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-profile/SKILL.md` et `rubric.json` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/SKILL.md` et `grille.json` | Le profil est un écran de décision atteint depuis une seule vidéo, avec environ trois secondes pour convaincre. |
| S2-M15 | **Recherche concurrentielle.** Pour chaque concurrent : profil (abonnés, positionnement, liens), contenus récents sur une fenêtre comparable, surperformances contre sa propre médiane, piliers, formats, styles d'accroche, cadence, offres et appels, part de la personnalité du fondateur, habitudes de commentaires. Puis chercher les écarts : sujets évités, formats qui surperforment mais peu utilisés, questions sans réponse, accroches faibles ou répétitives. Formuler les inférences au conditionnel (« semble », « suggère »). Séparer concurrents directs et aspirationnels. | Instagram, TikTok, Pinterest, autres | `ScrapeCreators_social-media-research-skills@64ba7b4:skills/competitor-social-research/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/report.md` | Structure le benchmark au-delà des chiffres. |
| S2-M16 | **Démontage d'un compte.** Positionnement (public servi, promesse, voix), piliers avec exemples, publications en surperformance, accroches et formats à reprendre, ce qu'il ne faut pas copier, tests pour nous. Chercher des mécaniques répétables, pas un résumé de profil. Ne jamais affirmer une causalité. | Instagram, TikTok | `ScrapeCreators_social-media-research-skills@64ba7b4:skills/creator-profile-teardown/SKILL.md` | Format court pour étudier un compte de référence. |
| S2-M17 | **Fouille des commentaires et des avis.** Collecter les commentaires (et les avis clients), retirer le spam, garder les mots exacts. Classer : questions, objections, plaintes, éloges, confusion, demandes, intention d'achat, débat, culture et humour. Regrouper par thème, noter fréquence et intensité, citer une phrase type par thème. Séparer un commentaire bruyant d'un motif répété. Ne pas citer de détail personnel. Côté avis : relever points de douleur, usages réels, langage émotionnel, points forts cités, hésitations avant achat (« banque de la voix client »). | Instagram, TikTok, YouTube, autres | `ScrapeCreators_social-media-research-skills@64ba7b4:skills/comment-mining/SKILL.md` ; `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` (Step 2, « Customer Voice Bank ») | Nourrit directement les formules « L'objection » et « La question mot pour mot » (A12, A16), qui exigent des mots réels. |
| S2-M18 | **Veille de tendances.** Définir niche, pays et urgence. Interroger 2 à 4 sources, regrouper par sujet, format, accroche, son ou problème du public, classer par force de la preuve et pertinence. Pas de tendance déclarée sur une seule publication. Tenir compte du pays (les tendances TikTok sont très locales). Écarter ce qui ne colle pas à la marque. Sur TikTok, le Creative Center public sert à voir les sons qui montent en France (et s'ils sont dans la bibliothèque commerciale) et les publicités de la niche qui tournent depuis des semaines. | TikTok, Instagram, YouTube, Pinterest | `ScrapeCreators_social-media-research-skills@64ba7b4:skills/trend-discovery/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (Creative Center) | Seule méthode du corpus qui couvre Pinterest (recherche Pinterest citée comme source). |
| S2-M19 | **Démontage de publicités actives.** Dans les bibliothèques publicitaires (Meta, Google, LinkedIn) : relever annonceur, date de début, type de créa, texte, titre, appel, page de destination. Regrouper par angle (douleur, cible, offre, preuve, objection traitée, comparaison, urgence). Une publicité active n'est pas une publicité gagnante ; la répétition et la durée sont des signaux. Ne jamais inventer dépense, conversion ou ciblage. | Meta (Instagram, Facebook), Google, LinkedIn | `ScrapeCreators_social-media-research-skills@64ba7b4:skills/ad-library-teardown/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` (publicités qui tournent depuis des semaines) | Montre les accroches que les concurrents paient pour diffuser. |
| S2-M20 | **Mesure du rythme de montage d'une référence.** Mesurer au lieu d'estimer : nombre de coupes franches et secondes par plan ; présence et niveau de la musique sous la voix ; place des effets sonores (sur les coupes ou non) ; taille du visage et fréquence des zooms. Nos valeurs doivent rester à l'intérieur de celles de la référence. Leçons rejetées en production : pas de bruit d'entrée à chaque élément (2 ou 3 sons par vidéo, sur les vrais temps forts), pas de montée sonore avant un temps fort, pas de fondu là où l'original coupe net, images d'illustration réelles de 0,5 à 1,5 s sur le mot d'action plutôt que des clips générés. | Instagram, TikTok | `Melvynx_video-agent-skills@f454292:skills/steal/SKILL.md` (étape 2) ; `Melvynx_video-agent-skills@f454292:skills/steal/references/learnings.md` | Transforme « un montage qui marche » en valeurs vérifiables. Les commandes ffmpeg de la source ne sont pas reprises ici (S3 production). |
| S2-M21 | **Rythme de la veille.** Une veille complète par mois, pas tous les jours : une formule tient une saison. Réaudit de nos publications un mois après chaque changement. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md` (« Offer the next step ») | Évite de courir après le bruit quotidien. |
| S2-M22 | **Score d'accroche : usage limité.** Un score textuel d'accroche sert à éliminer les accroches clairement faibles (ouverture sur une salutation, un préambule ou rien de concret), pas à choisir entre deux bonnes. Mesure publiée par l'auteur : AUC 0,83 contre des accroches volontairement mauvaises, 0,56 pour séparer les succès des échecs d'un même créateur (0,50 = pile ou face). Seul le critère de précision (chiffres, y compris dits en toutes lettres) a discriminé. Le classifieur de formules nommait 49 % des accroches réelles. | Instagram, TikTok, YouTube Shorts | `instagram-agent-skill@d03c56b:README.md` (« What I actually measured ») | Garde-fou contre la sur-confiance dans les outils de notation. |
| S2-M23 | **Combiner deux familles d'accroche.** Pour chaque vidéo, préparer trois accroches : une qui arrête le défilement (négation, chiffre précis, question), une qui retient au-delà de 3 s (récit, aveu, émotion), une libre. Rester sous 12 mots. Écrire séparément la phrase dite (environ 2 s) et le texte à l'écran (environ 1 s, 6 mots maximum). | Instagram, TikTok | `rediumvex_viral-hooks-skill@e26b339:SKILL.md` (Workflow, étapes 3 et 4) ; `instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json` (note et règle 1) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json` (règles) | Donne trois variantes testables par vidéo. |
| S2-M24 | **Tests séquencés.** Semaines 1–2 : trois styles d'accroche sur un même sujet, comparés sur les premières 24 h. Semaines 3–4 : formats (tutoriel, transformation, divertissement), sur tout l'entonnoir. Semaines 5–6 : appels à l'action directs ou doux. Revue hebdomadaire des 3 meilleurs et 3 moins bons. | TikTok, Instagram | `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` (« A/B Testing Framework », « Weekly Performance Review ») | Plan de test simple. Preuve C : aucune mesure fournie par la source. |

### 2.2 Règles des plateformes relevées

À revérifier sur la documentation officielle avant toute application : ces valeurs viennent de dépôts tiers, pas des plateformes.

| ID | Règle | Plateforme | Source |
|---|---|---|---|
| S2-R01 | Ne jamais se connecter au compte à la place de l'utilisateur ni demander de mot de passe. | Instagram, TikTok | `instagram-agent-skill@d03c56b:skills/ig-viral/SKILL.md` ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` |
| S2-R02 | La collecte automatisée en volume viole les conditions d'utilisation d'Instagram et de TikTok et fait bloquer les comptes. Lecture à vitesse humaine uniquement, pas de robot, pas de tâche de fond. | Instagram, TikTok | mêmes sources ; `instagram-agent-skill@d03c56b:README.md` (« The fine print ») |
| S2-R03 | La publication automatique passe par l'API officielle de publication de contenu (compte professionnel, application Meta, page liée, jeton longue durée, revue d'application). Commenter, suivre ou envoyer des messages par automatisation de navigateur ou outil tiers viole les conditions. Exception : les réponses automatiques par mot-clé en message privé, via les outils d'Instagram ou de partenaires agréés, déclenchées après un commentaire. | Instagram | `instagram-agent-skill@d03c56b:README.md` (« The fine print ») |
| S2-R04 | Les statistiques ne sont disponibles que pour les comptes professionnels (Créateur ou Entreprise). Certaines métriques n'apparaissent qu'après 24 à 48 h. | Instagram | `Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md` (« Honest limits ») |
| S2-R05 | Champ nom : 30 caractères, indexé par la recherche. Bio : 150 caractères sur Instagram, 80 sur TikTok. Trois publications épinglées maximum sur les deux. Instagram autorise jusqu'à 5 liens ; sur TikTok, le lien en bio dépend du type de compte et du nombre d'abonnés. | Instagram, TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/grille.json` ; `instagram-agent-skill@d03c56b:skills/ig-profile/rubric.json` |
| S2-R06 | Un compte entreprise TikTok limite les sons à la bibliothèque musicale commerciale. | TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/grille.json` (categorie_contact) ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md` |
| S2-R07 | Activité attendue pour la note pleine : une publication dans les 7 derniers jours sur Instagram, dans les 3 derniers jours sur TikTok. | Instagram, TikTok | `Explo38_reels-tiktok-fr@a2281b6:skills/rt-profil/grille.json` (activite_recente) |
| S2-R08 | Les contenus sponsorisés (#ad, mention de partenariat rémunéré, indicateur `paidPartnership` de TikTok) sont exclus des calculs de surperformance. | Instagram, TikTok | `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (point 5) |
| S2-R09 | Formats techniques indicatifs : vidéo verticale 9:16 ; épingle Pinterest verticale 2:3 avec texte en surimpression ; mots-clés Pinterest dans le titre, la description et le nom des tableaux. | TikTok, Instagram, Pinterest | `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` (« Platform-Specific Guidelines ») ; `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` (« Video Specifications ») |

---

## 3. Catalogue de formats (amorce)

Comment lire le niveau B. Notre benchmark ne donne que le type de publication, la date, le multiple d'engagement et la première ligne de légende. Le contenu visuel n'a pas été observé. Pour les formats B, la structure plan par plan est donc **proposée** à partir des règles des sources, et signalée comme telle. Les durées viennent de sources de niveau C.

Lien du benchmark pour toutes les fiches : `lovenspa@485c428:claude/agent-instagram/data/benchmark-2026-11-11.md` (copie identique : `social/donnees/lovenspa/instagram/benchmark-2026-11-11.md`).

### F01. Reel de visite sensorielle d'un logement — preuve B

- **Plateforme** : Instagram (Reels). Transposable à TikTok.
- **Objectif** : portée et conversion (hypothèse ; le benchmark ne mesure que l'engagement).
- **Observé** : 8 comptes au-dessus de 3x. Love in Room (50,1x, 11,2x, 7,2x, 4,1x, 3,6x), Chéri fais tes valises (15,5x, 7,8x, 4,5x), Let's go my love (9,9x), Les Cabanes dans les Bois (5,8x, 3,4x, 3,2x), Canopy & Stars (4,2x, 3,4x), Secret de Paris (4,0x, 3,5x), AbracadaRoom (3,1x), Attrape-Rêves (3,1x).
- **Structure proposée** (règles de `instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json`, `rules`, et `Melvynx_video-agent-skills@f454292:skills/steal/references/learnings.md`, point 4) :
  1. 0–1 s : premier plan déjà en mouvement, dans le lieu (porte qui s'ouvre, vapeur qui monte). Texte à l'écran de 6 mots maximum. Pas de mise en place.
  2. 1–8 s : détails sensoriels, plans courts de 0,5 à 1,5 s, coupe franche.
  3. Avant la moitié : l'atout promis (le spa rien qu'à deux) est montré.
  4. Fin : nom du lieu ou région, appel (lien en bio ou commentaire, voir F09).
  5. Légende : première ligne en suspens (accroche A61).
- **Durée** : 15 à 30 s (`nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md`, Instagram ; preuve C).
- **Exemples** : [Love in Room, 50,1x](https://www.instagram.com/reel/DcTr2wHI4T9/) « Une chambre, quelques marches… et un espace bien-être rien qu'à deux. » ; [Secret de Paris, 4,0x](https://www.instagram.com/reel/Dcd6dG_AdSS/) ; [Les Cabanes dans les Bois, 5,8x](https://www.instagram.com/reel/DbtYgFHILBd/).
- **Limites** : Love in Room n'a que 20 publications ; les succès de Chéri fais tes valises datent de 2025 (dernière publication il y a 177 jours).
- **Sources** : benchmark ; règles ci-dessus ; formule A24 « La révélation ».

### F02. Concours (carrousel ou Reel) — preuve B, biaisée

- **Plateforme** : Instagram.
- **Objectif** : abonnés et portée.
- **Observé** : 9 comptes au-dessus de 3x. Weekendesk (152,2x, 56,7x), Coucoo Cabanes (55,2x, 50,1x), Smartbox (39,4x), Explore France (31,8x), Staycation (31,3x), YESforLOV (8,3x), Let's go my love (7,8x, 6,1x, 5,8x), Amoureux du monde (7,4x, 6,0x, 5,1x, 3,2x), Passage du Désir (6,9x).
- **Biais** : la mécanique (commenter, identifier un ami) gonfle les commentaires. Ces publications devraient être retirées des médianes et classées à part (S2-M03, S2-R08). Le multiple ne prouve donc pas une préférence du public pour le format.
- **Structure observée dans les légendes** : titre en capitales « CONCOURS », lot chiffré (« 2 nuits », « une nuitée »), souvent un partenaire (Coucoo × Morphée, Weekendesk × hôtel), mention « terminé » ajoutée au titre après le tirage (Let's go my love, Amoureux du monde). Le contenu des diapositives n'a pas été observé.
- **Exemples** : [Coucoo Cabanes, 55,2x](https://www.instagram.com/p/DeMCq8tEV3j/) ; [Let's go my love, 7,8x](https://www.instagram.com/p/DfPDpKzjUxR/).
- **À valider hors sources** : règlement de jeu-concours et règles Meta sur les promotions (aucune source compilée ne les couvre).
- **Sources** : benchmark ; `Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md` (point 6, concours à séparer).

### F03. Carrousel sélection ou guide d'adresses — preuve B

- **Plateforme** : Instagram. Version épingle multipage sur Pinterest (F16).
- **Objectif** : enregistrement et partage.
- **Observé** : 6 comptes au-dessus de 3x. Hipcamp (9,6x « 50 favorites »), Le Bonbon (8,6x, escapades près de Paris), Millesvoyages (7,1x, astuces), Explore France (6,5x, 3,4x), Staycation (4,9x, liste de lodges avec bain nordique et bain à remous), Mr & Mrs Smith (4,6x, 3,2x, guides de ville).
- **Structure proposée** (`nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` ; formule A11) :
  1. Diapo 1 : couverture forte, promesse chiffrée (« {{N}} logements avec spa à moins de {{durée}} de {{ville}} »).
  2. Diapos 2 à N : un lieu par diapositive, une photo réelle, une ligne d'atout.
  3. Une diapositive « favori » annoncée dès la couverture.
  4. Dernière diapo : appel à enregistrer ou à partager.
- **Nombre de diapos** : 5 à 10 (source nexscope, preuve C). Sept éléments maximum dans la liste (`instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=11`, piège).
- **Exemples** : [Staycation, 4,9x](https://www.instagram.com/p/Dd4K8BxjgEG/) ; [Mr & Mrs Smith, 4,6x](https://www.instagram.com/p/DcgYiaZoMGi/).
- **Sources** : benchmark ; sources ci-dessus.

### F04. Carrousel d'un lieu unique, en reportage photo — preuve B

- **Plateforme** : Instagram.
- **Objectif** : portée et enregistrement.
- **Observé** : 5 comptes au-dessus de 3x. Bruno Maltor (65,7x, 12,8x, 5,1x, légende réduite au nom du lieu), Plum Guide (5,5x « Your own private island »), Canopy & Stars (4,3x, 3,7x), Les Plus Beaux Villages de France (4,3x), Secret de Paris (3,9x, image d'une chambre thématique).
- **Structure proposée** : diapo 1 = la plus belle vue du logement ; diapos suivantes = détails (spa, lit, lumière du soir) ; dernière = localisation. Le contenu exact des diapositives n'a pas été observé.
- **Exemples** : [Plum Guide, 5,5x](https://www.instagram.com/p/Dehf8O5Fy68/) ; [Canopy & Stars, 4,3x](https://www.instagram.com/p/De3l2XJl7hv/).
- **Sources** : benchmark.

### F05. Annonce de nouveauté ou de partenariat — preuve B

- **Plateforme** : Instagram (carrousel surtout).
- **Objectif** : portée, abonnés.
- **Observé** : 4 comptes au-dessus de 3x. YESforLOV (53,1x, artiste partenaire), Coucoo Cabanes (6,8x, nouveau domaine), Canopy & Stars (6,8x, « New to our collection »), Staycation (4,0x, 3,6x, 3,0x, collaborations et événements).
- **Structure proposée** (formule A24 « La révélation ») : diapo 1 « Nouveau » + la photo qui montre l'atout ; diapo 2 ce que ça change ; diapos suivantes détails ; dernière : quand et où réserver.
- **Exemples** : [Canopy & Stars, 6,8x](https://www.instagram.com/p/DdmVvBFjWUG/) ; [Coucoo Cabanes, 6,8x](https://www.instagram.com/p/DbDQNKeCHRc/).
- **Sources** : benchmark ; `instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=24`.

### F06. Contenu saisonnier ou daté — preuve B

- **Plateforme** : Instagram (Reel et carrousel).
- **Objectif** : portée et partage.
- **Observé** : 5 comptes au-dessus de 3x. Beautiful Destinations (35,6x, 34,3x, 33,8x, Noël), Le Bonbon (30,8x, événement), Hipcamp (14,2x, Perséides avec dates), Sortir à Paris (10,4x, 5,7x, 4,4x, 3,4x, illuminations et agenda), Weekendesk (3,0x, marchés de Noël en Alsace).
- **Structure proposée** (formule A19 « La date limite ») : accroche avec la date ou la saison ; plans du lieu dans l'ambiance de saison ; information pratique datée ; appel avant la date. L'urgence doit être vraie.
- **Exemples** : [Sortir à Paris, 10,4x](https://www.instagram.com/reel/DfPEcFqMawt/) ; [Weekendesk, 3,0x](https://www.instagram.com/reel/DfPywy5GBl3/).
- **Sources** : benchmark ; `instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=19` ; calendrier saisonnier dans `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` (Step 3).

### F07. Carrousel texte « qui parle » (phrase, mème, prise de position) — preuve B, ton à adapter

- **Plateforme** : Instagram.
- **Objectif** : partage et commentaires.
- **Observé** : 5 comptes au-dessus de 3x. Je m'en bats le clito (20,4x « Imaginez, juste. », 17,1x, 14,3x), Madmoizelle (19,1x, 10,4x, image texte), Gang du clito (8,1x, 6,5x, 6,3x), Passage du Désir (4,5x « La team anxieux.ses, vous validez ? »), Coucoo Cabanes (3,5x, tendance des émojis).
- **Limite** : la plupart des succès sont militants ou d'actualité sociale. Transposition Love'nSpa : complicité de couple, humour tendre, jamais militant ni explicite.
- **Structure proposée** : diapo 1 = une phrase courte qui se suffit ; diapos suivantes = développement en 2 à 4 phrases ; dernière = question ouverte au public.
- **Exemples** : [Passage du Désir, 4,5x](https://www.instagram.com/p/DbdrcbKjEbg/) ; [Coucoo Cabanes, 3,5x](https://www.instagram.com/p/DbF5S6oDZnf/).
- **Sources** : benchmark.

### F08. Reel incarné en série (vlog) — preuve B, peu transposable

- **Plateforme** : Instagram, avec renvoi vers YouTube.
- **Objectif** : portée et abonnés.
- **Observé** : 4 comptes au-dessus de 3x. Ben N'co (62,2x, 14,4x, 9,7x, 9,2x, 6,1x, épisodes « la suite sur YouTube »), Millesvoyages (49,0x, 6,9x), Madmoizelle (27,8x, « On a suivi… »), Bruno Maltor (3,9x).
- **Limite** : repose sur une personne à l'écran. Love'nSpa publie sans visage à ce stade. Élément transposable : la série à épisodes.
- **Exemple** : [Ben N'co, 62,2x](https://www.instagram.com/reel/DcL4im-ti9E/).
- **Sources** : benchmark.

### F09. Reel avec appel « commentez pour recevoir le lien » — preuve C

- **Plateforme** : Instagram.
- **Objectif** : conversion et commentaires.
- **Observé** : un seul compte, AbracadaRoom (3,5x, 3,2x). Le premier mot de la légende est l'appel.
- **Structure** : Reel de visite (F01) ; légende ouverte par l'appel (A63) ; réponse automatique en message après le commentaire.
- **Règle** : réponse automatique uniquement via les outils officiels ou partenaires agréés (S2-R03).
- **Exemple** : [AbracadaRoom, 3,5x](https://www.instagram.com/reel/DdDowLuOgdv/).
- **Sources** : benchmark ; `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (« Hand off », mots d'appel pour l'outil commentaire-vers-message) ; `instagram-agent-skill@d03c56b:README.md`.

### F10. Contenu éducatif sur le couple, avec une experte — preuve C

- **Plateforme** : Instagram (Reel ou carrousel).
- **Objectif** : enregistrement et partage.
- **Observé** : 2 comptes seulement (seuil B non atteint). YESforLOV (17,7x, Reel avec sexologue ; 10,8x, carrousel « 5 façons… »), Le Bonbon (5,3x, statistique sur les couples).
- **Garde-fou** : ton romantique et sensuel, jamais explicite. Sujets possibles : complicité, temps à deux, rituels. Statistique toujours sourcée (A23).
- **Sources** : benchmark.

### F11. Avant / après à l'écran — preuve C

- **Plateforme** : Instagram, TikTok.
- **Objectif** : portée.
- **Structure** (`instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=13`) : plan 1 l'avant (chambre en journée) ; coupe franche ; plan 2 l'après (bougies, spa allumé) ; une phrase sur un seul levier.
- **Durée** : non précisée par la source.
- **Exemple** : formule A13.
- **Sources** : source ci-dessus ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json#id=13` ; format « Transformation » de `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md`.

### F12. Démonstration à froid — preuve C

- **Plateforme** : Instagram, TikTok.
- **Objectif** : portée.
- **Structure** (`instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=18`) : la vidéo commence au milieu du geste (couvercle qu'on soulève, eau qui se met à bouillonner) ; résultat visible tout de suite ; si le résultat tarde, couper jusqu'à lui et montrer l'attente après.
- **Exemple** : formule A18.
- **Sources** : source ci-dessus ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json#id=18`.

### F13. POV (point de vue) — preuve C

- **Plateforme** : TikTok, Instagram.
- **Objectif** : portée.
- **Structure proposée** : texte à l'écran « POV : vous… » dès la première image ; caméra subjective qui avance dans le logement ; arrivée sur le spa.
- **Exemple** : formule A48.
- **Sources** : `rediumvex_viral-hooks-skill@e26b339:hooks-database.md#068` ; `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` (Hook Strategies) ; `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` (TikTok, « Best formats »).

### F14. Adaptation d'une tendance (son ou format du moment) — preuve C

- **Plateforme** : TikTok, Instagram.
- **Objectif** : portée.
- **Structure** (`nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md`, Template 3) : début du son ou du format tendance ; « Moi : situation qu'on reconnaît » ; « Aussi moi : la solution » ; démonstration ; appel discret.
- **Règles** : vérifier que le son est dans la bibliothèque commerciale si le compte est entreprise (S2-R06) ; écarter les tendances qui ne collent pas à la marque (S2-M18).
- **Exemple** : formule A60.
- **Sources** : source ci-dessus ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-veille/SKILL.md`.

### F15. Avis client ou contenu client repris — preuve C

- **Plateforme** : Instagram, TikTok.
- **Objectif** : conversion (preuve sociale).
- **Structure** (`nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-branding/SKILL.md`, « Customer Transformation ») : l'avant (le besoin du couple) ; l'expérience ; l'après ; nom et accord du client.
- **Exemple** : formules A25, A44.
- **Sources** : source ci-dessus ; `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-social-media-marketing/SKILL.md` (UGC, 2 fois par semaine dans leur exemple) ; `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` (« UGC Repost »).

### F16. Épingle Pinterest verticale — preuve C

- **Plateforme** : Pinterest.
- **Objectif** : trafic vers le site (recherche).
- **Structure** (`nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md`, Pinterest) : visuel vertical 2:3, texte en surimpression, couleurs vives ; mots-clés dans le titre, la description et le nom du tableau. Variante multipage pour les tutoriels pas à pas (« Idea Pins » dans la source, nom de format à vérifier).
- **Limite** : seule source Pinterest du corpus ; aucune mesure.
- **Sources** : source ci-dessus.

### F17. Face à face (comparatif tranché) — preuve C

- **Plateforme** : Instagram, TikTok.
- **Objectif** : commentaires.
- **Structure** (`instagram-agent-skill@d03c56b:skills/ig-reel/hooks.json#id=17`) : annonce des deux options ; critères montrés ; verdict net, jamais « les deux ont du bon ».
- **Exemple** : formule A17.
- **Sources** : source ci-dessus ; `Explo38_reels-tiktok-fr@a2281b6:skills/rt-video/hooks.json#id=17`.

### F18. Coulisses — preuve C

- **Plateforme** : Instagram (Stories, Reels), TikTok.
- **Objectif** : confiance.
- **Structure proposée** : préparation réelle d'un logement avant une arrivée ; aucun visage nécessaire.
- **Exemple** : formule A59.
- **Sources** : `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-social-media-marketing/SKILL.md` (« Behind-the-Scenes Content ») ; `rediumvex_viral-hooks-skill@e26b339:hooks-database.md#100`.

**Bilan** : 18 formats, 8 en preuve B (F01 à F08), 10 en preuve C, aucun en A.

---

## 4. Éléments écartés, conflits, sécurité et licence

### 4.1 Éléments écartés

| Élément | Source | Raison |
|---|---|---|
| Treize skills TikTok Shop « Beta » (promotions, stock, logistique, service client, retours, gestion des créateurs, conversion, expédition, recherche produit, conformité, avis, produits tendance, prix) et `etsy-social-media-marketing` | `nexscope-ai_ecommerce-skills@ee0fb29` | Coquilles vides : gabarit générique, aucun contenu exploitable. |
| Skills TikTok Shop de vente, publicité, affiliation, live, logistique, marges, protection de marque, différenciation | `nexscope-ai_ecommerce-skills@ee0fb29` | Hors périmètre S2 : Love'nSpa ne vend pas de produit physique sur TikTok Shop. |
| Objectifs chiffrés (taux de vue > 70 %, engagement > 5 %, clic > 2 %, conversion > 3 %, enregistrement > 1 %) | `nexscope-ai_ecommerce-skills@ee0fb29:tiktok-shop-content-strategy/SKILL.md` | Aucune source ni mesure. Ne peuvent pas servir de cible. |
| Fréquences de publication (TikTok 1 à 3 par jour, Instagram 4 à 7 par semaine, Pinterest 5 à 15 épingles par jour) et nombres de hashtags | `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-content-marketing/SKILL.md` ; `tiktok-shop-content-strategy/SKILL.md` | Non étayés. Gardés seulement comme hypothèses à tester (voir Conflits). |
| Répartition du budget influenceurs (70/20/10) et structures de campagnes publicitaires | `nexscope-ai_ecommerce-skills@ee0fb29:ecommerce-social-media-marketing/SKILL.md` ; `tiktok-shop-ads/SKILL.md` | Hors périmètre S2. |
| Points d'accès ScrapeCreators et appels Treg | `ScrapeCreators_social-media-research-skills@64ba7b4` ; `Melvynx_video-agent-skills@f454292` | Outils payants de collecte tierce. Les méthodes sont gardées, les outils non (voir Conflits, S2-R02). |
| Téléchargement de Reels tiers (yt-dlp) et mesure ffmpeg | `Melvynx_video-agent-skills@f454292:skills/steal/SKILL.md` ; `skills/outliers/SKILL.md` | Exécution de code et récupération de contenus tiers. Méthode gardée en S2-M20, commandes non reprises. |
| Scripts `swipe.py`, `veille.py`, `score_hook.py`, `minutage.py` | `instagram-agent-skill@d03c56b` ; `Explo38_reels-tiktok-fr@a2281b6` | Non exécutés (consigne). Leur logique est décrite en S2-M01, S2-M07 et S2-M22. |
| Accroches 037 « J'ai pleuré en écrivant ça », 094 « J'ai échoué publiquement… », 097 « Je suis fatigué de faire semblant » | `rediumvex_viral-hooks-skill@e26b339:hooks-database.md` | Pathos personnel, peu crédible pour une marque. |
| Accroche 058 « Combien de temps avant que… » | idem | Ressort anxiogène, contraire au ton. |
| Accroche 078 « Ce que votre médecin a dit est faux » | idem | Dénigrement d'une autorité, risque de désinformation. |
| Accroches 087, 089, 090 (taux sanguins, doses, âge de la ménopause) | idem | Allégations de santé, hors univers. |
| Exemples des sources (CV et emploi, coaching, chiffres « 73 % » sans source) | toutes les bases d'accroches | Remplacés par des exemples Love'nSpa avec `{{ }}` pour les faits. |
| `index.html` et `preview.html` | `rediumvex_viral-hooks-skill@e26b339` | Doublons de `hooks-database.md`. |
| Remake mot pour mot d'une vidéo concurrente (mêmes phrases, même ordre, ±15 % de mots) | `Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md` (étape 3) | Trop proche de la copie. On garde la formule, pas le script (S2-M09). |

### 4.2 Conflits

| Sujet | Position A | Position B | Choix retenu |
|---|---|---|---|
| Seuil de surperformance | 3x = signal, < 1,5x = normal (`ig-viral`, `rt-veille`, `outliers`) | 2x = surperformance, 3x = forte, 5x = exceptionnelle (`insta-audit/references/workflow.md`) ; 1,5–2x légère, 2–5x forte, 5x+ énorme (`outlier-post-finder`) ; 2x pour son propre compte (`outliers`, mode 2 ; `insta-audit/SKILL.md`) | 3x pour les comptes de référence (aligné sur le niveau B et le benchmark). 2x pour nos propres publications. |
| Base de la médiane | 12 dernières vidéos (`ig-viral`, `rt-veille`) | publications de 7 à 180 jours, au moins 10 (`outliers`) ; au moins 20 publications (`outlier-post-finder`) ; 50 dernières, toutes dates (notre `benchmark.py`) | Fenêtre 7–180 jours, au moins 10 publications. Notre benchmark mélange des publications de 2024 à 2026 selon les comptes (Madmoizelle, Amoureux du monde, Chéri fais tes valises) : à corriger. |
| Exclusion des publications récentes | moins de 48 h (`insta-audit/SKILL.md`) | moins de 7 jours (`insta-audit/references/workflow.md`, `outliers`) | 48 h pour nos statistiques internes, 7 jours pour la veille. |
| Médiane d'un nombre pair | la plus haute des deux valeurs du milieu (`outliers`) | moyenne des deux (Python `statistics.median`, utilisé par `benchmark.py`) | Écart mineur. Garder la méthode actuelle et la documenter. |
| Concours et sponsorisés | à exclure ou classer à part (`outliers`, `workflow.md`) | inclus dans la liste « > 3x » de notre benchmark | Les sortir des médianes et des classements au prochain passage. F02 reste B mais marqué « biaisé ». |
| Mode de collecte | lecture humaine, aucun service de scraping (`ig-viral`, `rt-veille`) | API tierces payantes (ScrapeCreators, Treg) | API officielle Meta (`business_discovery`) comme aujourd'hui, plus relevé manuel. Pas de service tiers sans validation juridique. |
| Degré de reprise | formule seulement, jamais le script (`ig-viral`, `rt-veille`, `outliers`/Honest limits) | mêmes phrases dans le même ordre (`outliers`, étape 3) | Formule seulement. |
| Répartition des piliers | 70 % éducation, 20 % coulisses, 10 % promotion (`ecommerce-social-media-marketing`) | 40/30/20/10 (`tiktok-shop-content-strategy`) ; 40/25/20/10/5 (`ecommerce-content-marketing`) | Aucune n'est étayée. Décider par l'audit (S2-M10). |
| Durée des Reels | 15–30 s (`ecommerce-content-marketing`, Instagram) | 15–60 s, 30 s idéal (`tiktok-shop-content-strategy`) ; 15–30 s (`tiktok-shop-listing-optimization`) | Hypothèse 15–30 s, à confirmer par l'audit par tranche de durée. |
| Fenêtre de l'accroche | 2 s parlées, 1 s à l'écran (`ig-reel/hooks.json`, note) | 3 premières secondes (`tiktok-shop-content-strategy`, `rediumvex` SKILL) | Écrire pour 1 à 2 s ; mesurer la rétention à 3 s. |
| Jour et heure | à vérifier en dernier, presque jamais la cause (`ig-audit`, `rt-audit`) | « meilleurs horaires » comme levier (`tiktok-shop-analytics`, `ecommerce-social-media-marketing`) | Vérifier en dernier, avec au moins 3 publications par groupe. |
| Format du fil Instagram | 1:1 (`ecommerce-social-media-marketing`) | aucune autre source | À vérifier sur la documentation officielle. |
| Métrique du benchmark | vues (toutes les méthodes de surperformance) | likes + commentaires (notre benchmark, API sans vues) | Nommer « surperformance d'interactions » (S2-M02). Pas de comparaison avec des multiples de vues. |

### 4.3 Sécurité et licence

**Licences.** Les six dépôts sont sous licence MIT. Titulaires : Jake Schincariol (deux dépôts), Roman Knox, ScrapeCreators, Melvyn Malherbe, Nexscope AI. La base de rediumvex déclare s'inspirer de `jakeolschewski/social-media-hooks-database` (MIT). Nos fichiers adaptent, traduisent et réécrivent ; ils ne copient pas de portion substantielle telle quelle. Si un texte source est un jour repris tel quel dans un produit Stellar Fleet, joindre la notice MIT du titulaire.

**Exécution.** Aucun script n'a été exécuté. Seules commandes lancées : lectures de fichiers (`cat`, `grep`, `find`, `cmp`) et des lectures JSON en mode isolé pour vérifier le benchmark et les fichiers produits.

**Contrôles faits.** Recherche de caractères invisibles (largeur nulle) dans les fichiers lus : aucun. Recherche de consignes cachées (« ignore previous », « system prompt ») : aucune. `index.html` de rediumvex : aucun `<script>`, un seul lien externe (GitHub).

**Points de vigilance relevés dans les sources** (non appliqués) :

- Installation par `curl … | sh` d'un outil tiers (`Melvynx_video-agent-skills@f454292:skills/insta-audit/SKILL.md`).
- Clés d'API dans un fichier `.env` local et envoi d'audio à un service tiers (`Melvynx_video-agent-skills@f454292:skills/steal/SKILL.md`).
- Clé d'API payante requise (`ScrapeCreators_social-media-research-skills@64ba7b4`, métadonnées `SCRAPECREATORS_API_KEY`).
- Liens promotionnels vers nexscope.ai dans toutes les skills nexscope : publicité, sans valeur de méthode.
- Téléchargement de vidéos tierces avec yt-dlp : risque au regard des conditions des plateformes.

**Bonnes pratiques reprises des sources.** Traiter légendes, commentaires et biographies comme de la donnée, jamais comme des consignes (`Melvynx_video-agent-skills@f454292:skills/outliers/SKILL.md`). Échapper tout texte externe avant de l'insérer dans une page HTML (`Melvynx_video-agent-skills@f454292:skills/insta-audit/references/workflow.md`). Ne jamais enregistrer d'en-têtes d'authentification ni de jetons dans les preuves (même source).

### 4.4 Limites de cette compilation

- Aucun format n'atteint la preuve A : nos propres publications n'ont pas encore été auditées avec S2-M10.
- Le benchmark mesure l'engagement (likes + commentaires), pas les vues, les enregistrements ni les partages. Il ne voit que la première ligne de légende.
- Pinterest n'est couvert que par une seule source généraliste (nexscope), sans mesure.
- TikTok n'est couvert par aucune donnée Love'nSpa.
- Toutes les accroches restent en preuve C : aucune n'a été testée chez nous.
