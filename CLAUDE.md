# Règles permanentes — dépôt Love'nSpa

## Contrôle qualité obligatoire (règle de Florian du 11/11/2026, « hyper important »)
Aucune affirmation, aucun chiffre, aucun développement ne part en production ni dans un message à Florian (chat, Slack, doc, journal) sans relecture par un agent QA indépendant.
- Agent QA = un sous-agent (outil Agent) qui n'a pas vu ton raisonnement. Donne-lui le brief d'origine, les fichiers et les données sources, jamais ta conclusion à confirmer.
- Il vérifie : conformité au brief ; chaque chiffre recalculé depuis la source ; chaque affirmation prouvée par un fichier, une requête ou une page en ligne ; tests unitaires et E2E lancés ; bugs et trous de couverture.
- Écart trouvé : corriger, puis refaire passer le QA. Ce qui ne passe pas n'est ni publié ni affirmé ; on écrit « non vérifié » ou « non établi ».
- Dans la réponse finale, dire que le QA a été fait et ce qu'il a corrigé.
- Une écriture en production (Shopify, thème, Klaviyo, Lovable) passe le QA AVANT l'écriture, puis une vérification en ligne APRÈS.

## Autres règles
- Aucune hypothèse dans les données ; analyses sur des jeux de données complets ; un chiffre non relevé reste vide.
- Tests unitaires pour chaque fonction, test d'intégration de bout en bout pour chaque développement.
- Branche de travail : claude/zen-edison-sac366 (`git pull --rebase` avant push). Coordination des agents : claude/COORDINATION-AGENTS.md ; URL gelées : claude/lots/URL-GELEES.md.
- Thème live : uniquement via `bash claude/agent-seo/theme_publish.sh` (pull du live juste avant).
