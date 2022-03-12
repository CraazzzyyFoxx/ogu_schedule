import enum


class DayType(enum.IntEnum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


def try_value(cls, value):
    for name, value_ in cls._member_map_.items():
        if value_.value == int(value):
            return cls._member_map_[name]
    return value
