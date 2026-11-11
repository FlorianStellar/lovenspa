# Gabarits de réponse (vouvoiement)

Gabarits rédigés pour le système d’après les règles S9 de la compilation. Production au vouvoiement ; une marque au tutoiement (`ton.registre` de `marques/<id>/marque.json`) les transpose une fois, par écrit. À faire valider une fois par chaque marque.

Règles communes :

- Prénom ou pseudo une fois, en tête, sans point d’exclamation (S9-04). Longueur alignée sur celle du message reçu. TikTok : 150 caractères au plus (P-08, à vérifier dans la documentation officielle).
- Chaque `{{champ}}` vient de l’offre (S3, fiche de la boutique) ou du journal. Champ absent : pas de réponse, transfert G7 (S9-12).
- Le lien de réservation n’est jamais inventé : « lien en bio », ou l’`url` de l’offre.
- Chaque réponse passe le contrôle S6 avant envoi (S6-23), typographie française comprise.
- Varier la première ligne d’une réponse à l’autre ; ne jamais coller deux réponses identiques dans un même fil.
- Exécution : manuel (à outiller, jalon J7). Voir la charte de `../SKILL.md`.

## G1. Question de prix (réponse dans la fiche)

**Décision en attente (C-03).** Tant que la marque n’a pas décidé de citer son prix « à partir de » en public, G1 n’est pas utilisé : toute question de prix part en G7 (comportement par défaut, le plus prudent).

Si la marque décide de citer le prix (décision écrite au journal et dans ses règles) : condition, la question porte sur le prix sans dates précises et `prix_a_partir_de` existe dans l’offre.

> {{prénom}}, {{nom court du logement}} est à partir de {{prix_a_partir_de}} € la nuit. Le tarif exact dépend de vos dates : il s’affiche dès que vous les choisissez sur la page du logement, lien en bio.

Le format du prix suit `contexte_prix_logement` de `regles.json` pour que le contrôle `PRIX` le reconnaisse.

## G2. Question de dates ou de disponibilité

Les disponibilités ne sont pas dans l’offre : ne jamais confirmer une date.

> {{prénom}}, le calendrier de {{nom court du logement}} est à jour sur sa page, lien en bio. Vous y voyez les dates libres et le tarif pour celles-ci.

Demande de confirmation, de montant pour des dates, de remise ou de modification de réservation : G7.

## G3. Commentaire mot-clé

**Décision en attente (C-04).** Tant que la marque n’a pas décidé d’envoyer la chose promise en message privé après un commentaire mot-clé, aucun message privé n’est envoyé : seule la réponse publique ci-dessous s’applique (comportement par défaut, le plus prudent).

Réponse publique (par défaut) :

> {{prénom}}, voici {{la chose promise}} : {{emplacement exact, par exemple « lien en bio, rubrique {{nom de la rubrique}} »}}.

Si la marque décide l’envoi en message privé, et seulement si la légende l’a promis et que l’outil officiel de réponse automatique déclenché par le commentaire est en place (S9-08, P-04) :

Réponse publique :

> {{prénom}}, c’est envoyé dans vos messages.

Message privé (trois lignes, la chose d’abord, question facultative) :

> {{prénom}}, voici {{la chose promise}} : {{lien}}
> {{une ligne d’usage tirée de l’offre}}
> {{une question courte sur le point précis}}

Exemple (Love’nSpa) de ligne d’usage : « Le spa est privatif, il est à vous pour toute la soirée. » Exemple de question : « Plutôt week-end ou soir de semaine ? »

## G4. Critique

Une seule réponse dans le fil (S9-05). Ton : humour nul, empathie très haute (S6-14).

> {{prénom}}, vous avez raison sur {{le point exact, repris avec ses mots}}. {{un fait vérifié de l’offre}}

Exemple (Love’nSpa) de fait vérifié : « Le spa est chauffé toute l’année. » (seulement s’il figure dans l’offre).

Variante réclamation (la critique décrit un séjour vécu) : ne rien discuter en public.

> {{prénom}}, merci de nous l’avoir dit. Notre service client veut reprendre ça avec vous : écrivez-nous en message privé ou à {{contact du service client}}.

Puis transfert au service client avec le lien du commentaire (G7, catégorie RÉCLAMATION).

## G5. Spam, insulte, troll

Aucune réponse publique. Action : masquer, jamais supprimer (S9-06, C-02). Ligne de journal :

> {{date et heure}} · {{plateforme}} · {{pseudo}} · motif : spam | insulte | troll · action : masqué · lien : {{permalien du commentaire}}

## G6. Repartage d’un contenu client

Cas A. La personne a identifié la marque et la marque veut republier son contenu. Réponse sous sa publication, dans sa mention ou en réponse à son message (elle a interagi en premier : pas de premier message non sollicité) :

> {{prénom}}, merci pour ce partage. Pouvons-nous republier votre {{photo ou vidéo}} sur {{compte de la marque}}, avec votre compte en crédit ? Un « oui » écrit en réponse suffit. Sans votre accord, nous ne republions rien.

À réception du « oui » : consigner l’accord (S9-14), puis republier avec « Photo : @{{pseudo}} ». Sans réponse : rien, pas de relance.

Cas B. La personne demande à être republiée :

> {{prénom}}, merci. Nous regardons votre {{photo ou vidéo}} et, si nous la republions, ce sera avec votre compte en crédit. Votre message vaut accord, vous pouvez le retirer à tout moment en nous l’écrivant.

Consigner son message comme accord écrit. La décision de republier suit le contrôle visuel S6 (S6-19, S6-20).

Registre des accords (une ligne par accord) : compte, date, texte exact de l’accord, contenu visé, capture du message, retrait éventuel (date).

## G7. Transfert au service client (argent, réclamation, doute)

> {{prénom}}, pour {{vos dates | votre réservation | ce paiement}}, notre service client vous répond directement : écrivez-nous en message privé ou à {{contact du service client}}.

Ne jamais citer un montant, un remboursement ou un geste commercial. Fiche de transfert : pseudo, plateforme, lien du message, catégorie (ARGENT, RÉCLAMATION, DOUTE), texte reçu.

Variante pour une question de prix tant que C-03 est en attente :

> {{prénom}}, pour le tarif de {{nom court du logement}}, notre service client vous répond directement : écrivez-nous en message privé ou à {{contact du service client}}.

## G8. Message d’un hébergeur

Hébergeur partenaire ou candidat. Aucun engagement (référencement, commission, paiement, avis).

> Bonjour {{prénom}}, merci pour votre message. Les demandes des hébergeurs sont suivies par {{équipe partenaires}} : écrivez à {{contact partenaires}} avec le nom et la ville de votre logement.

Paiement ou litige : G7 vers {{équipe partenaires}}. Commentaire public d’hébergeur mécontent : G4, variante réclamation.

## G9. Soutien

> Merci, {{prénom}}. Au plaisir de vous accueillir.

Ou seulement un j’aime (S9-07). Trois à huit mots au plus.

## Champs à fournir par la marque

`{{contact du service client}}`, `{{équipe partenaires}}`, `{{contact partenaires}}`, `{{compte de la marque}}` : à écrire dans `marques/<id>/` (champ cible, à outiller). Tant qu’un de ces champs manque, il n’est jamais inventé : G4 et G7 gardent seulement « écrivez-nous en message privé » ; G6 et G8 ne partent pas (transfert interne seulement, consigné au journal).
