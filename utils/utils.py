from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/Amsterdam")


def convert_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    return datetime.strptime(date_str, format)


def convert_iso_datetime(date_str: Optional[str]) -> Optional[str]:
    """'2026-10-05T10:00:00.000Z' -> '2026-10-05 12:00:00' (Dutch local time)."""
    if not date_str:
        return None
    parsed = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    return parsed.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")


def convert_iso_date(date_str: Optional[str]) -> Optional[str]:
    """'2026-11-20T00:00:00.000Z' -> '2026-11-20 00:00:00'. Date-only values, no timezone shift."""
    if not date_str:
        return None
    return f"{date_str[:10]} 00:00:00"
