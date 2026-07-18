from datetime import datetime, timezone

from models.alert import Alert
from models.audit_log import AuditLog
from models.event import Event


DECISIONS = {
    "LIFT_BLOCK": "ALLOWED",
    "REQUIRE_MFA": "MFA_REQUIRED",
    "MAINTAIN_TEMP_BLOCK": "TEMP_BLOCK",
    "PERMANENT_BLOCK": "BLOCKED",
}


def apply_response_action(session, incident, action, actor):
    alert = (
        session.query(Alert)
        .filter(Alert.id == incident.alert_id)
        .first()
    )

    event = None
    if alert and alert.event_id:
        event = (
            session.query(Event)
            .filter(Event.id == alert.event_id)
            .first()
        )

    decision = DECISIONS.get(action)
    action_labels = {
        "LIFT_BLOCK": "Levée du blocage",
        "REQUIRE_MFA": "MFA exigé",
        "MAINTAIN_TEMP_BLOCK": "Blocage temporaire maintenu",
        "PERMANENT_BLOCK": "Blocage définitif appliqué",
        "REVOKE_SESSIONS": "Sessions révoquées",
    }

    if event and decision:
        event.security_action = decision

    if action == "LIFT_BLOCK":
        incident.status = "RESOLVED"
        incident.resolved_at = datetime.now(timezone.utc)
        if alert:
            alert.status = "RESOLVED"
    else:
        incident.status = "CONTAINED"
        if alert:
            alert.status = "IN_PROGRESS"

    label = action_labels[action]
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    incident.comments = (
        f"{incident.comments or ''}\n"
        f"[{timestamp}] {actor} : {label}."
    ).strip()

    session.add(
        AuditLog(
            actor=actor,
            action=label,
            target_type="INCIDENT",
            target_id=incident.id,
            details=(
                f"Incident #{incident.id} · "
                f"alerte #{incident.alert_id} · "
                f"décision : {decision or 'aucune'}"
            ),
        )
    )

    session.commit()

    return label