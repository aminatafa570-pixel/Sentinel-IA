def generate_recommendations(event):
    reasons = (event.risk_reasons or "").lower()
    network_type = (event.network_type or "").lower()
    device = (event.device or "").lower()

    actions = []

    if event.security_action == "BLOCKED":
        priority = "CRITICAL"
        summary = (
            "La connexion a été bloquée. Une investigation humaine "
            "doit confirmer l’absence de compromission du compte."
        )
        actions.append("Maintenir le blocage de la session et de l’adresse IP.")
    elif event.security_action == "TEMP_BLOCK":
        priority = "HIGH"
        summary = (
            "La connexion est temporairement suspendue en attendant "
            "une vérification de l’identité de l’utilisateur."
        )
        actions.append("Exiger une authentification forte avant déblocage.")
    elif event.security_action == "MFA_REQUIRED":
        priority = "MEDIUM"
        summary = (
            "L’activité est inhabituelle mais non critique. "
            "Une vérification supplémentaire est recommandée."
        )
        actions.append("Déclencher une vérification MFA adaptative.")
    else:
        priority = "LOW"
        summary = (
            "Aucune action bloquante n’est nécessaire. "
            "Conserver l’événement pour l’analyse comportementale."
        )
        actions.append("Conserver l’événement dans le journal de sécurité.")

    if "échouée" in reasons:
        actions.append(
            "Vérifier les tentatives récentes et surveiller un éventuel brute force."
        )

    if "localisation" in reasons:
        actions.append(
            "Confirmer la localisation avec l’utilisateur et vérifier "
            "la réputation de l’adresse IP."
        )

    if "heure inhabituelle" in reasons:
        actions.append(
            "Comparer cette activité avec les horaires habituels de l’utilisateur."
        )

    if "anomalie comportementale" in reasons:
        actions.append(
            "Analyser les connexions précédentes du compte avant toute levée de blocage."
        )

    if network_type in {"tor", "proxy"}:
        actions.append(
            "Appliquer une politique renforcée : blocage de la source "
            "et réinitialisation des sessions actives."
        )

    if network_type == "vpn":
        actions.append(
            "Vérifier si ce VPN fait partie des réseaux approuvés par l’entreprise."
        )

    if "unknown" in device or "inconnu" in device:
        actions.append(
            "Demander l’enregistrement ou la validation de ce nouvel appareil."
        )

    return {
        "priority": priority,
        "summary": summary,
        "actions": list(dict.fromkeys(actions)),
    }