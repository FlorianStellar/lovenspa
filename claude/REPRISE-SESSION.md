# Reprise de session — agent SEO Love'nSpa (état au 03/11/2026)

Doc de pilotage : https://claude.ai/artifact/1RAXLmVgLKQ8XsBwhvY3C4 · Journal : `claude/journal-deploiements-seo.md` · Outils : `claude/agent-seo/`

## À faire en ouverture de session
1. Vérifier les plugins actifs (ListPlugins) ; si SearchFit SEO est présent, confronter le plan et les écarts E1-E16 du doc à ses skills (seo-audit, technical-seo, ai-visibility, internal-linking, keyword-clustering, schema-markup, content-strategy). N'ajouter au doc que le nouveau ou le contradictoire ; relecture par un agent QA.
2. Vérifier `SHOPIFY_FLAG_STORE` et `SHOPIFY_CLI_THEME_TOKEN` (sans les afficher) ; si présents : `npx @shopify/cli theme pull` du thème MAIN, puis pousser V5 (`claude/theme/V5-loven-churn-lien-love-room.md`) après sauvegarde et md5 au journal.
3. Chercher le canal Slack `#lovenspa-seo` ; si présent, y poster les décisions en attente (validation des écarts E1-E16, go BigQuery, accès Bing Webmaster Tools).
4. Après validation de Florian : créer les tâches planifiées du doc (section « Rituels et tâches planifiées »), heure de Paris.

## Décisions déjà prises
- Cible « love room » = `/collections/love-room`.
- Anglais retiré volontairement ; `/en/` répond en 301 vers FR (V4 sans objet).
- Pas de fusion des articles cannibalisés (maillage C2).
- V1 accès Git OK ; V5 go (lien churn vers love-room).
