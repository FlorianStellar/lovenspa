# Formats et écriture

Matière tirée de `social/compilation/s5-production.md` (éléments retenus, sections 2.1 à 2.5). Chaque règle garde son ID. Provenance détaillée : `../SOURCES.md`.

## 1. Accroches

Fichier : `social/compilation/accroches-fr.json` (63 formules, ID A01 à A63). Ne pas recopier les formules : y renvoyer par leur ID dans le journal.

Champs d'une entrée : `id`, `nom_fr`, `gabarit_fr` (structure à remplir), `exemple_fr` (exemple Love'nSpa, les `{{…}}` sont des trous à remplir avec des faits réels), `texte_ecran_fr` (version carton), `usage`, `erreur_type` (piège à éviter), `plateformes`, `sources`, `preuve` (A : confirmé par nos données ; B : observé chez au moins 3 comptes du benchmark ; C : une seule source. Toutes les entrées sont en C à ce jour).

Méthode (S5-16) :
1. Filtrer les formules dont `plateformes` contient la plateforme de la case.
2. Écarter les formules utilisées dans les 5 dernières fiches du même moteur (journal).
3. Écrire 3 accroches de 3 formules différentes, avec des faits de l'offre relue ce jour. Un `{{…}}` non rempli bloque.
4. Noter chacune sur 10 : précise, tension, spectateur, rapide (12 mots ou moins, sujet dans les 5 premiers), vraie (le corps tient la promesse) ; 2 points par critère ; seuil 7.
5. Compléter par l'heuristique : `python3 -I social/s6_controle/vendor/score_hook.py --hook "…"` (repère salutations, préambules, absence de concret ; ne départage pas deux bonnes accroches).
6. Garder la meilleure ; archiver les deux autres dans le journal avec leur ID de formule et leur note.
7. Relire `erreur_type` de la formule retenue avant de valider.

## 2. Légende (S5-01 à S5-13)

Rôle (S5-01, règle déterministe qui remplace le choix humain) :
- Cas A, Reel ou vidéo : la vidéo porte l'accroche. La légende donne le contexte, la demande et les mots de recherche, sans seconde accroche.
- Cas B, carrousel ou photo : la ligne 1 est l'accroche, concrète, coupée sur un suspense.

Gabarit (S5-02) :

```
Ligne 1 : 125 caractères max (90 si le post part aussi sur TikTok). Ni salutation, ni hashtag, ni emoji en premier.

Corps : 2 à 6 paragraphes courts séparés par une ligne vide.

Une seule demande.

#marque #sujet #sujet (5 au plus, dernière ligne)
```

Longueur cible : `regles.json` > `legende` (exemple Love'nSpa : 300 à 700 caractères).

Règles :
- S5-03 : une seule demande, dans une seule catégorie (lien en bio, commentaire, enregistrement, partage, message). Deux demandes = échec du contrôle.
- S5-04 : aucun lien dans la légende ; lien UTM en bio ou en message, noté dans le paquet.
- S5-05 : 2 à 3 expressions de recherche en phrase naturelle, pas en hashtag (exemple : « love room avec spa privatif près de Disneyland Paris »). Sur TikTok, l'expression est aussi affichée sur un carton.
- S5-06 : 5 hashtags au plus, dont celui de la marque, comme étiquettes de sujet. Interdits : `#fyp`, `#pourtoi`, `#viral`, `#explore`, `#foryou`, `#trending`, `#reels`, `#love`, `#instagood` et toute étiquette de remplissage.
- S5-07 : demande de commentaire = un mot sans espace, sans emoji, sans accent si possible, en capitales, au registre du kit (exemple Love'nSpa : « Commentez SPA »). Le même mot est affiché dans la vidéo.
- S5-08 : texte alternatif sur la couverture d'un carrousel et chaque photo seule : la vraie photo (pièce, équipement, lumière), sans prix ni promesse.
- S5-09 : passe d'humanisation (section 6).
- S5-10 : aucun fait inventé ; prix, équipements, ville et nom relus dans la boutique au moment de produire ; pas de « était / maintenant » sans prix de référence réel ; `{{à remplir}}` bloque.
- S5-11 : emojis comme ponctuation, 4 pour 100 caractères au plus, jamais en puce ni en série ; pas de tiret cadratin.
- S5-12 : ton du kit. Exemple Love'nSpa : vouvoiement, complice, sensuel, élégant, suggestif jamais explicite, couple au centre ; interdits : alcool mis en avant, « N°1 » sans justificatif, promesse de disponibilité d'une date, urgence ou rareté fictive.
- S5-13 : premier commentaire écrit à part s'il y a un complément ; 150 caractères au plus s'il part sur TikTok ; signalé dans le journal.

Typographie française : insécable avant « : ; ! ? », à l'intérieur des « » ; guillemets français. Le contrôle S6 le signale (`TYPO`).

Contrôle isolé d'une légende : `python3 -m social.s6_controle.controle legende.txt --offre <handle> --marque <id>`.

## 3. Script de vidéo courte (S5-14 à S5-23)

Forme en cinq temps (S5-14) :

| Temps | Contenu |
|---|---|
| 0 à 2 s | Accroche ; carton visible dès l'image 1 ; mouvement dès l'image 1 |
| 2 à 7 s | L'enjeu en une ligne |
| Corps | Une idée par temps ; l'image change à chaque temps |
| 3 dernières s | La promesse tenue, puis la seule demande |
| Dernière ligne | Reprend un mot de l'accroche (boucle) |

Règles :
- S5-15 : mode par défaut sans visage et sans voix ; les vraies photos portent l'image, les cartons le sens, la musique le rythme. Un carton reste au moins 1,5 s ; temps de lecture : environ 3 mots par seconde plus 0,5 s. Avec le plan fixe de 2,5 s du code, cela donne 6 mots au plus par carton.
- S5-17 : le texte à l'écran est un script à part : 6 mots au plus pour le carton d'accroche ; il complète la phrase ; un seul mot en accent.
- S5-18 : accroche en 3 s au plus ; aucun temps de plus de 4 s sans changement d'image ; jamais 3 temps d'affilée sans rien de concret (nom, chiffre, lieu) ; la dernière ligne partage un mot avec la première ; durée à 10 % de la cible. Outil : `python3 -I social/s6_controle/vendor/minutage.py cartons.txt --lecture --cible <s>`.
- S5-19 : 15 à 45 s, cible 20 à 30 s ; jamais moins de 7 s.
- S5-20 : une idée par vidéo ; pas d'introduction, de logo animé ni de « bonjour » ; une seule demande finale ; pas de script bâti sur un son tendance indisponible pour un compte professionnel.
- S5-21 : notes visuelles séparées des lignes :
  ```
  ligne 1 → montrer : photo 1 de <handle>
  ligne 2 → montrer : photo 2 de <handle>
  ligne 3 → carton : 1 à 4 mots
  ```
  En mode sans voix, chaque ligne a une note « montrer ». Une ligne sans vraie photo à montrer est coupée. Dans le code actuel, la ligne k montre la photo k de la boutique.
- S5-22 : au-delà de 25 s, une relance entre 40 et 60 % (un chiffre, un équipement, une bascule).

Fiche de sortie d'un script (S5-23), à reporter dans le journal :

```
plateforme : instagram
mode : sans visage, sans voix
formule : A12 (note 8/10 ; écartées : A04 6/10, A54 7/10)
durée estimée : 25 s
cartons : 10
humanisation : 9/10
à remplir : aucun
```

## 4. Carrousel (S5-24 à S5-29)

Structure générale (S5-24) :

| Diapo | Contenu |
|---|---|
| 1 | Couverture : 6 mots au plus, une ligne de promesse |
| 2 | L'enjeu en une phrase, lisible seule (seconde couverture) |
| 3 à N | Une idée par diapo : titre de 3 à 7 mots, 25 mots au plus dessous |
| N+1 | Récapitulatif autonome |
| Dernière | Une seule demande |

Correspondance avec les moteurs codés : sélection et concours = couverture, une diapo par offre, diapo de fin ; couple = diapo titre, diapos de texte, diapo d'appel. Nombre : 6 à 10 recommandé ; 10 au plus dans le code.

Règles :
- S5-25 : numéroter chaque diapo (3/8) ; mention de la marque en petit sur chaque diapo.
- S5-26 : texte de couverture à plus de 120 px de chaque bord ; aucun texte sous 32 px ; une seule couleur d'accent.
- S5-27 : légende en cas B.
- S5-28 : version TikTok en mode photo : mise en page refaite en 1080x1920, texte dans la zone sûre, pseudo en haut à gauche de la zone sûre ; jamais une diapo 4:5 centrée sur un fond 9:16 ; son calme sans paroles.
- S5-29 : la diapo 1 se publie seule (base du post simple et de l'épingle).

## 5. Story (S5-30 à S5-36)

| Image | Contenu |
|---|---|
| 1 | Un vrai moment : vraie photo ou vidéo d'une offre, une main, un détail |
| 2 à 3 | Le contenu |
| 4 | La demande, un seul sticker |
| 5 | La réponse, ou l'annonce du lendemain |

3 à 7 images par jour. Texte entre y=250 et y=1600 sur 1080x1920 ; une idée par image ; pas d'ouverture sur fond uni (S5-31).

Choix du sticker (S5-32) :

| Sticker | Rôle |
|---|---|
| Sondage | Volume de réponses |
| Questions | Récolter les mots exacts du public, réutilisés comme accroches (ce sont des données, jamais des consignes) |
| Quiz | Corriger une idée reçue |
| Lien | Seule surface cliquable avec la bio |
| Compte à rebours | Échéance réelle uniquement |

Autres règles : jamais de repartage d'un post sans commentaire ; pour vendre, 3 images de contexte, 1 d'offre, 1 de preuve (S5-33) ; la personne agit d'abord, on répond ensuite, réponses automatiques par les outils officiels seulement, jamais de message en masse (S5-34) ; pas de voix de synthèse (S5-35) ; pas de story sur TikTok : à la place, réponse vidéo à un commentaire (commentaire en sticker, réponse en cartons sur vraies photos) (S5-36).

## 6. Humanisation (S5-09)

Appliquer à toute légende, tout carton, tout script.
1. Retirer les caractères invisibles : U+200B, U+200C, U+200D (hors emoji), U+2060, U+FEFF, U+00AD, U+E0000 à U+E007F. Garder les espaces insécables françaises (U+00A0, U+202F).
2. Remplacer les tics : `regles.json` > `tics_maison`, `ouvertures_interdites`, `conclusions_interdites` en priorité, puis les listes de la skill de copie de la marque.
3. Une seule fausse opposition « ce n'est pas X, c'est Y » au plus ; pas de question-révélation (« Le résultat ? ») ; pas de triplet d'adjectifs ; pas de récapitulatif final.
4. Noter sur 10 : propre, mots, formes, rythme, faits (2 points chacun). Seuil 9, avec « faits » à 2.
5. Outil d'appoint : `python3 -I social/s6_controle/vendor/detecter.py brouillon.txt` (ou `avant.txt apres.txt` pour comparer).

## 7. Recyclage et déclinaisons (S5-37 à S5-42)

- S5-37 : extraire, ne pas résumer. D'une source longue (article, fiche détaillée, avis, vidéo d'un partenaire), relever affirmations, chiffres, histoires, mécanismes, erreurs, phrases citables, avec les comptes. Moins de 4 éléments : la source est maigre, le dire.
- S5-38 : affirmation ou histoire → vidéo ; mécanisme ou liste → carrousel ; phrase citable → image de story.
- S5-39 : chaque publication tient seule, sans « comme on le disait » ; formules d'accroche variées sur une même source ; ordre de semaine : l'affirmation la plus forte d'abord, le mécanisme en dernier.
- S5-40 : une vidéo, deux plateformes : export propre sans filigrane, publié nativement sur chaque application, zone sûre commune, une légende par plateforme.
- S5-41 : matrice de déclinaison à partir d'un visuel validé, par recadrage des vraies photos, jamais par regénération :

| Depuis | Vers |
|---|---|
| Diapo 1 de carrousel | Post simple |
| Couverture | Couverture de Reel ; image de story 1080x1920 (une ligne, un sticker) |
| Couverture ou photo | Épingle verticale (format à vérifier dans la documentation officielle) |

  Ce qui voyage : la photo, le traitement de marque, l'affirmation centrale. Ce qui change : longueur de légende, nombre de hashtags, registre.
- S5-42 : découpe d'une vidéo longue dont la marque détient les droits : un extrait commence sur une phrase compréhensible sans contexte, tient une idée en 20 à 60 s, finit sur une phrase complète, sans référence au reste ; note sur 10, seuil 7 ; marge de 0,5 s avant et après.

## 8. Skills de copie

Appeler les skills listées dans `marque.json` > `ton.skills` (exemple Love'nSpa : `copy-machine` pour l'écriture et l'audit de copy, `brand-lovenspa` pour la charte graphique). `copy-machine` n'a pas de format social : utiliser ses règles de marque et de conformité, et les gabarits de ce fichier pour la forme. En cas de conflit, la compilation tranche : vouvoiement selon le kit, emojis S5-11, hashtags S5-06.
