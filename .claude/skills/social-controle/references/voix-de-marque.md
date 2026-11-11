# Voix de marque : méthode de contrôle du ton

Méthode tirée des skills brand-voice (Tribe AI), brand-review (knowledge-work-plugins) et brand-voice-guidelines, brand-dna (claude-marketing), modifiée et traduite en français par Stellar Projects, 2026. Provenance : `../SOURCES.md`.

La méthode est la même pour toutes les marques. Les valeurs viennent de `social/marques/<id>/marque.json`. Aucune valeur de marque n’est écrite ici, sauf les exemples marqués « exemple ».

## 1. Paramètres lus dans `marque.json`

| Champ | Existe aujourd’hui | Usage |
| --- | --- | --- |
| `langue` | oui | Langue du contrôle. |
| `ton.registre` | oui (`vouvoiement` ou `tutoiement`) | Contrôle du registre (section 4, étape 1). |
| `ton.style` | oui, texte libre | Lu comme résumé de la voix. Sans fiche voix détaillée, c’est le seul repère d’attributs. |
| `ton.skills` | oui | Skills d’écriture de la marque (S5) : non utilisées par le contrôle. |
| `ton.voix` | non, champ cible (à outiller) | Fiche « Nous sommes / Nous ne sommes pas » (section 2). |
| `ton.profil` | non, champ cible (à outiller) | Six axes de 1 à 10 et 3 à 5 adjectifs (section 3). |
| `ton.matrice` | non, champ cible (à outiller) | Matrice de ton par contexte (section 5) ; à défaut, la matrice par défaut ci-dessous s’applique. |

Un champ absent n’est jamais deviné : il est `null`, et le contrôle qu’il porterait est signalé « non spécifié » dans le rapport (S6-16, S6-19).

## 2. Fiche voix « Nous sommes / Nous ne sommes pas » (S6-13)

Pour chaque attribut de voix :

| Champ | Contenu |
| --- | --- |
| `nous_sommes` | L’attribut, en un ou deux mots. |
| `nous_ne_sommes_pas` | Sa dérive à éviter. |
| `veut_dire` | Ce que l’attribut veut dire dans un texte. |
| `ne_veut_pas_dire` | Ce qu’il ne veut pas dire. |
| `sonne_juste` | Une phrase réelle de la marque qui l’incarne. |
| `sonne_faux` | Une phrase qui le trahit. |

Exemple (Love’nSpa, tiré du brief ; phrases à écrire par la marque) :

| Nous sommes | Nous ne sommes pas |
| --- | --- |
| Romantiques | mièvres |
| Sensuels | explicites, jamais |
| Attentionnés, au vouvoiement | familiers |

Une fiche est utile si deux relecteurs, avec elle, rendent le même verdict sur le même texte.

## 3. Profil de voix sur six axes (S6-16)

Six axes notés de 1 à 10 : formel / familier ; rationnel / émotionnel ; joueur / sérieux ; affirmé / nuancé ; classique / innovant ; expert / accessible. Plus 3 à 5 adjectifs. Champ inconnu = `null`.

Confiance par section (S6-17) :

| Niveau | Condition |
| --- | --- |
| Haute | 3 sources concordantes ou plus (charte, publications, échanges clients). |
| Moyenne | 1 à 2 sources, ou déduction. |
| Basse | Source unique, ou sources en conflit. |

Une section de confiance basse ouvre une question ouverte, consignée au journal avec une recommandation. La recommandation s’applique par défaut ; la marque peut la corriger a posteriori. Rien ne bloque.

## 4. Contrôle d’un texte, étape par étape

1. **Registre.** Si `ton.registre` vaut `vouvoiement` : toute forme de « tu » adressée au lecteur (tu, te, t’, toi, ton, ta, tes, impératifs en -e de 2e personne comme « réserve ta ») est un constat de gravité haute. L’inverse pour `tutoiement`. Les appels à l’action de `regles.json` contiennent les deux formes : seule celle du registre est acceptée.
2. **Voix constante, ton variable (S6-12).** La voix (les attributs) ne change jamais. Le ton se règle sur trois curseurs : formalité, énergie, technicité. Une demande « plus détendu » déplace le ton, jamais la voix.
3. **Attributs.** Pour chaque attribut de `ton.voix` : le texte tombe-t-il du côté « nous sommes » ou « nous ne sommes pas » ? Citer le passage. Sans `ton.voix`, juger contre `ton.style` et marquer le constat « confiance basse ».
4. **Ton selon le contexte (section 5).** Comparer le ton du texte à la ligne de la matrice qui correspond (légende, réponse de soutien, réclamation, crise).
5. **Familiarité.** Ne jamais ajouter de tournure orale (« t’as », « y’a ») pour gagner des points au contrôle VOIX de `detecter.py` (C-09).
6. **Rapport (S6-10, S6-11).** Tableau ci-dessous ; chaque constat cite sa règle (clé de `regles.json`, champ de `marque.json` ou ID de compilation). Un constat sans règle est un goût, pas un contrôle : il est retiré.

| Problème | Emplacement | Gravité | Règle | Correction |
| --- | --- | --- | --- | --- |

Gravité :

| Gravité | Définition | Équivalent système |
| --- | --- | --- |
| Haute | Contredit la voix, ou risque de conformité. | Bloquant (`REFUSE`). |
| Moyenne | Incohérent, sans dommage. | Avertissement (`A_REVOIR`). |
| Basse | Préférence. | Note, sans effet sur le statut. |

Donner un avant / après pour les 3 à 5 problèmes les plus graves. Verdict global : Conforme (`OK`), À reprendre (`A_REVOIR`), Refusé (`REFUSE`).

## 5. Matrice de ton par contexte (S6-14, valeurs par défaut)

| Contexte | Formalité | Énergie | Technicité | Humour | Empathie |
| --- | --- | --- | --- | --- | --- |
| Réseaux sociaux (légendes, réponses de soutien) | basse à moyenne | haute | basse | selon la marque | selon la marque |
| Support client, réclamation | moyenne | non spécifié | non spécifié | nul | très haute |
| Crise | haute | non spécifié | non spécifié | nul | très haute |

Le registre de la marque (`ton.registre`) s’applique dans tous les contextes, même quand la formalité est basse.

## 6. Audit de cohérence mensuel (S6-15)

1. Échantillon : 3 contenus par canal (légendes, réponses S9 quand elles existent).
2. Note de 1 à 5 par attribut de voix.
3. Écarts repérés et classés selon la gravité de la section 4.
4. Recherche des mots interdits (`tics_maison`, `ouvertures_interdites`, `conclusions_interdites`, lexique).
5. Test : lu à voix haute, est-ce une seule personne qui parle ?
6. Résultat au journal de la marque. La dérive lente se voit ici, pas légende par légende.

## 7. Confidentialité (S6-18)

Dans les rapports et les exemples : initiale du prénom seulement, jamais de pseudo complet ni de coordonnées d’un client.

## Non repris

Exemples avant / après à chiffres inventés, règles de style anglaises, archétypes illustrés par des marques réelles, recherche de documents de marque dans des outils tiers, extraction de couleurs et polices d’un site (compilation, section 5).
