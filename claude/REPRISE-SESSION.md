# Reprise de session — agent SEO Love'nSpa (état au 03/11/2026, fin de session 2)

Doc de pilotage : https://claude.ai/artifact/1RAXLmVgLKQ8XsBwhvY3C4 · Journal : `claude/journal-deploiements-seo.md` · Outils : `claude/agent-seo/`

## À faire en ouverture de session
0. `pip install -q -r claude/agent-seo/requirements.txt` (sinon gsc_client.py échoue : google.oauth2 absent des conteneurs neufs).
1. Vérifier les plugins actifs (ListPlugins) ; si SearchFit SEO est présent, confronter le plan et les écarts E1-E16 du doc à ses skills (seo-audit, technical-seo, ai-visibility, internal-linking, keyword-clustering, schema-markup, content-strategy). N'ajouter au doc que le nouveau ou le contradictoire ; relecture par un agent QA.
2. Vérifier `SHOPIFY_FLAG_STORE` et `SHOPIFY_CLI_THEME_TOKEN` (sans les afficher) ; si présents : `npx @shopify/cli theme pull` du thème MAIN, puis pousser V5 (`claude/theme/V5-loven-churn-lien-love-room.md`) après sauvegarde et md5 au journal.
3. Chercher le canal Slack `#lovenspa-seo` ; si présent, y poster les décisions en attente (validation des écarts E1-E16, go BigQuery, accès Bing Webmaster Tools).
4. Après validation de Florian : créer les tâches planifiées du doc (section « Rituels et tâches planifiées »), heure de Paris.

## Décisions déjà prises
- Cible « love room » = `/collections/love-room`.
- Anglais retiré volontairement ; `/en/` répond en 301 vers FR (V4 sans objet).
- Pas de fusion des articles cannibalisés (maillage C2).
- V1 accès Git OK ; V5 go (lien churn vers love-room).

## Fait le 03/11 (session 2)
- SearchFit SEO : confrontation des 7 skills au plan, puis passage du QA. Ajouté au doc (rev 31) : E17, E18, E21 et les précisions sur E6, E8, V6 et V7. T5 et T6 sont débloqués.
- Shopify CLI OK. V5 : pull du thème MAIN (md5 inchangé), patch, tests et sauvegarde dans `claude/theme/`. **Push live refusé par la politique de sécurité de la session** : il attend l'autorisation explicite de Florian.
- Slack #lovenspa-seo (C0CEDJXLQPL) : décisions en attente postées.
- Étape 4 : go de Florian (« tourner en autonomie »). 6 tâches planifiées créées dans cette session, heure de Paris :
  - veille indexation, chaque jour à 06:23 ;
  - cycle hebdomadaire, le lundi à 07:47 ;
  - exécution des lots de niveau A, le mardi à 09:17 ;
  - revue mensuelle, le 1er du mois à 09:37 ;
  - revue trimestrielle, le premier lundi du trimestre à 10:17 ;
  - fin de l'audit d'indexation, une seule fois, le 03/11 à 11:47.
- Push V5 : refusé une seconde fois après le go d'autonomie. Pour le débloquer, il faut une règle de permission (Bash `npx @shopify/cli@latest theme push`) ou un collage manuel.

# Emailing voyageurs LSPA (05/11/2026)
Doc : https://claude.ai/artifact/LJJy1JXosZoQqYMEWvgALw · Outils : `claude/agent-emailing/` (clé `KLAVIYO_TOKEN`, compte YdW2ER) · niveau d'autonomie N1 depuis le 05/11 (envois autonomes sous garde-fous ; suppressions sur go de Florian).
- Segments : ULt6nv (1 clients), YgFB45 (2 engagés), WpCtcc (3 tièdes), TTygHG (4 à réactiver), X8Wwag (5 à supprimer). Hébergeurs exclus à l'envoi (EXCL_SEGMENTS_AT_SEND).
- Flows en brouillon : voir `flows_ids.json`. Campagnes : `campaigns_ids.json`. Métriques : S8ypgR, U6Q3wu, XFFNxs (contrat dans `event_schema.py`).
- Décision de Florian (05/11) : les 2 896 réservants abonnés sont gardés en consentement (marketing_basis=soft_optin, consent_source=reprise_historique). Groupe témoin : 308 sur 3 113 (temoin.py).
- Tâches planifiées : cycle hebdo le mardi à 10:13 (trig_01Ru4tHdid4cnAnZMfwvuNLM), revue mensuelle le 1er à 11:23 (trig_01A8Xp1aiqQhMwZzWkyD8Eko).
- Missions 1 à 3 en cours dans Lovable (message umsg_01m6ng1f4pfh5a7120wakfjfba + 2 compléments).
- 05/11 : 7 flows actifs. Programmé : réactivation e1 le 06/11 à 10:00 (throttle 10 %/h), Noël le 15/11 à 09:00, réactivation e2 le 20/11 à 10:00. Garde-fou le 06/11 à 13:00 (trig_01VcpPV1RuXqpqVQR3REeCuu).
- 06/11 : garde-fou déclenché sur la réactivation e1 (désinscriptions 0,58 % > 0,3 % ; 3 892 destinataires, 0 plainte) → envoi annulé. Go de Florian : relance « vague 1 bis » le 07/11 à 10:00 (hors segment TYhhWc des déjà servis), seuils réactivation (désinscriptions 1,5 %, plaintes 0,1 %, rebonds 5 %), e2 reportée au 21/11. Garde-fou le 07/11 à 13:00. NB : l'API Klaviyo exprime son heure courante en heure de New York.
- 07/11 : vague 1 bis terminée (9 081 destinataires, 3 plaintes, 0,36 % de désinscriptions). Total email 1 : 12 980 destinataires, 267 cliqueurs. E2 programmée le 21/11.

## Mise à jour 11/11/2026
- Branche de travail : claude/zen-edison-sac366 (peaceful-cannon fusionnée ; toutes les tâches planifiées y pointent). Toujours `git pull --rebase` avant push : d'autres sessions y poussent.
- E1 : export GSC → BigQuery configuré sur le projet deep-rainfall-514310-j9 (dataset searchconsole, UE). Contrôle des tables le 13/11 10:13 UTC.
- E7 : Bing opérationnel (claude/agent-seo/bing.py, clé BING_API_KEY), intégré au cycle hebdo du lundi.
- Prochaines échéances : 16/11 cycle hebdo (1er Bing, cadrage G2 conversion blog → réservation) ; 23/11 lecture L6 ; 30/11 relecture L5 ; 05/12 lecture L8.
- Détails : claude/journal-deploiements-seo.md.
