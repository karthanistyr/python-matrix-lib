import math
import time

def _seconds_to_iso8601_tz_shift_format(seconds):
    # this one's easy
    if(seconds == 0):
        return "Z"

    one_day_in_seconds = 86400
    if(seconds > one_day_in_seconds):
        raise ValueError("{} seconds exceeds the supported max value of {}" \
            .format(seconds, one_day_in_seconds))

    abs_seconds = math.sqrt(seconds*seconds)
    hours = math.floor(abs_seconds / 3600)
    minutes = math.floor((abs_seconds - hours*3600) / 60)
    # there isn't a need for "seconds" as there is no known TZ
    # shifted by fractional minutes

    return "{sign}{h}:{m}".format(
        sign="-" if seconds < 0 else "+",
        h="%02d" % hours,
        m="%02d" % minutes)

def to_iso8601(struct_time):
    return "{datetime}{tzshift}".format(
        datetime=time.strftime("%Y-%m-%dT%H:%M:%S", struct_time),
        tzshift=_seconds_to_iso8601_tz_shift_format(struct_time.tm_gmtoff)
        )

def get_microseconds():
    """Returns a time measurement in micro-seconds, rounded to the next µs"""
    return math.ceil(time.perf_counter() * 1000000)
