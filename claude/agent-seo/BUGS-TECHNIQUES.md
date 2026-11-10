# Agent de correction des bugs techniques SEO : règles d'autonomie

Mandat : Florian, le 10/11/2026 (« sois autonome sur la résolution des bugs techniques »).
Détection : `crawl_technique.py` (sitemap complet, sources des liens) + veilles d'indexation du journal.
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
2. `python3 claude/agent-seo/crawl_technique.py claude/audits/tech-AAAA-MM-JJ --workers 3`.
3. Comparer au crawl précédent : nouveaux bugs, bugs résolus, régressions.
4. Pour chaque bug Auto : inscrire au journal avant modification (objet, ancienne valeur sauvegardée dans `claude/audits/tech-AAAA-MM-JJ/avant/`), corriger, revérifier l'URL en direct.
5. Agent QA indépendant : chaque correction respecte ce document, aucune régression.
6. Journal, commit (`git add -f` pour les CSV), push. Section « SEO technique » du doc de pilotage mise à jour.
7. Message privé Slack à Florian (espace Lovenspa, U06HU46DCRK) : corrections faites, bugs Go en attente avec la décision demandée. Rien à signaler : pas de message.
