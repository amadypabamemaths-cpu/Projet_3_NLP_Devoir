"""Gabarits de messages frauduleux et légitimes + pools de substitution.

Le notebook et data_io.py génèrent le corpus à partir d'ici tant que l'équipe
n'a pas déposé ses vrais messages dans data/local/*.jsonl.
"""

FRAUD_TEMPLATES = [
    ("faux_gain",    "Félicitations ! Votre numéro a été tiré au sort et vous avez gagné {amount} FCFA. Envoyez {fee} FCFA de frais au {phone} pour réclamer."),
    ("faux_gain",    "Vous avez gagné {amount} FCFA à la loterie {org}. Cliquez ici : {url}"),
    ("faux_gain",    "CONGRATULATIONS! You won {amount} FCFA. Send {fee} FCFA to claim: {phone}"),
    ("faux_gain",    "Congratulation! You don win {amount} FCFA. Send {fee} to collect: {phone}"),
    ("faux_agent",   "Bonjour, j'ai envoyé {amount} FCFA par erreur sur votre numéro. Renvoyez-les au {phone} svp."),
    ("faux_agent",   "Je me suis trompé de destinataire. Renvoyez {amount} FCFA au {phone} merci."),
    ("phishing",     "Votre compte {op} sera suspendu dans 24h. Vérifiez ici : {url}"),
    ("phishing",     "Activité suspecte sur votre compte {op}. Confirmez votre code secret au {phone} immédiatement."),
    ("phishing",     "Your {op} account will be suspended. Verify at {url}"),
    ("faux_emploi",  "Offre d'emploi : Assistant(e), {amount} FCFA/mois, télétravail. Frais de dossier {fee} FCFA. Contactez {phone}."),
    ("faux_emploi",  "Recrutement urgent. Envoyez {fee} FCFA de frais au {phone} pour postuler. Places limitées."),
    ("faux_service", "Service client {op} : transaction suspecte. Communiquez votre code secret à 4 chiffres pour la bloquer."),
    ("faux_service", "Cher client {op}, votre compte est bloqué. Envoyez votre code PIN au {phone} pour le débloquer."),
    ("faux_proche",  "Papa, c'est moi, j'ai un problème. J'ai besoin de {amount} FCFA urgent. Envoie au {phone}."),
    ("faux_proche",  "Maman, mon téléphone est cassé, prête-moi {amount} FCFA sur ce numéro {phone}."),
]

LEGIT_TEMPLATES = [
    ("notif_paiement", "Vous avez reçu {amount} FCFA de {name} le {date}. Réf : {ref}. Voir le reçu : {url_legit}"),
    ("notif_paiement", "Votre paiement de {amount} FCFA à {org} a bien été enregistré. Merci."),
    ("rappel_facture", "Rappel : votre facture {org} de {amount} FCFA est due le {date}."),
    ("otp",            "Votre code de confirmation est {otp}. Ne le partagez avec personne."),
    ("otp",            "Code de validation : {otp}. Valable 5 minutes. Ne le communiquez à personne."),
    ("livraison",      "Votre commande #{ref} est en cours de livraison. Livreur : {name}, {phone}."),
    ("livraison",      "Colis #{ref} livré aujourd'hui. Merci de votre confiance."),
    ("marketing",      "Promo -20% sur tous les pagnes wax jusqu'à dimanche chez {org}."),
    ("marketing",      "Nouvelle collection disponible chez {org}. Livraison gratuite cette semaine."),
    ("conversation",   "Salut, on se voit toujours à {time} ce soir ? Je serai un peu en retard."),
    ("conversation",   "Merci pour hier, à bientôt !"),
    ("conversation",   "Tu peux m'envoyer le document quand tu peux ? Pas urgent."),
    ("notification",   "Votre mot de passe a été modifié avec succès. Si vous n'êtes pas à l'origine de ce changement, contactez le service client."),
    ("rappel_facture", "Votre abonnement {org} expire le {date}. Renouvelez depuis l'application."),
]

# Pièges : messages LÉGITIMES qui contiennent lien + montant.
TRAP_TEMPLATES = [
    "Vous avez reçu {amount} FCFA de {name}. Réf : {ref}. Voir le reçu : {url_legit}",
    "Votre commande #{ref} est livrée. Montant : {amount} FCFA. Suivi : {url_legit}",
    "Paiement de {amount} FCFA confirmé chez {org}. Détails : {url_legit}",
    "Facture {org} de {amount} FCFA réglée. Télécharger : {url_legit}",
    "Transfert de {amount} FCFA vers {name} effectué. Réf : {ref}. Statut : {url_legit}",
    "Reçu #{ref} : {amount} FCFA reçus de {name}. Vérifier : {url_legit}",
    "Votre abonnement {org} ({amount} FCFA) est actif. Gérer : {url_legit}",
    "Commande #{ref} expédiée. Total : {amount} FCFA. Suivi : {url_legit}",
    "Remboursement de {amount} FCFA effectué. Détails : {url_legit}",
    "Nouveau paiement reçu : {amount} FCFA de {name}. Réf : {ref}. Reçu : {url_legit}",
]

# --- Pools de substitution -------------------------------------------------
NAMES = ["Awa Diop", "Moussa Fall", "Fatou Ndiaye", "Ibrahima Sow", "Aminata Ba",
         "Ousmane Diallo", "Khadija Sy", "Aliou Cissé", "Mariama Traoré", "Cheikh Diop"]
AMOUNTS = ["500 000", "250 000", "100 000", "50 000", "25 000", "15 000", "10 000",
           "5 000", "2 000", "1 500 000"]
FEES = ["5 000", "3 000", "2 000", "1 000", "500", "10 000"]
PHONES = ["07 XX XX XX XX", "77 XXX XX XX", "78 XXX XX XX", "76 XXX XX XX", "+221 77 XXX XX XX"]
ORGS = ["Wave", "Orange Money", "MTN MoMo", "Senelec", "TissuPlus", "Free", "Expresso"]
OPS = ["Wave", "Orange Money", "MTN MoMo", "Free Money"]
URLS = ["http://bit.ly/xx", "https://wave-secure-verif.xyz/update", "http://gagne-500k.top",
        "https://mtn-momo-verif.tk/pin", "http://bit.ly/claim-prize"]
URLS_LEGIT = ["https://wave.com/recu/8841", "https://orange.sn/facture", "https://mtn.sn/track"]
REFS = [f"MP2403{str(i).zfill(2)}-{8840+i}" for i in range(20)]
DATES = ["12/03 à 14:05", "13/03 à 09:12", "20/03 à 18:30", "le 25/03", "le 02/04"]
TIMES = ["19h", "20h", "12h30", "18h", "demain à 10h"]
OTPS = [str(1000 + i) for i in range(9000)]


def fill(template: str, rng) -> str:
    """Substitue les variables du gabarit en tirant aléatoirement dans les pools."""
    return template.format(
        amount=rng.choice(AMOUNTS), fee=rng.choice(FEES), phone=rng.choice(PHONES),
        org=rng.choice(ORGS), op=rng.choice(OPS),
        url=rng.choice(URLS), url_legit=rng.choice(URLS_LEGIT),
        name=rng.choice(NAMES), ref=rng.choice(REFS),
        date=rng.choice(DATES), time=rng.choice(TIMES), otp=rng.choice(OTPS),
    )