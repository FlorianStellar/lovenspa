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

- 02/11/2026 16:02 UTC : collection `love-room` modifiée hors agent (titre actuel « Love Rooms en France : toutes nos adresses vérifiées »). Touche l'URL du lot L5 : lecture du 24/11 à interpréter avec cette réserve.
- Semaine du 28/09/2026 : langue `en` retirée de la boutique (seule `fr` publiée). Segment `/en/` : 47 526 impressions en S39, 785 en S44. Robots.txt vérifié : ne bloque pas `/en/`.

## Décisions de Florian

- 02/11/2026 : retrait de la langue anglaise volontaire.
- 02/11/2026 : pas de fusion des articles cannibalisés (massage tantrique, kamasutra, sofa tantra) ; traitement par maillage interne (action C2, niveau A).
- 02/11/2026 : V1 accès écriture GitHub donné ; V4 go noindex `/en/pages/guide-qu-est-ce-love-room` ; V5 go lien churn vers `/collections/love-room`.

## Constats agent du 02/11/2026

- V4 sans objet : `/en/pages/guide-qu-est-ce-love-room` répond 301 vers `/pages/guide-qu-est-ce-love-room` (200). Une 301 ne peut pas porter de noindex et consolide déjà vers la page FR. Échantillon `/en/` : `/en/` 301 vers `/`, fiches et pages 301 vers FR, `/en/collections/love-room` 404, `/en/blogs/news` 301 vers `/en/blogs/sexo` (chaîne à vérifier).
- V5 : écriture API sur le thème MAIN bloquée par Shopify. Code prêt : `claude/theme/V5-loven-churn-lien-love-room.md`, collage manuel par Florian.
- Haloscan : API joignable avec la clé de l'environnement (crédits au 02/11 : 9 819 mots-clés, 2 448 site).

## CSS / fichiers thème en attente de push par Florian

- CSS de lecture + repositionnement mobile bloc éditorial (écrit en local, branche `claude/zen-edison-sac366`)
- V5 : `sections/loven-churn.liquid`, lien « love room » vers `/collections/love-room` (voir `claude/theme/`)

---

## Règles du journal

- Avant toute modification de niveau A : inscrire le lot ici, figer la liste témoin, sauvegarder les anciennes valeurs.
- Lecture à J+21 minimum, page par page et requête par requête, médiane ou paires, jamais position moyenne agrégée.
- Retour arrière automatique si le lot fait moins bien que son témoin.
- Seule une lecture contre témoin a le droit de dire « ça marche ».
