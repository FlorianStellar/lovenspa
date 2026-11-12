# Journal Instagram @lovenspa.fr

Une ligne par publication produite (date, handle, format, accroche, formule de hook, statut du contrôle), puis les bilans d'audit datés.

## 11/11/2026 : état de départ (page publique, sans métriques)
- 7 950 abonnés, 4 624 abonnements, 221 publications.
- 12 dernières publications (30/09 au 08/11), contrôle maison v0.2 lancé sans fiche logement (le critère LOGEMENT ne peut donc pas y être mesuré) :
  bloquées hors critère LOGEMENT 11/12 ; accroche coupée 7/12 ; appel à l'action absent 10/12 (un seul : 2/12) ;
  tics maison 12/12 ; répétition (au moins 2 tics partagés avec la majorité des légendes suivantes) 11/12 ; conclusion « Parce que… » 8/12.
- Logement nommé : 0/12, relevé à la lecture des 12 légendes (aucun nom d'établissement, ville ou prix cité). Reels : 2/12.
- Source : data/baseline-public-2026-11-11.json. Métriques à venir via l'API (connexion permanente).

## 11/11/2026 : premier audit API (instantané complet, 219 publications)
Source : data/snapshot-2026-11-11.json ; audits data/audit-2026-11-11*.md.
- La métrique « vues » n'existe que pour les posts publiés à partir du 20/01/2025 (avant, l'API renvoie 0 avec une portée > 0) : analyse sur 20/01/2025 → 09/11/2026, 168 posts, vues 168/168.
- Médiane du compte : 1 513 vues.
- Jeux concours (43 posts, tous en carrousel sauf 1) : médiane 8 004 vues, multiple 5,29, partages/portée 2,13 %, abonnements/portée 0,98 %.
  Hors concours (125) : médiane 1 307 vues, multiple 0,86, partages/portée 0,00 %, abonnements/portée 0,00 %. 86/125 sans aucun partage, 67/125 sans enregistrement.
  Les partages des concours sont en partie imposés par la mécanique (identifier, partager) : comparables entre concours, pas avec le reste.
- Dernier concours le 18/06/2026. Médiane des posts hors concours : 1 420 vues (T3 2026), 1 118 (T4 2026, au 09/11).
- Reels hors concours (18) : médiane 1 290 vues, multiple 0,85, temps de visionnage moyen médian 3,8 s.
- Cadence 12/10 → 08/11 : 0,5 Reel, 0,5 carrousel et 1 image par semaine (cible 3 Reels).
- Portée du compte sur 30 jours : 1 777 comptes non abonnés, 1 277 abonnés.

## 11/11/2026 : stratégie (changement d'approche demandé par Florian)
Stratégie déduite de la marque et du benchmark, non des posts passés : doc « Stratégie Instagram Love'nSpa 2026-2027 » (https://claude.ai/artifact/2kWuAKDD13LwfSTDqDUY5v), en attente de validation.
- Benchmark Business Discovery : data/benchmark-2026-11-11.md (37 comptes, 50 derniers posts, likes + commentaires).
- Abonnés (API) : 35-44 ans 36,7 %, 25-34 ans 27,9 %, 45-54 ans 20,6 % ; femmes 55,1 % ; France 89,8 %, Ukraine 3,5 %, Belgique 2,2 %.
- Commandes Shopify par mois : pic en décembre (136 en 2024, 174 en 2025), creux en août (23, 46).
- Heures de connexion des abonnés : non fournies par l'API pour ce compte.

## 2026-11-12 — J3 bibliothèque S2 Instagram v1
- Échantillon : benchmark-2026-11-12.json, 37 comptes lus (3 illisibles), 50 publications max par compte, hygiène S2-M03 (fenêtre 7–180 j, ≥10 publications, épinglées retirées, concours et partenariats écrits à part).
- 76 signaux à 3x ou plus de la médiane du compte et du format, classés par agent (signaux_classes.json) ; 10 hors organique : 5 par le filtre de légende, 5 partenariats repérés au contrôle qualité (`partenariat_releve`).
- Fiches : 18 (B : F01, F03, F06, F07 ; C : 14 ; A : 0). F05 redescend en C (2 comptes organiques). Accroches réelles FR : 40. Règles : 34 (30 officielles, 2 secondaires, 2 non trouvées) dans regles.md.
- Écarts majeurs relevés (décisions à prendre) : zone de texte des Reels, permissions du jeton, format JPEG 4:5 des carrousels par l'API, is_ai_generated.
- Relecture humaine : en attente (Florian).

## 2026-11-12 — Décisions de Florian sur les écarts J3 (regles.md)
1. Zone texte des Reels : y=270–1248, marges 65 px (visuels.py).
2. Permissions Meta (content_publish, manage_comments, manage_messages) : à ajouter maintenant.
3. Carrousels : JPEG 1080x1350 (4:5), 10 diapositives max (choix éditorial).
4. Label IA : visuel photoréaliste généré ou modifié par IA seulement (`ia_photorealiste` -> is_ai_generated).
5. Concours : 3 mentions IG-R28 bloquantes en S6.
6. Mot-clé -> message privé unique avec lien, sous 7 j, sans relance, à partir de J7 (C-04).
