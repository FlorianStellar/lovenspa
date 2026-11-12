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

## 2026-11-12 — Jeton Meta régénéré
- Utilisateur système, sans expiration. Permissions vérifiées par debug_token : instagram_basic, instagram_manage_insights, instagram_content_publish, instagram_manage_comments, instagram_manage_messages, instagram_manage_contents, pages_show_list, pages_read_engagement, business_management.
- Connexion vérifiée : @lovenspa.fr, 7956 abonnés, 222 publications. Publication toujours fermée (STOP, moteurs_valides vide).

## 2026-11-12 — J4 galerie de rendus (en attente de validation)
- 5 rendus dans production/j4 : 2 Reels lieu (Le Nid de l'Erdre, Romantic Room Alexis), carrousel sélection (6 logements ≤ 150 €), carrousel couple, concours de démonstration. Prix relus le jour même ; tous PRET au contrôle S6.
- Défauts trouvés à la relecture visuelle et corrigés : titres de carrousel blancs sur crème (couleur figée avant chargement du kit) ; phrases des Reels sans lien avec la photo (ajout de `reel_photos`) ; photo de vin en couverture du concours (ajout de `couverture.photo`). Espaces insécables ajoutés automatiquement (typo_fr).
- Photos écartées : sofa tantrique (équipement exclu), vin (loi Evin).
- Anomalie catalogue à corriger (S3) : La Villa Yucatan a pour ville « Paris » alors que la page dit « au cœur de l'Île-de-France », spa accessible de 21 h 30 à 23 h 30 seulement ; l'ancienne légende « en plein Paris » était fausse.
- Galerie : https://claude.ai/artifact/FkGZpdPZXhGHmNyYa4rJgL

## 2026-11-12 — J4 v2 après revue d'un expert social media
- Revue : aucun des 5 rendus v1 publiable (notes 3 à 6/10) ; défauts : Reels muets en diaporama lent sur fond flouté, cartons trop longs, temps fort absent, lien en bio non mesurable, contrôle sans lien texte/photo. Deux affirmations de la revue infirmées : les chiffres d'Alexis et du Nid figurent dans les descriptions Shopify ; le couple « REFUSE » ne l'est que par la règle LOGEMENT, sans objet pour ce moteur.
- Décisions de Florian : musique libre de droits ; page lovenspa.fr/instagram comme lien en bio.
- Réalisé : moteur Reel plein cadre (plans 1,25 s, panoramique dès t=0, musique CC0 intégrée, -13 dB), gabarits refaits, S6 (FAIT_CHIFFRE, REVUE, TEMPS_FORT), revue visuelle obligatoire liée à l'empreinte du contenu, bibliothèque de 15 musiques (6 CC0, 9 CC BY, licences archivées), page Shopify « instagram » créée NON publiée (gid://shopify/Page/162447688016).
- Résultat : 5 rendus PRET ; avertissements restants : montant 150 € (seuil de la sélection, source = stratégie) ; temps fort non évoqué par le mot « offrir » dans le concours.
- À faire par un humain : écouter les musiques (voix non vérifiées) ; corriger la ville de La Villa Yucatan ; deux produits carte cadeau actifs (carte-cadeaux-love-room et carte-cadeau-lovenspa).
- Galerie v2 : https://claude.ai/artifact/FkGZpdPZXhGHmNyYa4rJgL

## 2026-11-12 — J4 v5 : 7 moteurs à 9/10
- Consigne de Florian : ajuster jusqu'à 9/10 par moteur et vérifier qu'aucun moteur ne manque.
- Moteurs manquants par rapport au doc de stratégie validé : stories quotidiennes et post mensuel de recrutement des hébergeurs ; ajoutés (contrats, stratégie, planificateur, rendu, contrôle, publication). Limites API : ni sticker (sondage, lien) ni repartage ; repartage possible seulement avec accord daté de l'auteur.
- 5 passages de l'expert social media : v1 3 à 6/10 ; v2 6 à 8 ; v3 6 à 9 ; v4 8 à 9 ; v5 9/10 sur les 7 moteurs (Reel Nid, Reel Loft Spa, sélection, couple, concours, story, recrutement).
- Corrections système issues des revues : verdict cohérent, audio 48 kHz, contrôle des chiffres à l'écran et en légende contre la description, montants sourcés, temps fort, revue visuelle obligatoire (photos sous droits, textes incrustés, personnes, alcool, doublons de la semaine), logement inédit pour le couple, stories après le post du jour (19:30), graphie des communes.
- Photos écartées : Alexis (soupçon de retouche ou génération, non vérifiable), personne en sous-vêtements (Loft Spa), écran projetant un film d'animation (Suites B Spa), texte d'horaires incrusté (Gîte jacuzzi XXL).
- À faire par un humain : écouter les musiques ; publier un règlement de concours ; mettre en ligne /pages/instagram à J7 ; corriger dans Shopify la ville de La Villa Yucatan et « Saint Etienne » (Loft Spa) ; demander à l'hébergeur d'Alexis si ses photos sont retouchées ou générées.
- Galerie v3 : https://claude.ai/artifact/FkGZpdPZXhGHmNyYa4rJgL

## 2026-11-12 — Retour de Florian sur la galerie v3
- Musiques : écoutées et validées (champ `ecoute_validee` dans licences.json).
- Reel Loft Spa : panoramiques trop rapides. Cause : trajet = toute la largeur de la photo en 1,5 s, donc ~1 400 px/s sur des photos larges. Correction système : vitesse plafonnée à 90 px/s, trajet centré (VITESSE_PAN, visuels.py) ; mesuré sur le rendu : 128 px en 1,4 s. Les deux Reels sont refaits.
