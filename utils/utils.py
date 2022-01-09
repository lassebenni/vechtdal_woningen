from datetime import datetime


def convert_datetime(date_str: str, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    return datetime.strptime(date_str, format)
