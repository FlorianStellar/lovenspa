# Journal des déploiements SEO — lovenspa.fr

Convention : une entrée par lot, newest first.
Colonnes : date déploiement · lot · levier · URLs modifiées · témoin · date lecture · verdict

---

## Lots actifs

| # | Déployé | Lot | Levier | N URLs | Témoin | Lecture prévue | Verdict |
|---|---|---|---|---|---|---|---|
| L8 | 10/11/2026 | 10 pages à CTR anormal (8 articles, 2 pages) | SEO title + meta description (`global.title_tag` / `description_tag`). Écriture v1 à 08:19 UTC. v2 à 10:17 UTC après QA : 9 titles raccourcis (suffixe thème compris, ≤ 60 car.), promesse « définition » retirée de love hôtel. | 10 | 5 articles figés (`claude/lots/L8.md`) | J+21 compté à partir du 11/11 → lecture le 05/12/2026 | en cours. Fellation (521 mots) et levrette (407 mots) sont des contenus minces : réserve pour la lecture. |
| L6 | 02/11/2026 | 25 fiches 404 (churn) | Status DRAFT/ARCHIVED/UNLISTED→ACTIVE + templateSuffix=produit-churn (corrigé le jour même : premier passage en `churn`, suffixe inexistant dans le thème lovenspa 4.1, fiches servies quelques heures sur le template produit standard) | 25 | Sans témoin : action de récupération 404→200, suivi non causal (impressions et clics des 25 URL à J+21 vs 90 j avant) | 23/11/2026 | en cours. Rendu non vérifié : lovenspa.fr bloqué par le réseau de l'environnement. |
| L5 | 13/10/2026 | collection `/collections/love-room` | Réécriture éditoriale (9 H2, FAQPage 7Q, 47 liens, chiffres oct.) | 1 | `/pages/guide-qu-est-ce-love-room` | 27/10/2026 · **24/11/2026** | ⚠ Lu à J+27 le 09/11, non conclusif. Sur 21 j avant / 21 j après : lot clics ×2,40, position de 11,8 à 9,0 ; témoin clics ×3,00, position de 8,2 à 10,2. Témoin d'une seule page, faible volume. Contaminé par 3 événements (02/11 et 03/11 ×2). Décision Go en attente. |
| L4 | 28/09/2026 | 35 metas fiches | SEO title + meta description | 35 | 35 témoins figés | 02/11/2026 | ⚠ Verdict du 02/11 retiré le 09/11 : il reposait sur une médiane agrégée, sans paires. Non lisible tant que les listes du lot et du témoin ne sont pas retrouvées. |
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

## Veille indexation du 06/11/2026

- 608 URL, 0 erreur (`veille.py`) : 83 fiches actives modifiées depuis 48 h, les 20 fiches suivies et les 506 collections. Aucun écart de canonical. Fichier : `claude/veille/veille-2026-11-06.csv`.
- Fiches suivies : aucun changement depuis le 05/11. 13 en 404 pour Google, 5 inconnues, 1 noindex, 1 redirection.
- Nouvelle anomalie : `le-1888-maison-romantique-avec-balneo-en-sologne` est « URL is unknown to Google ». La fiche a été créée le 04/11 et publiée le 05/11 à 18:49 UTC ; elle répond 200. Je l'ajoute au suivi.
- Collections : les mêmes 4 anomalies, toujours en attente de décision.

## Veille indexation du 07/11/2026

- 600 URL inspectées, 0 erreur : 75 fiches modifiées depuis 48 h, 21 fiches suivies, collections. Aucune nouvelle anomalie, aucun écart de canonical. Fichier : `claude/veille/veille-2026-11-07.csv`.
- Fiches suivies (21) : 2 sont maintenant indexées (1 qui était en 404, 1 qui était inconnue) et 1 est passée de « inconnue » à « découverte ». Il en reste 19 non indexées : 12 en 404, 4 inconnues, 1 découverte, 1 noindex, 1 redirection.
- Collections : les 4 mêmes anomalies que les jours précédents.

## Veille indexation du 08/11/2026

- 573 URL inspectées, 0 erreur : 49 fiches modifiées depuis 48 h, 19 fiches suivies et les collections. Aucune nouvelle anomalie, aucun écart de canonical. Fichier : `claude/veille/veille-2026-11-08.csv`.
- Fiches suivies : 3 de plus sont indexées (une « inconnue », une « découverte », la fiche en redirection). Il reste 16 fiches non indexées : 12 en 404 depuis le premier relevé, 3 inconnues, 1 noindex.
- Collections : les 4 mêmes anomalies que lors des veilles précédentes.

## Veille indexation du 09/11/2026

- 559 URL inspectées, 0 erreur : 37 fiches modifiées depuis 48 h, 16 fiches suivies, collections. Aucune nouvelle anomalie, aucun écart de canonical. Fichier : `claude/veille/veille-2026-11-09.csv`.
- Fiches suivies : 1 fiche de plus indexée (elle était en 404). Il en reste 15 non indexées : 11 en 404, 3 inconnues, 1 noindex.
- Collections : les 4 mêmes anomalies.

## Cycle hebdo du 09/11/2026

- Compte rendu ajouté au doc et corrigé après QA. Données : `claude/veille/hebdo-2026-11-09.json`.
- KPI 28 j : 128 287 clics (+5,4 %), 3 025 639 impressions (+4,1 %). « love room » au niveau requête : 4 051 clics, position 4,7.
- Erreur corrigée : une somme faite au niveau requête × page comptait deux fois les impressions de « love room ». Les chiffres sont maintenant pris au niveau requête.
- Lectures : L5 non conclusif ; verdict de L4 retiré ; L1, L2, L3 non lisibles.
- Lot proposé : L8, 10 URL, témoin figé de 5 URL après retrait de la page Halloween le 10/11 (`claude/lots/L8.md`). L7 reporté, faute de la liste L6.
- Règle : toute liste de lot et de témoin est enregistrée dans `claude/lots/` avant déploiement.
- Go en attente : univers cible (option A ou B) et décision sur L5.

## Veille indexation du 10/11/2026

- 584 URL, 0 erreur : 63 fiches modifiées depuis 48 h, 15 fiches suivies, les collections. Aucune nouvelle anomalie, aucun écart de canonical. Fichier : `claude/veille/veille-2026-11-10.csv`.
- Fiches suivies : aucun changement. Toujours 15 fiches non indexées : 11 en 404, 3 inconnues de Google, 1 en noindex.
- Collections : les 4 mêmes anomalies.

## 10/11/2026 : bascule des tâches sur zen-edison (go de Florian)

- peaceful-cannon fusionnée dans `claude/zen-edison-sac366` (merge 4b19e5c). Les 5 tâches récurrentes de la session SEO du 03/11 (veille, hebdo, exécution, mensuelle, trimestrielle) pointent maintenant sur zen-edison.
- Le cycle du lundi utilise l'export plat maison (`site_export.py` et `site_audit.py`), qui remplace Matrixify.

## Décisions de Florian du 10/11/2026

- Univers cible : option A, soit tout le site hors marque et hors /en/, haut de tunnel compris. Nouvelle action G2 : stratégie de conversion du trafic blog vers la réservation.
- L5 : réécriture gardée. Relecture au 30/11 contre un témoin élargi à plusieurs collections ville.
- Fiches en 404 et fiches non listées indexées : en attente.
- `tous-les-departements` et `toutes-les-regions` : noindex voulu (contenu mince). Clos.
- E1 BigQuery et E7 Bing Webmaster Tools : go.
  - Côté agent, l'usage du compte de service GSC pour lire et configurer le projet GCP a été refusé par la politique de sécurité de la session.
  - Configuration à faire par Florian dans les consoles (étapes envoyées dans la conversation).

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

## Export plat du site, 10/11/2026 (remplace Matrixify)

- Outils : `claude/agent-seo/site_export.py` (bulk operations de l'API Admin Shopify, lecture seule) et `site_audit.py` (audit hors ligne en 0,4 s). 21 tests.
- Export : 3 524 objets (1 801 produits, 508 collections, 777 pages, 438 articles), 16 763 liens (16 215 éditoriaux, 548 de menus), 44 445 appartenances produit-collection, 8 413 redirections, 20 menus. Données : `claude/exports/site-2026-11-10/`.
- Publiés : 1 237 fiches, 505 collections, 764 pages, 367 articles.
- Liens à corriger : 205 liens vers 43 cibles. 183 passent par une redirection (dont 55 vers `/collections/love-room-sauna-privatif` et 43 vers un article du magazine renommé), 17 pointent vers une page non publiée et 5 vers une URL introuvable.
- Sans aucun lien entrant (éditorial, menu ou grille) : 29 collections, 20 pages et 175 articles. Pour les articles, les listes du blog générées par le thème ne sont pas comptées.
- Constat : les 7 fiches supprimées vues en 404 le 05/11 redirigent maintenant en 301 (redirections ajoutées entre-temps).
- Matrixify : licence en plan Demo (10 objets par export) ; rien n'est acheté.

## Crawl de validation du 10/11/2026

- 2 876 URL : 2 840 en 200, 36 en 429. Sources des liens cassés relevées (`claude/audits/tech-2026-11-10/liens_casses.csv`) : 31 cibles en 301 ou 404.
- Priorité : 2 liens de menu présents sur les 2 839 pages crawlées mènent à des redirections (`/pages/loveroom-recap` et `/pages/love-room-le-guide-des-hebergements-reserves-aux-couples`, toutes deux vers `/pages/loveroom`). Traitement : agent du mercredi (menus ajoutés au niveau Auto).
- Concordance avec l'export plat : les cibles du crawl se retrouvent dans `liens_a_corriger.csv` ; l'export donne en plus la source exacte (menu ou body).

## Bugs techniques, passage du 11/11/2026 (agent du mercredi) : inscription avant modification

- Export du 11/11 + audit comparé au 10/11 : 205 liens à corriger vers 43 cibles (inchangé). Diff : 10 titles du lot L8, 2 nouveaux articles, 2 fiches modifiées hors agent (la-suite-isahora, mas-alegria-loverom-spa : description).
- Périmètre du passage (plafond 30 objets) : 2 menus + 28 pages publiées, 47 liens qui passent par une redirection. Outil : `claude/agent-seo/fix_links.py` (6 tests). Sauvegardes : `claude/audits/tech-2026-11-11/avant/`.
- Correspondances vérifiées en direct (chaîne suivie, 200 à l'arrivée) :
  - /blogs/articles/le-fauteuil-tantra-un-guide-complet → /blogs/magazine/le-fauteuil-tantra-un-guide-complet
  - /blogs/magazine/love-room-alsace-spa-privatif-route-des-vins-et-marches-de-noel-feeriques → /collections/alsace
  - /blogs/magazine/raviver-la-flamme-du-couple-guide-complet → /blogs/magazine/comment-raviver-la-flamme-apres-des-annees-de-relation
  - /collections/jacuzzi-privatif → /collections/chambre-jacuzzi-spa-privatif
  - /collections/love-room-bordeaux → /collections/bordeaux
  - /collections/love-room-lyon → /collections/lyon
  - /collections/love-room-normandie → /collections/normandie
  - /collections/love-room-paris → /collections/paris
  - /collections/love-room-sauna-privatif → /collections/sauna-privatif
  - /collections/love-room-sofa-tantrique → /collections/sofa-tantrique
  - /collections/secret-room-love-room-week-end-amoureux → /collections/secret-room
  - /collections/spa-privatif → /collections/chambre-jacuzzi-spa-privatif
  - /collections/toutes-les-love-rooms → /collections/love-room
  - /pages/chambre-jacuzzi-privatif-offrir-hors-saison  → /pages/chambre-jacuzzi-privatif-offrir-hors-saison
  - /pages/chambre-jacuzzi-privatif-preservez-intimite-chambre-! → /pages/chambre-jacuzzi-privatif-preservez-intimite-chambre
  - /pages/chambre-jacuzzi-privatif-services-exclusifs-suites-luxe  → /pages/chambre-jacuzzi-privatif-services-exclusifs-suites-luxe
  - /pages/erreurs-eviter-choix-chambre-spa-privatif-lune-miel. → /pages/erreurs-eviter-choix-chambre-spa-privatif-lune-miel
  - /pages/guide-la-love-room-secret-room  → /pages/guide-la-love-room-secret-room
  - /pages/guide-love-room-rochelle-cœur-vieille-ville → /pages/guide-love-room-rochelle-coeur-vieille-ville
  - /pages/guide-quel-type-love-room-choisir  → /pages/guide-quel-type-love-room-choisir
  - /pages/guide-une-love-room-paris-ville-amour  → /pages/guide-une-love-room-paris-ville-amour
- Pages traitées :
  - /pages/guide-a-occasions-organiser-week-end-amoureux (4)
  - /pages/loveroom (4)
  - /blogs/magazine/love-room-strasbourg-suites-avec-spa-privatif-de-la-petite-france-a-la-route-des-vins (2)
  - /blogs/magazine/love-room-toulouse-les-meilleures-suites-romantiques-avec-jacuzzi-privatif (2)
  - /pages/chambre-avec-jacuzzi-privatif-recap (2)
  - /pages/guide-atouts-love-room-escapade-couple (2)
  - /pages/guide-impact-love-rooms-relations-intimes (2)
  - /pages/guide-la-love-room-jacuzzi-privatif (2)
  - /pages/guide-la-love-room-piscine-privative (2)
  - /pages/guide-la-love-room-sauna (2)
  - /pages/guide-la-love-room-spa-privatif (2)
  - /pages/guide-love-room-valencienne-ses-tresors-caches (2)
  - /pages/guide-love-rooms-tendance-marche-hotelier (2)
  - /pages/kit-sextoy-lelo-couple (2)
  - /pages/sofa-tantra-recap (2)
  - /blogs/magazine/10-idees-de-week-end-en-amoureux-en-auvergne-rhone-alpes (1)
  - /blogs/magazine/10-idees-de-week-end-en-amoureux-en-occitanie (1)
  - /blogs/magazine/10-idees-de-week-end-en-amoureux-en-pays-de-la-loire (1)
  - /blogs/magazine/5-langages-de-l-amour-test-interpretations (1)
  - /blogs/magazine/baby-clash-couple-proteger-lien-apres-bebe (1)
  - /blogs/magazine/casser-la-routine-du-couple-12-rituels (1)
  - /blogs/magazine/charge-mentale-du-couple-apres-bebe-la-partager-pour-se-retrouver (1)
  - /blogs/magazine/comment-raviver-la-flamme-durablement (1)
  - /blogs/magazine/dead-bedroom-comment-sortir-du-desert-sexuel-dans-le-couple (1)
  - /blogs/magazine/demande-en-mariage-a-la-maison-15-scenarios-cosy (1)
  - /blogs/magazine/demande-en-mariage-facon-disney-10-idees-sans-le-parc (1)
  - /blogs/magazine/demande-en-mariage-originale-50-idees-par-contexte (1)
  - /blogs/magazine/demande-en-mariage-surprise-sans-stress-8-scenarios (1)
- Menus : `cocons` (2 éléments) et `guides` (1 élément) vers `/pages/loveroom` (200 vérifié).
- Exclus, à arbitrer : 7 liens vers des fiches supprimées redirigées vers une collection régionale (ancre au nom de l'hébergement), 1 lien vers l'abonnement redirigé vers l'accueil (page je-souhaite-quitter-lovenspa). `/collections/luxe` : « introuvable » dans l'export mais 200 en direct, faux positif à expliquer.

## Bugs techniques, passage du 11/11/2026 : résultat

- Menus : `cocons` (« Guide des love rooms », Page/118577529168 non publiée → Page/152267325776 `/pages/loveroom` ; « Guide du week-end en amoureux » → `/pages/loveroom`) et `guides` (« Guide de la Love Room » → `/pages/loveroom`). Titres, ordre et nombre d'éléments inchangés. Supprime les 2 liens redirigés présents sur toutes les pages.
- 28 pages et articles, 47 liens remplacés par leur URL finale (8 au premier lancement, interrompu par une erreur de type sur articleUpdate, puis 39 à la relance idempotente). Vérifié par l'API et en direct sur 3 pages (0 lien redirigé).
- QA indépendant : conforme (diff limité aux href, 21 URL finales en 200, plafond 30/30, aucune action Go). Remarque : le libellé « Guide du week-end en amoureux » du menu cocons pointe vers le guide des love rooms (cible de la 301 existante) ; libellé à revoir (Go, contenu).
- Reste : 110 liens redirigés dans 110 pages publiées (passages suivants), 8 liens exclus à arbitrer (Go), faux positif `/collections/luxe` : la boutique sert une collection « Love Room de Luxe » (id 654218821968, HTTP 200, canonical propre), mais l'API Admin ne connaît ni cet id ni le handle `luxe`. Cause non établie (suppression récente avec cache, ou ressource hors API) ; à revérifier au prochain passage, aucune action.

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

## 05/11/2026 · Widget V2 · case de consentement marketing (emailing)
- Fichier : assets/loven-booking.js (thème live #188545007952). Base md5 a201a30d3cc4de78aed70d21dca4ff82, sauvegarde claude/theme/backup/loven-booking.js.2026-11-05.orig.
- Patch : claude/theme/pret-a-pousser/assets/loven-booking.js (case de refus non cochée à l'étape contact ; corps booking-create : consent_text_version v1-2026-11-05 + marketing_opt_out au lieu de marketing_consent:false codé en dur).
- Tests : syntaxe node OK ; E2E Playwright (claude/theme/tests/e2e_consentement_v2.js, bubble-pink, booking-create intercepté) : case vide → opt_out false ; case cochée → opt_out true.
- Push live : refusé par la politique de sécurité de la session, en attente (go de Florian donné dans le chat).

## Veille indexation du 11/11/2026
- Univers : 588 URL (82 fiches modifiées ≤ 48 h + 15 suivies + collections du sitemap), 588 inspectées, 0 erreur.
- Aucune nouvelle anomalie, aucun écart de canonical. 4 anomalies connues ; suivi inchangé : 11 en 404, 3 inconnues de Google, 1 en noindex (en standby, décision du 10/11).
- L8 v2 vérifié en ligne : 10/10 conformes (title + suffixe ≤ 60, meta identique à celle de L8_valeurs.json). J0 du lot = 10/11.

## E1 — Export GSC → BigQuery : configuration Cloud (11/11/2026)
- Projet « lovenspa » inaccessible depuis florian@lovenspa.fr (créé sous un autre compte Google, facturation 018C76… fermée) : abandonné pour E1.
- Projet retenu : deep-rainfall-514310-j9 (« My First Project », org lovenspa.fr 864340713183), facturation 012B6C-716B93-6C13A4 active (billingEnabled: true).
- API BigQuery activée. Exception projet à la contrainte iam.allowedPolicyMemberDomains (allowAll, ce projet seulement ; le reste de l'org reste restreint). florian@lovenspa.fr : orgpolicy.policyAdmin au niveau org.
- Rôles : search-console-data-export@system → bigquery.jobUser + dataEditor ; lovenspa-seo-agent → bigquery.dataViewer + jobUser (4/4 après ~propagation).
- Export GSC configuré par Florian le 11/11 (searchconsole, UE). Contrôle des tables programmé le 13/11 à 10:13 UTC (trig_01KZg7muD4wVDzuuReULoH3b).
