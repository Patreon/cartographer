from datetime import timezone as timezone_


def as_utc(dt):
    if hasattr(dt, 'tzinfo'):
        if dt.tzinfo:
            return dt.astimezone(timezone_.utc)
        else:
            return dt.replace(tzinfo=timezone_.utc)
    return dt


def make_naive(dt):
    return as_utc(dt).replace(tzinfo=None)
