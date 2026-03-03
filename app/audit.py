import json
from .extensions import db
from .models import AuditLog

def log_action(actor_id: int, action: str, entity_type: str | None = None, entity_id: int | None = None, meta: dict | None = None):
    row = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        meta_json=json.dumps(meta or {}, ensure_ascii=False),
    )
    db.session.add(row)
    db.session.commit()
