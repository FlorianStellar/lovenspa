# Accroches : mode d'emploi

La bibliothèque compte 63 formules d'accroche en français. Elles ne sont pas recopiées ici : le fichier de référence est `social/compilation/accroches-fr.json`. Lis-le au moment de choisir ; ne le réécris pas de mémoire.

## Ce que contient le fichier

Une liste JSON de 63 objets, tous avec les mêmes champs :

| Champ | Contenu | Usage |
|---|---|---|
| `id` | A01 à A63 | Référence à citer dans le plan (S4), le paquet (S5) et le journal. |
| `nom_fr` | Nom court de la formule (« L'aveu chiffré », « La liste avec un favori »…) | Lecture humaine. |
| `gabarit_fr` | Forme à remplir, entre accolades `{…}` | La structure à reprendre. |
| `exemple_fr` | Exemple rédigé pour la première marque cliente, avec `{{ }}` pour les faits | Exemple seulement : à réécrire pour chaque marque. |
| `texte_ecran_fr` | Version texte à l'écran (6 mots environ), ou `null` (A27 à A63) | Premier carton d'une vidéo. `null` = pas de version écran fournie : l'écrire soi-même (6 mots maximum) si la formule sert en vidéo. |
| `usage` | Ce que la formule sert (enregistrements, nouvelles audiences, confiance…) | Choisir selon l'objectif de la fiche de format. |
| `erreur_type` | L'erreur qui fait échouer la formule, ou `null` | Contrôle avant de garder une accroche. |
| `plateformes` | instagram (63), tiktok (55), linkedin (29), x (26), youtube (25) | Ne pas utiliser une formule hors de ses plateformes sans l'écrire au journal. |
| `sources` | `dépôt@commit:chemin#id` | Traçabilité. |
| `preuve` | C pour les 63 | Aucune n'a été testée chez nous. |

Familles d'origine :

- A01 à A26 : les 26 formules communes à `instagram-agent-skill` (`skills/ig-reel/hooks.json`) et à leur traduction `Explo38_reels-tiktok-fr` (`skills/rt-video/hooks.json`), souvent rapprochées des entrées de `rediumvex_viral-hooks-skill`.
- A27 à A60 : formules tirées surtout de `rediumvex_viral-hooks-skill` (`hooks-database.md`, 100 formules en 10 catégories), filtrées (voir « Écartées ») ; A39, A41, A48 et A59 citent aussi `nexscope-ai_ecommerce-skills`, A60 ne cite que lui.
- A61 à A63 : formules relevées dans le benchmark de la première marque (A61 « La légende en suspens », A63 « Commentez pour recevoir le lien »). A02, A23 et A62 citent aussi ce benchmark.

## Comment choisir une accroche

1. Pars de la fiche de format (`formats.md`) et de son objectif : la fiche cite souvent ses formules (F01 -> A61 et A24, F03 -> A11, F06 -> A19, F09 -> A63…).
2. Filtre le fichier par `plateformes` et par `usage` compatible avec l'objectif.
3. (S2-M23) Prépare trois accroches de familles différentes : une qui arrête le défilement (négation, chiffre précis, question), une qui retient au-delà de 3 s (récit, aveu, émotion), une libre. Moins de 12 mots chacune.
4. Écris séparément la phrase dite (environ 2 s) et le texte à l'écran (environ 1 s, 6 mots maximum). Conflit tranché par la compilation : écrire pour 1 à 2 s, mesurer la rétention à 3 s.
5. Remplace chaque `{{ }}` par un fait vérifiable (S3 pour un produit, la marque pour un chiffre maison). Un fait manquant bloque l'accroche : ne l'invente pas, ne l'arrondis pas.
6. Relis `erreur_type` et vérifie que l'accroche ne tombe pas dedans.
7. Passe le filtre de score (ci-dessous), puis laisse S5 noter et S6 contrôler.
8. Note dans le paquet l'`id` de la formule retenue, pour que S8 puisse mesurer par formule.

## Score d'accroche = filtre, pas arbitre (S2-M22)

Un score textuel d'accroche sert à **éliminer** les accroches clairement faibles : ouverture sur une salutation, un préambule, ou rien de concret. Il ne sert **pas à choisir** entre deux bonnes accroches.

Pourquoi, selon la mesure publiée par l'auteur de `instagram-agent-skill` (README, « What I actually measured ») :

- AUC 0,83 pour séparer de vraies accroches d'accroches volontairement mauvaises : le score repère bien le mauvais.
- AUC 0,56 pour séparer les succès des échecs d'un même créateur, 0,50 étant pile ou face : le score ne prédit presque pas le succès.
- Seul le critère de précision (chiffres, y compris dits en toutes lettres) a discriminé.
- Le classifieur de formules ne reconnaissait que 49 % des accroches réelles : une bonne accroche peut n'appartenir à aucune formule.

Conséquences :

- Une accroche sous le seuil est réécrite ou jetée. Au-dessus du seuil, toutes se valent pour le score : départage par l'objectif de la fiche, la variété de la semaine et, plus tard, nos mesures S8 par formule.
- Ne classe jamais des accroches par leur score dans un rapport. Ne présente jamais un score comme une prévision de vues.
- La grille de notation elle-même appartient à S5 (S5-16 : note sur 10, seuil 7, critères précise, tension, spectateur, rapide, vraie). S2 n'en garde que l'usage limité.
- Les scripts de score des sources (`score_hook.py` et équivalents) ne sont pas exécutés ; leur logique est décrite ici.

## Faire évoluer la bibliothèque

- Une formule ne passe en B ou en A que comme un format : B si elle est relevée en tête de publications à plus de 3x chez au moins 3 comptes **et** confirmée en accroche parlée (S2-M06 : une légende n'est pas une accroche parlée, d'où A61 maintenue en C) ; A si nos mesures S8 par formule la confirment.
- La lecture par tiers (S2-M07) peut révéler des formules absentes : les accroches non classées du tiers du haut sont à lire à la main.
- Ajout d'une formule : mêmes champs, `preuve` C, source obligatoire. Modification du fichier `accroches-fr.json` : manuel (à outiller) ; tant que ce n'est pas outillé, noter les ajouts proposés au journal de la marque.

## Écartées (ne pas réintroduire)

Reprises de la compilation, section 4.1 : rediumvex 037, 094, 097 (pathos personnel) ; 058 (ressort anxiogène) ; 078 (dénigrement d'une autorité) ; 087, 089, 090 (allégations de santé) ; exemples des sources sur l'emploi, le coaching et les chiffres sans source (remplacés par des exemples avec `{{ }}`).
