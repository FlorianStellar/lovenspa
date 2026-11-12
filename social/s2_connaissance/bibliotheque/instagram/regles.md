# Règles de plateforme Instagram (jalon J3)

Lu le 2026-11-12. Sources : documentation officielle Meta et Instagram. Données complètes et citations dans `regles.json`.

Statuts : **officiel** (page Meta ou Instagram lue), **secondaire** (source hors documentation officielle, ou règle publicitaire appliquée faute de règle organique), **non trouvé** (aucune page officielle ne donne la valeur).

Les pages help.instagram.com ont été lues via leur miroir officiel facebook.com/help/instagram/<même identifiant>.

## Tableau des règles

| Id | Sujet | Règle | Valeur | Statut | Source |
|---|---|---|---|---|---|
| IG-R01 | Hashtags par publication | 5 hashtags au plus par publication. | 5 | officiel | [help.instagram.com/351460621611097](https://help.instagram.com/351460621611097) |
| IG-R02 | Hashtags par Reel | La limite de 5 vaut aussi pour les Reels (annonce du 18/12/2025). | 5 | secondaire | [Threads @creators](https://www.threads.com/@creators/post/DSalXGPCWM4) |
| IG-R03 | Légende (API) | 2 200 caractères et 20 mentions @ au plus. La doc API indique encore 30 hashtags : appliquer 5. | 2 200 | officiel | [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| IG-R04 | Troncature « … plus » | Aucun seuil officiel pour les légendes organiques. 125 caractères = recommandation publicitaire. | — | non trouvé | [Guide pub Meta](https://www.facebook.com/business/ads-guide/update/video/instagram-feed) |
| IG-R05 | Carrousel (application) | Jusqu'à 20 photos et vidéos. | 20 | officiel | [help.instagram.com/269314186824048](https://help.instagram.com/269314186824048) |
| IG-R06 | Carrousel (API) | 20 éléments au plus ; compte pour une publication. | 20 | officiel | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) |
| IG-R07 | Carrousel : recadrage | API : recadrage sur la 1re image (1:1 par défaut). Application : une orientation pour tous. | 1:1 défaut | officiel | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) |
| IG-R08 | Photos du fil (application) | Ratio 1,91:1 à 3:4 ; en 1080 px de large, hauteur 566 à 1440 px. | 1.91:1 à 3:4 | officiel | [help.instagram.com/1631821640426723](https://help.instagram.com/1631821640426723) |
| IG-R09 | Images (API) | JPEG seulement, 8 Mo max, ratio 4:5 à 1,91:1. Le 3:4 n'est pas accepté par l'API. | JPEG ; 4:5 | officiel | [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| IG-R10 | Reels : durée (application) | Jusqu'à 20 min. Au-delà de 3 min, pas de recommandation aux nouveaux publics. | 20 min / 3 min | officiel | [help.instagram.com/225190788256708](https://help.instagram.com/225190788256708) |
| IG-R11 | Reels : ratio et qualité | Ratio 1,91:1 à 9:16 ; ≥ 30 images/s ; ≥ 720 px. | 9:16 | officiel | [help.instagram.com/1038071743007909](https://help.instagram.com/1038071743007909) |
| IG-R12 | Reels : couverture | 420 x 654 px recommandés (1:1,55). | 420 x 654 | officiel | [help.instagram.com/1038071743007909](https://help.instagram.com/1038071743007909) |
| IG-R13 | Reels (API) | MOV/MP4, HEVC/H264, 23-60 fps, 25 Mb/s, 1920 px de large max, 300 Mo, **3 s à 15 min**, 9:16 recommandé, audio AAC 48 kHz 128 kb/s. | 3 s – 15 min | officiel | [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| IG-R14 | Reels : 1080 x 1920 | Aucune recommandation officielle organique. Pub Reels : 1440 x 2560. | — | non trouvé | [Guide pub Reels](https://www.facebook.com/business/ads-guide/update/image/instagram-reels) |
| IG-R15 | Reels : zone sûre | Pas de zone sûre organique. Pub Reels : laisser ~14 % en haut, 35 % en bas, 6 % sur les côtés. | 14 / 35 / 6 % | secondaire | [Guide pub Reels](https://www.facebook.com/business/ads-guide/update/image/instagram-reels) |
| IG-R16 | Stories (application) | Disparaît après 24 h. Durée max d'une vidéo : non documentée. | 24 h | officiel | [help.instagram.com/1662869217365427](https://help.instagram.com/1662869217365427) |
| IG-R17 | Stories (API) | Publiables (media_type STORIES). Vidéo 3-60 s, 100 Mo ; image JPEG 8 Mo ; 9:16 recommandé. | 3-60 s | officiel | [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| IG-R18 | Quota de publication | 50 publications par 24 h glissantes (le guide cite aussi 100 : retenir 50). | 50 | officiel | [content_publishing_limit](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/content_publishing_limit) |
| IG-R19 | Quota de conteneurs | 400 conteneurs par 24 h glissantes. | 400 | officiel | [IG User Media](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media) |
| IG-R20 | URL publique | Médias hébergés sur un serveur public au moment de la publication. | — | officiel | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) |
| IG-R21 | Permissions de publication | instagram_basic + instagram_content_publish (+ pages_read_engagement) ; ou instagram_business_basic + instagram_business_content_publish. Suppression : instagram_manage_contents. | — | officiel | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) |
| IG-R22 | Statuts de conteneur | EXPIRED, ERROR, FINISHED, IN_PROGRESS, PUBLISHED ; expiration à 24 h. | — | officiel | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) |
| IG-R23 | Limites de l'API | Pas d'identification de produits, pas de filtres ; alt_text pour images seulement. | — | officiel | [Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing/) |
| IG-R24 | Commentaires (API) | Répondre, masquer, supprimer : instagram_basic + instagram_manage_comments (+ pages_read_engagement). | — | officiel | [Comment moderation](https://developers.facebook.com/docs/instagram-platform/comment-moderation) |
| IG-R25 | Réponse privée | Sous 7 jours, **un seul message** ; relance seulement si la personne répond (sous 24 h). | 7 j ; 1 msg | officiel | [Private replies](https://developers.facebook.com/docs/instagram-platform/private-replies) |
| IG-R26 | Fenêtre de messagerie | La personne écrit d'abord ; réponse sous 24 h. Exceptions : 7 j (pub vers Direct, agent humain). Texte ≤ 1000 octets. | 24 h | officiel | [Messaging API](https://developers.facebook.com/docs/instagram-platform/instagram-api-with-instagram-login/messaging-api) |
| IG-R27 | Permissions messagerie | instagram_manage_messages (Facebook Login) ou instagram_business_manage_messages (Instagram Login). | — | officiel | [Comment moderation](https://developers.facebook.com/docs/instagram-platform/comment-moderation) |
| IG-R28 | Concours | Organisateur responsable (règlement, éligibilité). Exonération complète d'Instagram par chaque participant. Mention « non parrainé, approuvé ni administré par Instagram ». Interdit : identification inexacte. | — | officiel | [help.instagram.com/179379842258600](https://help.instagram.com/179379842258600) |
| IG-R29 | Contenu de marque | Uniquement avec l'outil de contenu de marque (label partenariat), partenaire identifié avec son accord. | — | officiel | [help.instagram.com/1695974997209192](https://help.instagram.com/1695974997209192) |
| IG-R30 | Contenu IA | Divulgation obligatoire des vidéos photoréalistes et sons réalistes créés ou modifiés ; sanctions possibles ; label « AI info ». | AI info | officiel | [about.fb.com, 02/2024](https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/) |
| IG-R31 | Contenu IA (API) | is_ai_generated = true à la création du conteneur (depuis le 22/06/2026) ; carrousel : parent seul. | — | officiel | [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog) |
| IG-R32 | Recommandations | Contenu sexuellement explicite ou suggestif (ex. vêtements transparents) : autorisé mais peut ne pas être recommandé. | — | officiel | [help.instagram.com/313829416281232](https://help.instagram.com/313829416281232) |
| IG-R33 | Musique (application) | Bibliothèque sous licence parfois indisponible selon le type de compte ; utiliser la Sound Collection. Reel boosté : pas de musique sous licence, ≤ 90 s, 9:16. | — | officiel | [help.instagram.com/1612770602842742](https://help.instagram.com/1612770602842742) |
| IG-R34 | Musique (API) | Instagram Audio API (Facebook Login) depuis le 01/06/2026 ; étiquetage musical pour son original seulement. | — | officiel | [Changelog](https://developers.facebook.com/docs/instagram-platform/changelog) |

## Écarts avec le système actuel

| Paramètre du système | Valeur actuelle | Règle officielle | Écart | Action proposée |
|---|---|---|---|---|
| `legende.max_hashtags` (marques/lovenspa/regles.json) | 5 | 5 par publication (IG-R01) | Aucun. Confirmé officiellement. | Remplacer la source secondaire par l'URL officielle dans la note. |
| `legende.max_visible` | 125 | Non documenté pour l'organique (IG-R04) | Règle maison, pas une règle Instagram. | Garder comme règle maison ; la mesurer sur le fil (S8). |
| `legende.max_caracteres` | 2 200 | 2 200 (IG-R03) | Aucun. | — |
| `MAX_DIAPOS` (social/s5_production/produire.py) | 10 | 20 (application et API, IG-R05, IG-R06) | Limite maison plus stricte que la plateforme. | Lire 20 depuis cette bibliothèque ; garder 10 comme choix éditorial si voulu. |
| Ratio des visuels de carrousel | non vérifié | API : JPEG, 4:5 à 1,91:1 ; recadrage sur la 1re image (IG-R07, IG-R09) | Un visuel 3:4 serait refusé par l'API. | S5 : exporter en 4:5 max, même ratio pour toutes les diapositives, JPEG ≤ 8 Mo. |
| Reels de 12,5 s | 12,5 s | API : 3 s à 15 min (IG-R13) | Conforme. | — |
| Reels 9:16, 1080 x 1920 | 1080 x 1920 | 9:16 recommandé, ≥ 720 px, ≤ 1920 px de large (IG-R11, IG-R13) | Conforme ; 1080 x 1920 n'est pas une valeur officielle (IG-R14). | — |
| Zone de texte des Reels (`ZONE_SURE_BAS`, social/s5_production/visuels.py) | y = 250 à 1440 | Pas de règle organique ; pub Reels : 14 % haut (y ≈ 269), 35 % bas (y ≈ 1248), 6 % côtés (x ≈ 65 à 1015) (IG-R15, secondaire) | **Écart majeur** : le bas du texte (1440) entre de 192 px dans la zone de légende et de boutons. Le haut (250) dépasse aussi de 19 px. | Passer à y = 270 à 1248 et marges latérales de 65 px. |
| `plafond_publications_jour` (S7) | 2 | 50 par 24 h (IG-R18) | Plafond maison, très en dessous du quota. | Garder ; lire aussi content_publishing_limit. |
| Permissions du jeton | instagram_basic, instagram_manage_insights, pages_show_list, pages_read_engagement, business_management | Publication : instagram_content_publish (IG-R21). Commentaires : instagram_manage_comments (IG-R24). Messages et réponses privées : instagram_manage_messages (IG-R25, IG-R27). Suppression : instagram_manage_contents. | **Écart majeur** : le jeton ne permet ni de publier, ni de répondre ou masquer, ni d'envoyer de message privé. | Demander instagram_content_publish, instagram_manage_comments, instagram_manage_messages (examen d'app Meta si accès avancé). |
| Mécanique « commentez un mot-clé, lien en message privé » | prévue (S9) | Réponse privée : 1 seul message, sous 7 jours ; relance seulement si la personne répond (IG-R25) ; exige instagram_manage_comments + instagram_manage_messages | **Écart majeur** : permissions absentes. Le premier message doit contenir le lien. Pas de relance automatique. | S9 : envoyer le lien dans l'unique réponse privée, sous 7 jours ; journaliser l'envoi pour ne jamais doubler. |
| Concours (S4/S5) | non vérifié | Règlement, exonération d'Instagram, mention de non-parrainage, pas d'identification inexacte (IG-R28) | À contrôler dans S6. | Ajouter ces trois mentions au gabarit concours. |
| Visuels générés par IA | non vérifié | Divulgation des contenus photoréalistes ; is_ai_generated dans l'API (IG-R30, IG-R31) | Paramètre absent de S7. | S5 : drapeau IA ; S7 : passer is_ai_generated. |
| Musique des Reels | non vérifié | Compte professionnel : bibliothèque sous licence possiblement indisponible ; Sound Collection (IG-R33) | Risque de son coupé. | S5 : son libre de droits ou original intégré au fichier. |
