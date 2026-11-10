# Agent de correction des bugs techniques SEO : règles d'autonomie

Mandat : Florian, le 10/11/2026 (« sois autonome sur la résolution des bugs techniques »).
Détection : export plat du site (`site_export.py`, API Admin Shopify, remplace Matrixify) audité hors ligne (`site_audit.py`), crawl `crawl_technique.py` pour ce que génère le thème (1er mercredi du mois), veilles d'indexation du journal.
Branche : `claude/zen-edison-sac366`. Journal : `claude/journal-deploiements-seo.md`, section « Bugs techniques ».

## Corrigé sans demander (Auto), puis rapporté

| Bug | Correction | Garde-fous |
| --- | --- | --- |
| Lien interne vers une 301 (`liens_casses.csv`, statut 301) | Remplacer l'URL par sa cible finale dans le body_html source | La cible finale répond 200 (vérifié) |
| Lien interne vers une 404 | Remplacer par la page 200 la plus proche : fiche churn existante, sinon collection ville, sinon département. Aucune cible sûre : retirer le lien, garder le texte | Cible vérifiée en 200 ; jamais une fiche active d'un autre hébergeur à la place d'une fiche supprimée |
| URL 404 avec impressions GSC (90 j) ou liens internes | Redirection 301 Shopify (urlRedirectCreate) vers la même cible que ci-dessus | Jamais sur une URL qui répond 200 ; jamais de chaîne (la cible n'est pas elle-même redirigée) |
| JSON-LD invalide dans un body_html | Corriger la syntaxe seulement, sans changer le contenu | JSON parseable après correction |
| Bug du thème prouvé (JSON-LD invalide, H1 absent ou double, lien cassé en dur dans un template) | Patch minimal via `bash claude/agent-seo/theme_publish.sh` | Pull du live et md5, sauvegarde dans `claude/theme/backup/`, tests, vérification E2E sur 3 URL, retour à la version sauvegardée si la vérification échoue |

Plafond par passage : 30 objets Shopify modifiés et 3 fichiers de thème. Le surplus attend le passage suivant.

## Jamais sans le go de Florian (Go)

- noindex, robots.txt, blocage des facettes, sortie du sitemap, canonical choisi volontairement.
- Dépublier, supprimer ou changer le statut d'un produit, d'une page, d'un article ou d'une collection.
- Prix, disponibilité, contenu éditorial (titles, metas, textes : ce sont des lots SEO contre témoin).
- Toute correction dont la cause n'est pas prouvée.

## Déroulé de chaque passage

1. `git pull`, `pip install -q -r claude/agent-seo/requirements.txt`.
2. `python3 claude/agent-seo/site_export.py claude/exports/site-AAAA-MM-JJ` (quelques minutes, jeton SHOPIFY_API_TOKEN, lecture seule), puis `python3 claude/agent-seo/site_audit.py claude/exports/site-AAAA-MM-JJ --precedent <export précédent>`. Entrée principale : `audit/liens_a_corriger.csv` (source, cible, verdict, URL finale).
   Premier mercredi du mois : en plus, `python3 claude/agent-seo/crawl_technique.py claude/audits/tech-AAAA-MM-JJ --workers 3` (H1, JSON-LD, canonical, noindex générés par le thème).
3. Comparer au passage précédent (`audit/diff.csv`, `resume.json`) : nouveaux bugs, bugs résolus, régressions, modifications faites hors agent.
   Avant de corriger un lien, vérifier en direct le statut de sa cible : l'export dit ce que Shopify contient, le direct dit ce que le visiteur reçoit.
4. Pour chaque bug Auto : inscrire au journal avant modification (objet, ancienne valeur sauvegardée dans `claude/audits/tech-AAAA-MM-JJ/avant/`), corriger, revérifier l'URL en direct.
5. Agent QA indépendant : chaque correction respecte ce document, aucune régression.
6. Journal, commit (`git add -f` pour les CSV), push. Section « SEO technique » du doc de pilotage mise à jour.
7. Message privé Slack à Florian (espace Lovenspa, U06HU46DCRK) : corrections faites, bugs Go en attente avec la décision demandée. Rien à signaler : pas de message.
