import typing

from aiogram.utils.markdown import hbold, hlink

from schedule_ogu.models.db import ScheduleSubjectModel, EmployeeModel, ExamModel, UserModel, ScheduleModel
from schedule_ogu.models.enums import SubjectType, DayType, UserType


class RendererSchedule:
    subject_type = {
        SubjectType.lecture: "лек",
        SubjectType.practice: "пр",
        SubjectType.laboratory: "лаб",
        SubjectType.test: "зачёт",
        SubjectType.consultation: "конс",
        SubjectType.exam: "экзамен"
    }

    days_ru_short = {DayType.Monday: "пн",
                     DayType.Tuesday: "вт",
                     DayType.Wednesday: "ср",
                     DayType.Thursday: "чт",
                     DayType.Friday: "пт",
                     DayType.Saturday: "сб",
                     }

    days_ru = {DayType.Monday: "Понедельник",
               DayType.Tuesday: "Вторник",
               DayType.Wednesday: "Среду",
               DayType.Thursday: "Четверг",
               DayType.Friday: "Пятницу",
               DayType.Saturday: "Субботу",
               }

    times = {1: "08:30 - 10:00",
             2: "10:10 - 11:40",
             3: "12:00 - 13:30",
             4: "13:40 - 15:10",
             5: "15:20 - 16:50",
             6: "17:00 - 18:30",
             7: "18:40 - 20:10",
             8: "20:20 - 21:50"}

    @classmethod
    def render_base_subject(cls, subject: ScheduleSubjectModel) -> str:
        return f"📖 {hbold(f'{subject.number}.')} {subject.name}\n" \
               f"📌 {hbold(cls.subject_type.get(subject.type))}\n" \
               f"🕐 {cls.times[subject.number]}\n"

    @classmethod
    def render_employee(cls,
                        employee: EmployeeModel) -> str:
        return hlink(employee.short_full_name, employee.url)

    @classmethod
    def render_zoom(cls, subject: ScheduleSubjectModel | ExamModel):
        name = ""
        if subject.zoom_link is not None and subject.zoom_link != " ":
            name += f"\n💻  <a href='{subject.zoom_link}'>Конференция</a>"

        if subject.zoom_password is not None and subject.zoom_password != " ":
            name += f"\n  <b>Пароль:</b> {subject.zoom_password}"
        return name

    @classmethod
    def render_subject(cls,
                       user: UserModel,
                       subject: ScheduleSubjectModel) -> str:
        name = cls.render_base_subject(subject)
        if user.type == UserType.Student:
            name += f"👤 {cls.render_employee(subject.employee)}\n" \
                    f"🚪 {subject.building}-{subject.audience}"
        else:
            name += f"👤 {hbold(subject.group.name)}\n" \
                    f"🚪 {subject.building}-{subject.audience}"

        if subject.sub_group:
            name += "\n"
            name += f"  {hbold(f'Подгруппа {subject.sub_group}')}"

        name += cls.render_zoom(subject)

        return name

    @classmethod
    def render_exam(cls,
                    user: UserModel,
                    subject: ExamModel) -> str:
        name = f"📖 {subject.name}\n" \
               f"📌 {hbold(cls.subject_type.get(subject.type))}\n" \
               f"🕐 {subject.str_date} ({cls.days_ru_short[subject.day]}) ,{subject.time}\n"

        if user.type == UserType.Student:
            name += f"👤 {cls.render_employee(subject.employee)}\n" \
                    f"🚪 {subject.dislocation}"
        else:
            name += f"👤 {hbold(subject.group.name)}\n" \
                    f"🚪 {subject.dislocation}"

        if subject.sub_group:
            name += "\n"
            name += f"  {hbold(f'Подгруппа {subject.sub_group}')}"

        name += cls.render_zoom(subject)

        return name

    @classmethod
    def render_subject_with_sub_groups(cls,
                                       user: UserModel,
                                       schedule: typing.List[ScheduleSubjectModel]) -> str:
        subject = schedule[0]
        name = cls.render_base_subject(subject)
        for index in range(len(schedule)):
            item = schedule[index]
            if index != 0 and index != len(schedule):
                name += f"  ▬▬▬▬▬▬\n"
            if user.type == UserType.Student:
                name += f"👤 {cls.render_employee(subject.employee)}\n" \
                        f"🚪 {subject.building}-{subject.audience}" \
                        f"  {hbold(f'Подгруппа {item.sub_group}')}"
            else:
                name += f"👤 {hbold(subject.group.name)}\n" \
                        f"🚪 {subject.building}-{subject.audience}" \
                        f"  {hbold(f'Подгруппа {item.sub_group}')}"

            if index != len(schedule) - 1:
                name += "\n"

        if subject.zoom_link is not None and subject.zoom_link != " ":
            name += f"\n💻  <a href='{subject.zoom_link}'>Конференция</a>"

        if subject.zoom_password is not None and subject.zoom_password != " ":
            name += f"\n  <b>Пароль:</b> {subject.zoom_password}"

        return name

    @classmethod
    def render_day(cls,
                   user: UserModel,
                   schedule: dict[DayType, ScheduleModel],
                   day: DayType
                   ) -> str:
        sch = schedule.get(day)

        header = f"Расписание на <u>{cls.days_ru[sch.day]}</u>: {sch.str_date} \n\n"

        if not sch.subjects:
            header += hbold("Спи спокойно сегодня нет пар")
            return header

        subjects = sorted(sch.subjects, key=lambda x: (x.number, x.sub_group))

        str_subjects: typing.List[str] = []
        prepared_schedule: dict[int, list[ScheduleSubjectModel]] = {}

        for index in range(1, max(subject.number for subject in subjects) + 1):
            prepared_schedule[index] = []

        for subject in subjects:
            prepared_schedule[subject.number].append(subject)

        for number, items in prepared_schedule.items():
            if not items:
                str_subjects.append(f'🗿 {hbold(f"{number}. Окно")}')
            elif len(items) == 1:
                str_subjects.append(cls.render_subject(user, items[0]))
            else:
                str_subjects.append(cls.render_subject_with_sub_groups(user, items))

        return header + "\n\n".join(str_subjects)

    @classmethod
    def render_exams(cls,
                     user: UserModel,
                     schedule: typing.List[ExamModel],
                     ) -> str:
        schedule = sorted(schedule, key=lambda x: x.date)

        header = f"Расписание Экзаменов\n\n"

        str_subjects: typing.List[str] = []

        for exam in schedule:
            str_subjects.append(cls.render_exam(user, exam))

        return header + "\n\n".join(str_subjects)


def format_buttons(buttons, row_width=3):
    keyboard = []
    row = []
    for index, button in enumerate(buttons, start=1):
        row.append(button)
        if index % row_width == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return keyboard
