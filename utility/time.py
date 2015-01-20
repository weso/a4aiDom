import datetime


def utc_now():
    return datetime.datetime.time(datetime.datetime.utcnow())

print(utc_now())