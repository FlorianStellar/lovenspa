# Spécifications par plateforme

**Règles de plateforme : une seule référence.** Zone visible de la légende, plafonds (hashtags, caractères, diapos), formats et durées officiels : `.claude/skills/social-veille/references/regles-plateformes.md` (S2). Cette skill n'en recopie aucune valeur : les sources tierces divergent (par exemple sur la zone visible d'une légende TikTok, compilation, section 5).

Les valeurs relevées dans les sources tierces, toutes **à vérifier dans la documentation officielle**, sont dans `social/compilation/s5-production.md`, section 3. S2 les reporte dans `regles-plateformes.md` après vérification. Tant qu'une valeur n'y figure pas :

- longueur de la ligne 1 : `legende.max_visible` de `marques/<id>/regles.json`, appliquée par le contrôle `ACCROCHE` ;
- nombre de hashtags : `legende.max_hashtags` de `regles.json` ;
- emojis : `max_emojis_legende` de `regles.json` (règle de marque, pas de plateforme) ;
- pour le reste, signaler le manque dans le journal et ne pas estimer.

Pinterest : aucune règle vérifiée. La mention « PI » dans les règles signifie « règle générique applicable », jamais « spécification Pinterest ».

## Valeurs de travail retenues (arbitrages de la compilation)

Ces valeurs sont des choix prudents du système, pas des spécifications. Elles restent valables tant que `regles-plateformes.md` ne les contredit pas. Toute nouvelle valeur passe par S2.

| Sujet | Valeur retenue | Origine |
|---|---|---|
| Format d'un Reel ou d'une vidéo TikTok | 1080x1920 (9:16) | sources IG, RT, MV (compilation, section 3) |
| Export vidéo | 30 i/s, H.264, yuv420p, AAC 48 kHz, `+faststart` ; avec son : -14 LUFS, crête vraie ≤ -1 dBTP | S5-43 |
| Zone de texte d'un Reel ou d'une vidéo TikTok | x=60 à 940, y=230 à 1440 ; aucun texte au-delà de x=850 entre y=900 et y=1440 | intersection la plus prudente des sources (conflit « zone sûre ») ; une bande plus prudente (MS) attend l'arbitrage de S2 |
| Zone de texte d'une story | 1080x1920, texte entre y=250 et y=1600 | S5-31 |
| Post de fil et diapo de carrousel | 1080x1350 ; le carré n'est qu'une déclinaison | conflit « format du post de fil » |
| Diapos par carrousel | 10 au plus | code actuel, en attendant la limite officielle de l'API |
| Taille de texte | 32 px minimum sur diapo ; 34 px en vidéo ; sous-titres 72 px minimum si voix | conflit « taille minimale » |
| Durée de Reel | cible 20 à 30 s, 15 à 45 s, jamais moins de 7 s | S5-19 |
| Piste audio | piste muette tant qu'il n'y a pas de musique sous licence, en 48 kHz ; avec musique, -14 LUFS | conflit « piste audio » |

## Valeurs codées aujourd'hui (faits du code, pas des spécifications)

| Constante | Valeur | Fichier |
|---|---|---|
| `CAROUSEL` | 1080x1350 | `social/s5_production/visuels.py` |
| `REEL` | 1080x1920 | idem |
| `ZONE_SURE_BAS` | 1440 | idem |
| `TAILLE_TEXTE_MIN` | 32 | idem |
| Plan par photo | 2,5 s, 30 i/s, zoom jusqu'à 1,08 | `visuels.render_reel` |
| Encodage | libx264, preset veryfast, crf 20, yuv420p, AAC piste muette 44,1 kHz, `+faststart` | idem |
| `MAX_DIAPOS` | 10 | `social/s5_production/produire.py` |

Le code porte encore les commentaires « à déplacer dans les règles de plateforme de S2 au jalon J3 » : ces dimensions sont propres à Instagram.
