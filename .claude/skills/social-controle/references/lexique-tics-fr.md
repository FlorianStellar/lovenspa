# Lexique FR des tics d’écriture IA (S6-01, S6-02)

Lexique compilé le 11/11/2026 : 203 entrées (149 reprises de `lexique.json`, origine « L » ; 44 adaptées de `slop.json`, origine « S » ; 10 reprises de `copy-machine`, origine « C »). Provenance et licences : `../SOURCES.md`.

Mode d’emploi :

- Chaque occurrence produit un avertissement `TICS_IA` (code cible, à outiller dans `controle.py`). Jamais bloquant seul.
- Le remplacement est une proposition. Le modèle réécrit la phrase et vérifie les accords. Aucun remplacement automatique (`humaniser.py` est écarté).
- « (suppr.) » = supprimer l’expression et reformuler la phrase.
- « (à relire) » = remplacement discutable : garder la détection, ne jamais appliquer le remplacement sans relecture.
- Recherche insensible à la casse et aux apostrophes (’ et ’ équivalents), en mot entier.
- Les formes au « tu » restent détectées (C-08) ; la production suit le registre de `marques/<id>/marque.json` (`ton.registre`).
- Le lexique est à la marque (S6-24) : le retrait d’un mot que la marque emploie vraiment est proposé par écrit à S1 (skill `social-strategie`), propriétaire de `marques/<id>/regles.json`, avec date et raison ; il s’applique après validation humaine (C-18).
- Doublons avec les règles maison : « essentiel » reste traité par `tics_maison` (seuil de répétition) ; seule l’expression « il est essentiel de » est gardée ici (C-11). « Imaginez » est traité par `ouvertures_interdites` et n’est compté qu’une fois (C-10).

## A.1 Entrées reprises de lexique.json (« L »), 149 entrées

### Verbes (30)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 1 | plonger dans | regarder | L |
| 2 | plongeons dans | regardons | L |
| 3 | plongeons | regardons | L |
| 4 | plongez dans | regardez | L |
| 5 | explorons | voyons | L |
| 6 | décryptons | voyons | L |
| 7 | booster | augmenter | L |
| 8 | boostez | augmentez | L |
| 9 | booste | augmente | L |
| 10 | boostent | augmentent | L |
| 11 | optimiser | améliorer | L |
| 12 | optimisez | améliorez | L |
| 13 | optimise | améliore | L |
| 14 | maximiser | augmenter | L |
| 15 | maximisez | augmentez | L |
| 16 | mettre en lumière | montrer | L |
| 17 | met en lumière | montre | L |
| 18 | mettent en lumière | montrent | L |
| 19 | témoigne de | montre | L |
| 20 | témoignent de | montrent | L |
| 21 | s’avère | est | L |
| 22 | s’avèrent | sont | L |
| 23 | favoriser | aider | L |
| 24 | favorise | aide | L |
| 25 | naviguer dans | s’y retrouver dans | L |
| 26 | capitaliser sur | miser sur | L |
| 27 | impacter | toucher | L |
| 28 | impacte | touche | L |
| 29 | impactent | touchent | L |
| 30 | prioriser | passer d’abord (à relire) | L |

### Adjectifs (25)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 31 | véritable | (suppr.) | L |
| 32 | véritables | (suppr.) | L |
| 33 | incontournable | à connaître (à relire) | L |
| 34 | incontournables | à connaître (à relire) | L |
| 35 | crucial | important | L |
| 36 | cruciale | importante | L |
| 37 | cruciaux | importants | L |
| 38 | cruciales | importantes | L |
| 39 | révolutionnaire | nouveau | L |
| 40 | révolutionnaires | nouveaux | L |
| 41 | innovant | nouveau | L |
| 42 | innovante | nouvelle | L |
| 43 | innovants | nouveaux | L |
| 44 | innovantes | nouvelles | L |
| 45 | holistique | global | L |
| 46 | primordial | important | L |
| 47 | primordiale | importante | L |
| 48 | fascinant | intéressant | L |
| 49 | fascinante | intéressante | L |
| 50 | inégalé | rare (à relire) | L |
| 51 | inégalée | rare (à relire) | L |
| 52 | optimal | bon | L |
| 53 | optimale | bonne | L |
| 54 | percutant | fort | L |
| 55 | percutante | forte | L |

### Noms (13)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 56 | game changer | gros changement | L |
| 57 | game-changer | gros changement | L |
| 58 | synergie | collaboration | L |
| 59 | synergies | collaborations | L |
| 60 | écosystème | milieu | L |
| 61 | paradigme | modèle | L |
| 62 | levier | moyen | L |
| 63 | leviers | moyens | L |
| 64 | valeur ajoutée | intérêt | L |
| 65 | hack | astuce | L |
| 66 | hacks | astuces | L |
| 67 | pépite | bonne idée | L |
| 68 | pépites | bonnes idées | L |

### Connecteurs (17)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 69 | incontestablement | (suppr.) | L |
| 70 | indéniablement | (suppr.) | L |
| 71 | assurément | (suppr.) | L |
| 72 | véritablement | vraiment | L |
| 73 | considérablement | beaucoup | L |
| 74 | significativement | nettement | L |
| 75 | en effet | (suppr.) (à relire) | L |
| 76 | par ailleurs | aussi | L |
| 77 | en outre | et | L |
| 78 | de surcroît | et | L |
| 79 | néanmoins | mais | L |
| 80 | toutefois | mais | L |
| 81 | afin de | pour | L |
| 82 | afin d’ | pour | L |
| 83 | en somme | bref | L |
| 84 | en définitive | (suppr.), jamais « au final » (C-12) | L |
| 85 | ainsi donc | donc | L |

### Ouvertures (28)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 86 | dans un monde en constante évolution | aujourd’hui | L |
| 87 | dans un monde en perpétuelle évolution | aujourd’hui | L |
| 88 | dans un monde qui va de plus en plus vite | aujourd’hui | L |
| 89 | à l’ère du numérique | aujourd’hui | L |
| 90 | à l’heure du numérique | aujourd’hui | L |
| 91 | dans le paysage actuel | aujourd’hui | L |
| 92 | dans le contexte actuel | aujourd’hui | L |
| 93 | dans le monde d’aujourd’hui | aujourd’hui | L |
| 94 | plus que jamais | (suppr.) | L |
| 95 | il est important de noter que | (suppr.) | L |
| 96 | il est important de souligner que | (suppr.) | L |
| 97 | il convient de noter que | (suppr.) | L |
| 98 | il convient de souligner que | (suppr.) | L |
| 99 | force est de constater que | (suppr.) | L |
| 100 | nul doute que | (suppr.) | L |
| 101 | il va sans dire que | (suppr.) | L |
| 102 | il est essentiel de | il faut | L |
| 103 | il est crucial de | il faut | L |
| 104 | il est primordial de | il faut | L |
| 105 | que ce soit pour | pour | L |
| 106 | un véritable atout | un plus | L |
| 107 | un élément clé | un point important | L |
| 108 | une étape clé | une étape importante | L |
| 109 | un enjeu majeur | un vrai sujet | L |
| 110 | jouer un rôle clé | compter | L |
| 111 | joue un rôle clé | compte | L |
| 112 | joue un rôle crucial | compte | L |
| 113 | solution clé en main | solution prête | L |

### Conclusions (12)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 114 | en conclusion | (suppr.) | L |
| 115 | pour conclure | (suppr.) | L |
| 116 | pour résumer | (suppr.) | L |
| 117 | en résumé | (suppr.) | L |
| 118 | n’hésitez pas à | (suppr.) | L |
| 119 | n’hésite pas à | (suppr.) | L |
| 120 | n’hésitez pas | (suppr.) | L |
| 121 | n’hésite pas | (suppr.) | L |
| 122 | le ciel est la limite | (suppr.) | L |
| 123 | à vous de jouer | (suppr.) | L |
| 124 | à toi de jouer | (suppr.) | L |
| 125 | et vous, qu’en pensez-vous | (suppr.) | L |

### Réseaux (24)

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 126 | arrête de scroller | (suppr.) | L |
| 127 | arrêtez de scroller | (suppr.) | L |
| 128 | ne scrolle pas | (suppr.) | L |
| 129 | ne scrollez pas | (suppr.) | L |
| 130 | dans cette vidéo | (suppr.) | L |
| 131 | dans la vidéo d’aujourd’hui | (suppr.) | L |
| 132 | dans ce reel | (suppr.) | L |
| 133 | dans ce tiktok | (suppr.) | L |
| 134 | abonne-toi pour plus de contenu | (suppr.) | L |
| 135 | abonnez-vous pour plus de contenu | (suppr.) | L |
| 136 | abonne-toi pour plus | (suppr.) | L |
| 137 | abonnez-vous pour plus | (suppr.) | L |
| 138 | like et abonne-toi | (suppr.) | L |
| 139 | likez et abonnez-vous | (suppr.) | L |
| 140 | l’algorithme adore | (suppr.) | L |
| 141 | l’algo adore | (suppr.) | L |
| 142 | cours, ne marche pas | (suppr.) | L |
| 143 | courez, ne marchez pas | (suppr.) | L |
| 144 | contenu de valeur | contenu utile | L |
| 145 | apporter de la valeur | aider | L |
| 146 | petite astuce | astuce | L |
| 147 | sans plus attendre | (suppr.) | L |
| 148 | on se retrouve dans une prochaine vidéo | (suppr.) | L |
| 149 | c’est parti | (suppr.) | L |

## A.2 Entrées adaptées de slop.json (« S »), 44 entrées

Entre crochets : l’entrée anglaise d’origine. Traduction de ce projet.

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 150 | sans accroc, en toute fluidité | simplement | S [seamless, seamlessly] |
| 151 | robuste | solide | S [robust] |
| 152 | à la pointe | récent, ou dire le fait | S [cutting-edge] |
| 153 | méticuleusement, avec un soin méticuleux | avec soin | S [meticulous, meticulously] |
| 154 | une myriade de | beaucoup de | S [myriad of, myriad] |
| 155 | une pléthore de | beaucoup de | S [plethora of, plethora] |
| 156 | une mine d’or | beaucoup | S [treasure trove] |
| 157 | une tapisserie de | un mélange de | S [tapestry] |
| 158 | l’univers de | le monde de | S [realm] |
| 159 | la pierre angulaire | la base | S [cornerstone] |
| 160 | sublimer | mettre en valeur | S [elevate] |
| 161 | débloquer | obtenir | S [unlock] |
| 162 | triés sur le volet, sélectionnés avec soin | choisis | S [curate, curated] |
| 163 | à couper le souffle | dire le détail précis (la vue, le bain) | S [breathtaking] |
| 164 | époustouflant | dire le détail précis | S [stunning] |
| 165 | captivant | intéressant | S [captivating] |
| 166 | iconique | connu | S [iconic] |
| 167 | le guide ultime | le guide | S [ultimate guide] |
| 168 | passer au niveau supérieur | progresser | S [level up] |
| 169 | sans effort | facilement | S [effortlessly] |
| 170 | en fin de compte | (suppr.) | S [ultimately] |
| 171 | un large éventail de | beaucoup de | S [a wide range of] |
| 172 | quand il s’agit de | pour | S [when it comes to] |
| 173 | en substance | bref | S [in essence] |
| 174 | inestimable | utile | S [invaluable] |
| 175 | remarquable | dire le fait | S [remarkable] |
| 176 | la recette secrète | la méthode | S [secret sauce] |
| 177 | soyons honnêtes | (suppr.) | S [let’s face it] |
| 178 | ce n’est un secret pour personne | (suppr.) | S [it’s no secret that] |
| 179 | on est tous passés par là | (suppr.) | S [we’ve all been there] |
| 180 | relisez bien cette phrase | (suppr.) | S [let that sink in, read that again] |
| 181 | matière à réflexion | (suppr.) | S [food for thought] |
| 182 | au bout du compte | (suppr.) | S [at the end of the day] |
| 183 | nous sommes ravis de vous annoncer, nous avons le plaisir de partager | (suppr.) | S [i am excited to announce, i’m thrilled to share] |
| 184 | attachez vos ceintures | (suppr.) | S [buckle up] |
| 185 | attention spoiler | (suppr.) | S [spoiler alert] |
| 186 | regardez jusqu’à la fin | (suppr.) | S [watch till the end] |
| 187 | vous n’allez pas y croire | (suppr.) | S [you won’t believe] |
| 188 | personne n’en parle | peu de gens le savent | S [nobody is talking about this, no one is talking about this] |
| 189 | ça a tout changé | ça a marché | S [this changed everything] |
| 190 | c’est le signe qu’il vous fallait | (suppr.) | S [this is your sign to] |
| 191 | j’étais loin de me douter | (suppr.) | S [little did i know] |
| 192 | la suite, vous la connaissez | (suppr.) | S [the rest is history] |
| 193 | faites-moi confiance, ne passez pas à côté | (suppr.) | S [trust me on this one, don’t sleep on this] |

## A.3 Entrées reprises de copy-machine (« C »), 10 entrées

Source : `copy-machine:references/compliance-fr.md` (« Tics IA à bannir ») et `copy-machine:scripts/copy_lint.py` (`AI_TICS`). Déjà présentes et non dupliquées : plongez, sublimer, véritable, incontournable, révolutionnaire, en somme, il est important de noter, que vous soyez (motif 17).

| N° | Tic | Remplacement proposé | Origine |
| --- | --- | --- | --- |
| 194 | dans un monde où | (suppr.) | C |
| 195 | découvrez l’univers | (suppr.), dire ce qu’on voit | C |
| 196 | n’attendez plus | (suppr.) | C |
| 197 | plongez au cœur | regardez | C |
| 198 | au cœur de | (à relire : légitime pour un lieu, « au cœur du Luberon ») | C |
| 199 | bien plus qu’un, bien plus qu’une | (suppr.), dire le fait | C |
| 200 | une expérience unique | dire ce qui est unique | C |
| 201 | un voyage | (à relire : légitime au sens propre) | C |
| 202 | élevez, élever votre | (suppr.), dire le fait | C |
| 203 | notamment | (à relire : « notably » a été écarté de slop.json comme mot courant) | C |

## B. Tics de structure à signaler (31 motifs, S6-02, S6-35)

Le code ne réécrit pas ces motifs. Il les signale (`STRUCTURE`, code cible à outiller) ; le modèle réécrit phrase par phrase en gardant le sens.

| N° | Motif | Correction attendue |
| --- | --- | --- |
| 1 | « Ce n’est pas juste X, c’est Y » | Dire la seule chose voulue, supprimer la mise en place. |
| 2 | « Non seulement X mais aussi Y » | Deux phrases, ou garder la moitié la plus forte. |
| 3 | « Il ne s’agit pas de X. Il s’agit de Y. » | Commencer par Y. |
| 4 | Question rhétorique seule sur sa ligne (« Le résultat ? ») | Répondre directement. |
| 5 | « Voici ce que j’ai appris » | Donner la leçon sans l’annoncer. |
| 6 | Triade « X, Y et Z. » | Deux éléments ou quatre. |
| 7 | Emoji 🚀 🔥 💡 ✨ 🎯 | Au plus `max_emojis_legende` de `regles.json` (exemple Love’nSpa : 1), jamais l’un de ceux-là (S6-22). |
| 8 | Mur de hashtags (au-delà de `legende.max_hashtags` de `regles.json`) | Rester sous le plafond, hashtag de marque compris. Seuil aligné sur `max_hashtags` (C-06). |
| 9 | Le modèle parle de lui (« en tant qu’IA ») | Supprimer la phrase. |
| 10 | Ouverture de conclusion (« En résumé ») | Pas de paragraphe de conclusion. |
| 11 | Appât d’engagement réflexe (« D’accord ? ») | Une question que seule la marque peut poser, sur le point précis. |
| 12 | Ouverture « arrêtez de scroller » | L’accroche vient de l’affirmation elle-même. |
| 13 | Préambule vidéo (« dans cette vidéo je vais vous montrer ») | Commencer par le gain. |
| 14 | Liste à puces en emojis | Tiret ou retour à la ligne. |
| 15 | Trois mots ou plus en majuscules d’affilée | Un mot au plus en légende (S6-22). |
| 16 | Appât réflexe d’abonnement ou d’identification | Demander la seule action que ce post mérite. L’appel à l’action exigé par `regles.json` reste obligatoire ; seule la formule générique est refusée (C-05). |
| 17 | « Que vous soyez X ou Y » | Parler à une seule personne. |
| 18 | Ouverture « Imaginez… » | Montrer la scène. Doublon de `ouvertures_interdites` : compter une fois (C-10). |
| 19 | Longueur de phrase uniforme (variation sous 0,35 sur 4 phrases ou plus) | Couper une phrase, en laisser une autre courir. |
| 20 | Puces de longueur uniforme (3 puces ou plus, écart type sous 1,6 mot) | Varier ou passer en phrases. |
| 21 | Liste de négations (« Pas de X, pas de Y, pas de Z ») | Dire ce qui se passe ; une seule absence réelle, dite une fois. |
| 22 | Ajouts qui traînent après la virgule (« …, sans X, sans Y » ; « …, garantissant que… ») | Finir la phrase sur l’affirmation ; un fait nouveau a droit à sa phrase. |
| 23 | Deux-points de révélation (« Le meilleur : … ») | Phrase normale. |
| 24 | Poème d’une phrase par ligne sur tout le texte | Des paragraphes ; couper là où une personne marquerait une pause. |
| 25 | Phrase-sagesse que personne ne contesterait | Le fait précis qu’elle évoque, ou rien. |
| 26 | Chute « citable » en dernière ligne (« Parce que vous le méritez. ») | Finir sur un fait, l’offre ou la demande. |
| 27 | Le texte se commente lui-même (« Voici pourquoi c’est important. ») | Supprimer ; ajouter un détail si le point en a besoin. |
| 28 | Sujet abstrait (« la plateforme permet… ») | Le couple, ou la personne, fait l’action. |
| 29 | Fausse étendue (« de X à Y » sans vraie étendue) | Nommer ce qui est vraiment couvert. |
| 30 | Esquive de « est » et « a » (« se pose comme », « s’impose comme », « dispose de ») | « est », « a », ou le verbe exact. |
| 31 | Cycle de synonymes pour une même chose (« lieu », « adresse », « écrin », « cocon ») | Choisir le mot du client et le répéter. |

## Non repris

- 58 entrées de `slop.json` écartées comme doublons d’un concept déjà présent (liste : compilation, annexe A.3).
- 43 entrées de `slop.json` non reprises : sans tic équivalent en français, ou contraires aux appels à l’action exigés (« save this for later », « tag someone who needs this », « share this with someone who needs it », « drop a comment below » : traités par le motif 16).
