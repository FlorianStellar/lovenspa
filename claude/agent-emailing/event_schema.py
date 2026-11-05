"""Contrat des événements Klaviyo poussés par la synchro Lovable (mission 2). Source unique des noms."""
EVENTS = {
    "Réservation commencée": ["logement_id", "logement_nom", "logement_url", "logement_image", "region",
                              "date_arrivee", "date_depart", "nb_nuits", "montant", "lien_reservation"],
    "Réservation confirmée": ["logement_id", "logement_nom", "logement_url", "logement_image", "region",
                              "date_arrivee", "date_depart", "nb_nuits", "montant"],
    "Séjour terminé": ["logement_id", "logement_nom", "logement_url", "logement_image", "region",
                       "date_arrivee", "date_depart", "nb_nuits", "montant"],
}
PROFILE_PROPS = ["marketing_basis", "consent_source", "consent_text_version", "dernier_logement_nom",
                 "dernier_logement_url", "dernier_logement_id", "derniere_region", "date_derniere_arrivee",
                 "date_dernier_depart", "nb_sejours", "montant_total"]
