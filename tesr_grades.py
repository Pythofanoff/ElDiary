from dbmanager import DBManager
import tkinter as tk

DBManager().create_db()

group_selected = 'ИСП,23-29'
fio = 'Test'

get_id_by_user = DBManager().get_id_by_users(data=(group_selected, fio))
if get_id_by_user:
    get_id_by_user = get_id_by_user[0][0]
else:
    pass

print('get_id_by_user: ', get_id_by_user)

marks_by_days: list = ['day' for day in range(1, 32)]
format_marks = ','.join(marks_by_days)
print('format_marks: ', format_marks)

get_discipline_id = DBManager().get_discipline_id(discipline='Русский', group=group_selected)[0]
print('get_discipline_id: ', get_discipline_id)

DBManager().save_or_update_grade(student_id=get_id_by_user, discipline_id=get_discipline_id, grade=format_marks, month_translit='sep_month')
    

