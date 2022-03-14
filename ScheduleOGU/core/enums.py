import enum


class DayType(enum.IntEnum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


class EducationalLevel(enum.IntEnum):
    Undergraduate = 0
    Specialty = 1
    Magistracy = 2
    Postgraduate = 3
    Residency = 4


class Years(enum.IntEnum):
    First = 1
    Second = 2
    Third = 3
    Fourth = 4
    Fifth = 5


def try_value(cls, value):
    for name, value_ in cls._member_map_.items():
        if value_.value == int(value):
            return cls._member_map_[name]
    return value


days_ru = {DayType.Monday: "Понедельник",
           DayType.Tuesday: "Вторник",
           DayType.Wednesday: "Среда",
           DayType.Thursday: "Четверг",
           DayType.Friday: "Пятница",
           DayType.Saturday: "Суббота",
           }

educational_level_ru = {"бакалавриат": EducationalLevel.Undergraduate,
                        "специалитет": EducationalLevel.Specialty,
                        "магистратура": EducationalLevel.Magistracy,
                        "аспирантура": EducationalLevel.Postgraduate,
                        "ординатура": EducationalLevel.Residency
                        }

times = {1: "08:30 - 10:00",
         2: "10:10 - 11:40",
         3: "12:00 - 13:30",
         4: "13:40 - 15:10",
         5: "15:20 - 16:50",
         6: "17:00 - 18:30",
         7: "18:40 - 20:10",
         8: "20:20 - 21:50"}
