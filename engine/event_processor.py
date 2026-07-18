from models.alert import Alert
from models.audit_log import AuditLog


ALERT_DECISIONS = {"TEMP_BLOCK", "BLOCKED"}


def process_event(session, event, risk_engine):
    analysis = risk_engine.analyze(event)

    event.risk_score = analysis["score"]
    event.risk_level = analysis["level"]
    event.risk_reasons = "; ".join(analysis["reasons"])
    event.security_action = analysis["decision"]

    session.add(event)
    session.flush()

    alert = None
    if analysis["decision"] in ALERT_DECISIONS:
        alert = Alert(
            event_id=event.id,
            user=event.user,
            level=analysis["level"],
            score=analysis["score"],
            reason=event.risk_reasons,
            status="OPEN",
        )
        session.add(alert)

    session.add(
        AuditLog(
            actor="Sentinel IA",
            action="Décision de sécurité appliquée",
            target_type="EVENT",
            target_id=event.id,
            details=(
                f"Utilisateur : {event.user} · "
                f"score : {analysis['score']}/100 · "
                f"décision : {analysis['decision']} · "
                f"raisons : {event.risk_reasons}"
            ),
        )
    )

    session.commit()
    session.refresh(event)

    return analysis, alert