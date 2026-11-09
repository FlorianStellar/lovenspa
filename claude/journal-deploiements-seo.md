# Journal des déploiements SEO — lovenspa.fr

Convention : une entrée par lot, newest first.
Colonnes : date déploiement · lot · levier · URLs modifiées · témoin · date lecture · verdict

---

## Lots actifs

| # | Déployé | Lot | Levier | N URLs | Témoin | Lecture prévue | Verdict |
|---|---|---|---|---|---|---|---|
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
- Lot proposé : L8, 10 URL, témoin figé de 6 URL (`claude/lots/L8.md`). L7 reporté, faute de la liste L6.
- Règle : toute liste de lot et de témoin est enregistrée dans `claude/lots/` avant déploiement.
- Go en attente : univers cible (option A ou B) et décision sur L5.

## CSS / fichiers thème en attente de push par Florian

- CSS de lecture + repositionnement mobile bloc éditorial (écrit en local, branche `claude/zen-edison-sac366`)
- ~~V5~~ publié le 03/11

---

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
