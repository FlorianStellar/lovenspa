# Journal des déploiements SEO — lovenspa.fr

Convention : une entrée par lot, newest first.
Colonnes : date déploiement · lot · levier · URLs modifiées · témoin · date lecture · verdict

---

## Lots actifs

| # | Déployé | Lot | Levier | N URLs | Témoin | Lecture prévue | Verdict |
|---|---|---|---|---|---|---|---|
| L6 | 02/11/2026 | 25 fiches 404 (churn) | Status DRAFT/ARCHIVED/UNLISTED→ACTIVE + templateSuffix=produit-churn (corrigé le jour même : premier passage en `churn`, suffixe inexistant dans le thème lovenspa 4.1, fiches servies quelques heures sur le template produit standard) | 25 | Sans témoin : action de récupération 404→200, suivi non causal (impressions et clics des 25 URL à J+21 vs 90 j avant) | 23/11/2026 | en cours. Rendu non vérifié : lovenspa.fr bloqué par le réseau de l'environnement. |
| L5 | 13/10/2026 | collection `/collections/love-room` | Réécriture éditoriale (9 H2, FAQPage 7Q, 47 liens, chiffres oct.) | 1 | `/pages/guide-qu-est-ce-love-room` | 27/10/2026 · **24/11/2026** | ✓ J+14 positif : pos 12.0→9.1, impr 3 692→5 473. Guide recule (8.7→10.5), pas de cannibalisation. Lecture définitive 24/11. |
| L4 | 28/09/2026 | 35 metas fiches | SEO title + meta description | 35 | 35 témoins figés | 02/11/2026 | ✓ J+35 positif : 0 régression sur top 70 fiches, gain médian −2.5 pos. Lire L4 paire-à-paire après récup liste Shopify. |
| L3 | 28/09/2026 | 17 fiches lot témoin | Body optimisé (structure + FAQ) | 17 | 16 témoins, 6 groupe B | 26/10/2026 | ⚠ Non conclusif : liste exacte non disponible. Récupérer URLs via Shopify (metafield seo-lot=L3). |
| L2 | 28/09/2026 | JSON-LD ItemList | Données structurées collections | 1 | n/a | 27/10/2026 | EN RETARD |
| L1 | 28/09/2026 | Robots + pagination | robots.txt réécrit ; 24/page + éditorial p.1 | n/a | n/a | — | déployé |

## Événements hors lots (contaminent les lectures)

- 03/11/2026 10:12 UTC : `bubble-pink` réactivée hors agent (ACTIVE, template standard, réservable à 200 €, vérifié via l'API Shopify). Elle n'est plus une fiche churn : retirée du périmètre de A1/L7 et de E17. C'est l'URL la plus affichée sur « love room » (pos. 9,0). La lecture de L5 et la cible O1 sont à interpréter avec cette réserve.
- 02/11/2026 16:02 UTC : collection `love-room` modifiée hors agent (titre actuel « Love Rooms en France : toutes nos adresses vérifiées »). Touche l'URL du lot L5 : lecture du 24/11 à interpréter avec cette réserve.
- Semaine du 28/09/2026 : langue `en` retirée de la boutique (seule `fr` publiée). Segment `/en/` : 47 526 impressions en S39, 785 en S44. Robots.txt vérifié : ne bloque pas `/en/`.

## Décisions de Florian

- 02/11/2026 : retrait de la langue anglaise volontaire.
- 02/11/2026 : pas de fusion des articles cannibalisés (massage tantrique, kamasutra, sofa tantra) ; traitement par maillage interne (action C2, niveau A).
- 02/11/2026 : « love room » → URL cible unique `/collections/love-room` (confirmé). Les autres URL classées sur la requête (bubble-pink, /pages/loveroom, guide) doivent y renvoyer et viser une autre intention.
- 02/11/2026 : V1 accès écriture GitHub donné ; V4 go noindex `/en/pages/guide-qu-est-ce-love-room` ; V5 go lien churn vers `/collections/love-room`.

## Constats agent du 02/11/2026

- V4 sans objet : `/en/pages/guide-qu-est-ce-love-room` répond 301 vers `/pages/guide-qu-est-ce-love-room` (200). Une 301 ne peut pas porter de noindex et consolide déjà vers la page FR. Échantillon `/en/` : `/en/` 301 vers `/`, fiches et pages 301 vers FR, `/en/collections/love-room` 404, `/en/blogs/news` 301 vers `/en/blogs/sexo` (chaîne à vérifier).
- V5 : écriture API sur le thème MAIN bloquée par Shopify. Code prêt : `claude/theme/V5-loven-churn-lien-love-room.md`, collage manuel par Florian.
- Haloscan : API joignable avec la clé de l'environnement (crédits au 02/11 : 9 819 mots-clés, 2 448 site).

## Constats agent du 03/11/2026

- Shopify CLI opérationnel (SHOPIFY_FLAG_STORE / SHOPIFY_CLI_THEME_TOKEN présents). Thème live confirmé : lovenspa 4.1 #188545007952.
- V5 : `theme pull` de `sections/loven-churn.liquid` sur MAIN, md5 6d0a9ef7f67399bd338d36cc90b29596 (9 460 o), identique au relevé du 02/11. Sauvegarde : `claude/theme/backup/loven-churn.liquid.2026-11-03.orig`.
- V5 patché et testé (1 lien `churn-love-room`, grille/CTA/JSON-LD intacts) : `claude/theme/pret-a-pousser/sections/loven-churn.liquid`, md5 8911557bcf9749463806572b99020a7d (9 962 o).
- V5 : le `theme push` brut a été refusé par la politique de sécurité. Florian a ajouté l'autorisation de `theme_publish.sh` dans `.claude/settings.json`.
- **V5 PUBLIÉ le 03/11/2026** via `theme_publish.sh` :
  - pull du live : md5 6d0a9ef7… identique à la base ;
  - push, puis pull de vérification : md5 8911557bcf9749463806572b99020a7d.
  - Contrôle E2E sur chambre-bien-etre, la-desirade et espace-prive-1 : HTTP 200, exactement 1 lien `/collections/love-room` (`churn-love-room`), grille, CTA et JSON-LD ItemList présents.
  - Événement hors lot : il ajoute un lien entrant vers la cible du lot L5.
- T1, audit complet de l'indexation des fiches (tâche planifiée du 03/11) :
  - périmètre : les 1 791 produits Shopify. Le chiffre de « 675 restantes » ne correspondait à aucun jeu de données ;
  - 0 erreur d'API, synthèse validée par le QA ;
  - fiches actives : 1 203 / 1 235 indexées (97,4 %) ;
  - 29 fiches actives répondent 200 sans être indexées (dont 16 churn vues en 404 par Google, crawl antérieur au 02/11) ;
  - 3 fiches actives ont un onlineStoreUrl vide et répondent 404 ;
  - 2 fiches UNLISTED sont indexées et répondent 200 ;
  - bubble-pink indexée, crawl du 03/11 (T5 résolu).
  Fichiers : `claude/audit-indexation-fiches-2026-11-03.csv`, `claude/audit-indexation-anomalies-2026-11-03.tsv`.

## Veille indexation du 04/11/2026

- Périmètre : 616 URL, soit les 97 fiches actives modifiées depuis 48 h, les 32 fiches actives non indexées le 03/11 et les 506 collections du sitemap (19 fiches sont dans les deux premières listes). Les 481 collections « modifiées » sur 48 h couvrent en pratique presque toutes les collections.
- Résultat partiel : 119 collections inspectées, toutes « Submitted and indexed », sans écart de canonical.
- Quota URL Inspection épuisé (HTTP 429) après la 119e URL, à 05:30 UTC. L'audit T1 de la veille en avait consommé 1 791.
- Toujours épuisé à 08:45 UTC : la remise à zéro n'est pas à 08:00 UTC (règle exacte non documentée, non vérifiée). Reprise planifiée à 15:30 UTC.
- Règle ajoutée : pas plus de 1 500 inspections un jour où la veille du lendemain est prévue. Les audits mensuels sont à étaler sur plusieurs jours.
- Proposition à Florian (à valider) : décaler la veille quotidienne de 06:23 à 09:23.
- Quota revenu à 15:30 UTC. Inspection terminée : 616 URL, 0 erreur (`claude/veille/veille-2026-11-04.csv`). Aucun écart de canonical.
- Suivi des 32 fiches actives non indexées le 03/11 :
  - 11 sont maintenant indexées : 4 qui étaient « 404 », 4 « découvertes », 3 « inconnues » ;
  - 21 restent non indexées : 13 toujours en 404 pour Google, 4 inconnues, 2 découvertes non indexées (dont 1 vue « découverte » le 03/11 et « inconnue » le 04/11), 1 en noindex, 1 en redirection.
  - Les 13 en 404 n'ont pas été recrawlées : dernier passage entre le 10/07 et le 31/10, toutes avant la republication du 02/11. Elles répondent 200 depuis (vérifié le 03/11).
- Fiches modifiées depuis 48 h, hors liste des 32 : aucune anomalie.
- Collections : 502 / 506 indexées. Les 4 autres :
  - `tous-les-departements` et `toutes-les-regions` : HTTP 200 avec `noindex, follow` dans le code rendu. Choix probablement voulu dans le thème, à confirmer par Florian.
  - `smart-proudct-filter-search-test` : collection de test publique (HTTP 200, 26 liens produits, présente dans le sitemap), « Crawled - currently not indexed ». Je propose de la dépublier (Go).
  - `provence-verte` : HTTP 200, « Crawled - currently not indexed », dernier crawl le 21/04.
- Aucune page clé touchée, donc pas de message privé Slack.

## Veille indexation du 05/11/2026

- 590 URL, 0 erreur : 63 fiches actives modifiées depuis 48 h, 21 fiches suivies et les 506 collections du sitemap. Aucun écart de canonical. Fichier : `claude/veille/veille-2026-11-05.csv`.
- Aucune nouvelle anomalie par rapport au 04/11.
- Fiches suivies : 1 nouvelle indexée, 20 encore non indexées :
  - 13 en 404 pour Google, toujours sans nouveau crawl ;
  - 5 inconnues ;
  - 1 en noindex ;
  - 1 en redirection.
- Collections : mêmes 4 anomalies que le 04/11. Décisions en attente.
- 05/11 : 3 tâches récurrentes du 02/11 désactivées (doublons de la session du 03/11) : veille quotidienne trig_011n41…, compte rendu hebdo trig_01RigK…, audit mensuel trig_01E1sz…. Lectures L6 (23/11) et L5 (24/11) conservées. Veille du 03/11 (trig_019HhJ…) : sa consigne pointe la branche peaceful-cannon-klj2cv ; les 6 tâches de la session du 03/11 pointent peaceful-cannon : fusionnée dans zen-edison le 05/11, bascule des prompts à valider par Florian dans cette session.

## CSS / fichiers thème en attente de push par Florian

- CSS de lecture + repositionnement mobile bloc éditorial (écrit en local, branche `claude/zen-edison-sac366`)
- ~~V5~~ publié le 03/11

---

## Crawl technique du 05/11/2026

- 2 873 URL du sitemap : 2 837 en 200, 36 articles en 429 (Shopify), 0 en 3xx/4xx/5xx. Données : `claude/audits/tech-2026-11-05/`.
- Liens internes : 16 cibles en 404, 22 en 301 (liste : `liens_hors_sitemap_statuts.txt`). Pages sources à relever (crawler à compléter).
- noindex dans le sitemap : tous-les-departements, toutes-les-regions. JSON-LD invalide : /collections/gap. Fiches churn : 0 offre dans le JSON-LD (E17 conforme). hreflang /en/ : aucun (V7 conforme). Robots IA : tous autorisés (E6 conforme).
- Core Web Vitals non mesurés : quota PageSpeed sans clé épuisé.
- Indexation réconciliée : référence = audit T1 (97,4 % des fiches actives) ; le bilan à 91,9 % (périmètre partiel) est remplacé.

---

## Audit Semrush Site Audit du 05/11/2026 (snapshot 6ae7f846ed026a1b91c89985, crawl du 02/11, 4 372 pages)

- Score : 46 erreurs, 10 871 avertissements, 10 541 notices. Erreurs = 4xx (10), titres dupliqués (16), contenu dupliqué (2), liens internes cassés (9), meta descriptions dupliquées (9).
- Détail des URL par erreur, statuts Shopify, IDs et comptes : `claude/audits/semrush-2026-11-05/preuves.json`.
- **Corrigé (autonome)** : 4xx + liens internes cassés, soit 19 des 46 erreurs. 10 redirections 301 Shopify (`claude/audits/semrush-2026-11-05/redirections.tsv`, IDs UrlRedirect 1010552111440 à 1010552406352).
  - 8 fiches en DRAFT → collection géographique. Cible choisie là où les tags produit et le texte des articles concordent, sinon la région.
  - Article Alsace non publié → /collections/alsace. Lien Rochelle « cœur » → handle réel « coeur ».
  - Réversible : une redirection Shopify ne s'applique qu'en 404 ; si une fiche repasse ACTIVE, son URL et les liens des articles refonctionnent sans intervention. Retour arrière : supprimer les 10 IDs.
  - Vérif live le 05/11 : 10/10 en 301 directe vers une cible en 200 sans chaîne (`verif_live.txt`).
- **Non corrigé, décision Florian** :
  - Doublons produits actifs : la-suite-etoilee / -2, le-boudoir-de-nana / -1, carte-cadeau-lovenspa / carte-cadeaux-love-room. Il faut choisir laquelle garder (l'autre passe en draft + 301).
  - Doublons collections : cote-d-or (38 produits) / cote-dor (18), val-d-oise (5) / val-doise (6). updatedAt observés entre 02:02 et 02:08 UTC (04-05/11) sur les 4 : source de mise à jour à identifier avant toute fusion.
  - Page vs article sur le même sujet : week-end-amoureux-bretagne, creer-sa-love-room, sauna-recap / sauna-guide. La règle « pas de fusion » du 02/11 s'applique-t-elle ?
  - Meta descriptions dupliquées : paris-jadore (2), lessentiel (2), jardin-deden / clair-de-lune hors du temps. Modification on-page à passer en lot A avec témoin.
  - Pages internes publiques et indexables : brandbook, charte-graphique, guidelines-images, guidelines-instagram. Elles contiennent 6 liens relatifs `Lovenspa_*.html` en 404. Je propose de les dépublier.
  - « Bloqués » : toutes-les-regions, tous-les-departements (noindex), déjà en attente.

### Suite du 05/11 : points 2 à 5 (go de Florian)

- **5. Dépublication** (Matrixify, job 778069876 : 4 mises à jour, 0 échec) de brandbook, charte-graphique, guidelines-images et guidelines-instagram. Vérifié en live : 4 en 404. Retour arrière : Published=TRUE (IDs dans `preuves.json`).
- **4. Meta descriptions différenciées** (Matrixify, job 778096614 : 6 mises à jour, 0 échec) sur paris-jadore ×2, lessentiel ×2, jardin-deden et clair-de-lune. Avant : chaque paire servait la meta d'une seule des deux fiches. Après : meta unique, tirée du texte de la fiche (`metas_lot.csv`, avant : `metas_avant.tsv`). Vérifié en live : 6/6 (`verif_metas_live.txt`). Lot on-page sans témoin, sur ordre explicite. Lecture GSC à J+21 (26/11), page par page.
- **2. Navigation des collections en double** (`menus_collections_doublons.txt`, `liens_entrants_collections_doublons.tsv`) :
  - menus : cote-dor et cote-d-or sont toutes deux dans « Tous les départements » ; val-doise y figure 2 fois ; val-d-oise n'est dans aucun menu ;
  - header et footer : aucune des 4 ;
  - corps des pages (blocs département ou proximité, aucune source trouvée dans nos scripts) : cote-d-or reçoit des liens de 25 pages, cote-dor de 31, val-d-oise de 12, val-doise de 19. Scan de 2 873 URL : 2 855 lues, 18 restées en 429.
- **3. Audit des paires** (`audit_doublons_gsc.json`, GSC du 04/07/2025 au 02/11/2026, inspection d'URL, similarité de texte Jaccard sur 5 mots) :
  - les 10 URL sont toutes indexées, avec un canonical Google égal à l'URL ;
  - cote-d-or : 75 clics / 3 488 impressions ; cote-dor : 159 / 4 181. Les deux se positionnent sur « love room cote d'or » (10,9 contre 6,9). Similarité 0,09, 38 produits contre 18. **Vraie cannibalisation.**
  - val-d-oise : 155 / 5 478, position 14,9 ; val-doise : 144 / 5 634, position 21,9. Les deux se positionnent sur « love room 95 ». Similarité 0,07. **Vraie cannibalisation.**
  - Bretagne : la page fait 146 / 26 719, l'article 0 / 64. L'article n'a aucun lien entrant et date de son dernier crawl le 05/09. Similarité 0,002. Seul le titre est en double.
  - Créer sa love room : l'article fait 63 / 3 455, la page 5 / 94. La page a 2 liens entrants et 2 H1. Similarité 0,033.
  - Sauna : le guide fait 60 / 12 885, sauna-recap 2 / 355, alors qu'il est lié dans le footer des 2 854 pages scannées. Similarité 0,045, même titre et même H1.

## Règles du journal

- Décision stratégique (Go, objectif, budget, périmètre, retour arrière sur page clé) : message privé Slack à Florian dès qu'elle apparaît.
- Fichiers du thème : Shopify CLI (Theme Access, variables SHOPIFY_FLAG_STORE / SHOPIFY_CLI_THEME_TOKEN). Toute publication passe par `claude/agent-seo/theme_publish.sh`, jamais par un `theme push` brut. Le script :
  - fait un pull du live juste avant le push ;
  - compare au md5 de base du patch ; si le live a changé ailleurs, il ne pousse rien (code 3), copie la version live à côté, et il faut fusionner puis recommencer ;
  - pousse ;
  - refait un pull et vérifie le md5.
  Le fichier d'origine est sauvegardé et les md5 avant/après sont notés ici.

- Avant toute modification de niveau A : inscrire le lot ici, figer la liste témoin, sauvegarder les anciennes valeurs.
- Lecture à J+21 minimum, page par page et requête par requête, médiane ou paires, jamais position moyenne agrégée.
- Retour arrière automatique si le lot fait moins bien que son témoin.
- Seule une lecture contre témoin a le droit de dire « ça marche ».
