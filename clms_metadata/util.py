import datetime


def format_zulu(date: datetime.datetime) -> str:
    """
    Format a datetime object as a zulu time string.
    :param date: the datetime object to format
    :return: the formatted datetime string
    """
    timespec = "auto"
    if date.microsecond:
        # prefer milliseconds if possible
        timespec = "milliseconds" if date.microsecond % 1000 == 0 else "microseconds"
    if date.tzinfo is None:
        return date.isoformat(timespec=timespec) + "Z"
    else:
        return date.isoformat(timespec=timespec).replace("+00:00", "Z")
