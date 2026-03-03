from datetime import datetime

def is_late(submitted_at: datetime, deadline_at: datetime) -> bool:
    return submitted_at > deadline_at
