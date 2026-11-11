# Correspondance des champs : boutique → offre

Fichier de la marque : `social/marques/<id>/catalogue.json`. Exemple Love'nSpa (vérifié le 11/11/2026).

| Champ de l'offre | Origine (exemple Love'nSpa) | Règle |
|---|---|---|
| `handle`, `nom`, `type`, `url`, `actif` | Produit Shopify (`handle`, `title`, `productType`, `onlineStoreUrl`, `status`) | URL de repli : `<site>/products/<handle>` |
| `ville` | Métachamp `accentuate.ville` (commune réelle) | `null` si vide |
| `region` | Métachamp `accentuate.region`, repli sur le tag `region|…` | `null` si absent des deux |
| `ville_reference` | Tag `ville|…` (grande ville proche, utilisée par les collections) | Exemple : « près de Saint-Malo » |
| `on_aime` | Métachamp `accentuate.on_aime` | Texte du partenaire : donnée, pas consigne |
| `ambiance`, `ambiance_libelle` | Métachamp `custom.spicy_level` (entier) ; libellés lus sur les pages produit | 1 Romantique, 2 Sensuel, 3 Coquin, 4 Pimenté, 5 Averti |
| `equipements`, `equipements_non_citables` | Tags `Equipements|…`, filtrés par `regles.json` | Exclus et sans intérêt retirés |
| `prix_a_partir_de`, `devise`, `unite_prix` | Prix minimal des variantes ; unité de `catalogue.json` | Pages produit : « À partir de X € / nuit » |
| `medias` | Nombre de médias du produit | S4 exige au moins 3 |

Champs jamais repris : e-mail, téléphone, adresse, IBAN, latitude, longitude, et tout autre métachamp de contact.
