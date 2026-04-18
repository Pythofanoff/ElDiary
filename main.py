# Задействие дисциплин в оценках
# Добавить подсчёт процента успеваемости студента
# Баг: у дисциплины перестало срабатывать проверку на уникальность (связано с перезаписью self.discipline в update_widgets())
# Добавить возможность описания и сводки всех данных о студенте (подробно), добавить эту фичу вниз таблицы

# Добавить возможность удалять записи с > 1 общей группой
# Добавить изменение групп для дисциплины  
# Сделать скроллбары поудобнее
# Подсветка оценок (2 - красный, 3 - оранжевый, 4 - жёлтый, 5 - зелёный)
# Добавить разлиновку полей 
# Оптимизация кода: уменьшение потребления ОЗУ

# Импорт всех нужных библиотек
import itertools
import tkinter as tk
from functools import reduce
from tkinter import messagebox, ttk

from dbmanager import DBManager


# Главный класс
class MainWindow(tk.Frame):
    month_translit: dict = {
        'Сентябрь': 'sep_month',
        'Октябрь': 'oct_month',
        'Ноябрь': 'nov_month',
        'Декабрь': 'dec_month',
        'Январь': 'jan_month',
        'Февраль': 'feb_month',
        'Март': 'mar_month',
        'Апрель': 'apr_month',
        'Май': 'may_month',
        'Июнь': 'jun_month'
    }

    # Инициализация важных компонентов 
    def __init__(self, root): 
        self.root = root 

        self.getdisciplines = DBManager().get_all_disciplines()

        self.pairs_disciplines: dict = {}
        for i in range(len(self.getdisciplines)):
            my_list: list = self.getdisciplines[i][0].split(',')
            self.pairs_disciplines[tuple(my_list)] = self.pairs_disciplines.get(tuple(my_list), []) + [self.getdisciplines[i][1]]

        # Создание переменной для combobox'а 
        self.months = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь']
        self.month_var = tk.StringVar(self.root, value=self.months[0])
        self.month_selected = 'Сентябрь'
        
        # Создание переменной для combobox'а 
        self.disciplines = ['Добавить дисциплину...', 'Удалить дисциплину...', 'Изменить дисциплину...']
        self.discipline_var = tk.StringVar(self.root, value=self.disciplines[0])
        self.discipline_selected = 'Добавить дисциплину...'

        # Создание переменной для combobox'а 
        self.mark = ['н\б', 2, 3, 4, 5]
        self.mark_var = tk.StringVar(value=self.mark[0])

        # Создание переменной для combobox'а 
        get_allGroups = DBManager().get_all_groups()
        # print('get_allGroups: ', get_allGroups)

        self.group = [x for y in get_allGroups for x in y] + ['Добавить группу...']
        # self.group.extend(['Добавить группу...'])
        # print('init first self.group: ', self.group)

        self.group_var = tk.StringVar(value=self.group[0])
        self.group_selected = self.group[0]


        self.month_translit_selected = MainWindow.month_translit.get(self.month_selected, '')

        self.data = DBManager().get_all_users(group_name=self.group_selected, month_translit=self.month_translit_selected)

        # Первоначальный запуск функций 
        self.init_filters()
        self.group_selected = self.cmb_month.get().strip()
        self.init_scrollbar()
        self.init_tree()

        self.binds()
        self.update_widgets()
        
    # Создание и работа с фильтрами над таблицей
    def init_filters(self):
        try:
            self.filter_frame.destroy()
        except AttributeError:
            pass 

        self.filter_frame = tk.Frame(self.root, bg='lightgray', height=29)
        self.filter_frame.pack(padx=0, pady=(0,6), fill='both')

        self.lbl_filter_month = tk.Label(self.filter_frame, text='Выберите месяц: ')
        self.lbl_filter_month.pack(anchor='e', side='left')
        self.cmb_month = ttk.Combobox(self.filter_frame, textvariable=self.month_var, values=self.months, state='readonly')
        self.cmb_month.pack(anchor='e', side='left')

        self.lbl_filter_discipline = tk.Label(self.filter_frame, text='Выберите дисциплину: ')
        self.lbl_filter_discipline.pack(padx=(3,2), anchor='e', side='left')
        self.cmb_discipline = ttk.Combobox(self.filter_frame, textvariable=self.discipline_var, values=self.disciplines, width=24, state='readonly')
        self.cmb_discipline.pack(anchor='e', side='left')

        self.lbl_filter_group = tk.Label(self.filter_frame, text='Выберите группу: ')
        self.lbl_filter_group.pack(padx=(3,2), anchor='e', side='left')
        self.cmb_group = ttk.Combobox(self.filter_frame, textvariable=self.group_var, values=self.group, width=24, state='readonly')
        self.cmb_group.pack(anchor='e', side='left')

        ttk.Button(self.filter_frame, text='Добавить студента...', command=self.add_students).pack(padx=(3,2), anchor='e', side='left')
        ttk.Button(self.filter_frame, text='Удалить студента(ов)', command=self.delete_students).pack(padx=(3,2), anchor='e', side='left')
        ttk.Button(self.filter_frame, text='Обновить', command=self.update_widgets).pack(padx=(3,2), anchor='e', side='left')

    # Метод добавления нового пользователя в таблицу
    def add_students(self, event=None):
        dialog, frame = self.create_dialog(title='Добавление нового студента...')

        # frame1 = tk.Frame(dialog)
        # frame1.pack(padx=4, fill='x')

        tk.Label(frame, text='Введите нового студента: ').pack(side='left', padx=4)

        entry_add_user = ttk.Entry(frame, width=25)
        entry_add_user.pack(padx=(3,0), pady=(5,5), side='left', anchor='e')
        entry_add_user.focus()

        frame2 = tk.Frame(dialog)
        frame2.pack(padx=4, fill='x')

        lbl = tk.Label(frame2, text='Введите группу: ')
        lbl.pack(side='left', padx=4)

        entry_add_group = ttk.Combobox(frame2, textvariable=self.group_var, values=self.group, width=24)
        entry_add_group.pack(padx=(5,0), pady=(5,5), side='right', anchor='e')

        def save(): 
            data = (entry_add_user.get().strip(), entry_add_group.get().strip()) + (','*30,)*10
            print('save_data_user: ', data)

            DBManager().add_user(data)

            self.update_widgets()

        ttk.Button(dialog, text='Сохранить', command=save).pack(side='bottom', pady=2)
            
    # Метод удаления студента / студентов по выделению в таблице
    def delete_students(self, event=None):
        iid = self.tree3.selection()
        msg = messagebox.askyesno('Предупреждение', 'Вы хотите удалить студента(ов) из таблицы безвозвратно?')

        if iid and msg:
            id_list: list = [self.tree3.set(id, 'Обучающиеся') for id in iid]

            for id in id_list:
                DBManager().delete_user(data=(id, self.cmb_group.get()))
        else:
            return 

        self.update_widgets()

    # Инициализация горячих клавиш
    def binds(self):
        self.cmb_month.bind('<<ComboboxSelected>>', self.get_month)

        self.cmb_discipline.bind('<<ComboboxSelected>>', self.get_discipline)
        # self.cmb_discipline.bind('<Enter>', self.delete_discipline)

        self.cmb_group.bind('<<ComboboxSelected>>', self.get_group)

        self.tree3.bind('<Button-1>', self.edit_value)

        self.root.bind('<Control-S>', self.update_widgets)
        self.root.bind('<Control-s>', self.update_widgets)
        self.root.bind('<Control-R>', self.update_widgets)
        self.root.bind('<Control-r>', self.update_widgets)
        self.root.bind('<F5>', self.update_widgets)
        self.root.bind('<Control-A>', self.add_students)
        self.root.bind('<Control-a>', self.add_students)
        self.root.bind('<Control-D>', self.delete_students)
        self.root.bind('<Control-d>', self.delete_students)
        self.root.bind('<Delete>', self.delete_students)

    # Вспомогательный метод для правильного закрытия окна
    def dismiss(self, window):
        window.grab_release() 
        window.destroy()

    # Метод обновления виджетов и данных 
    def update_widgets(self, event=None):
        # self.group_var.set(self.group[0])

        self.month_selected = self.month_var.get()
        self.discipline_selected = self.discipline_var.get()
        self.group_selected = self.group_var.get()
        # self.cmb_group.set(self.group[0])

        self.month_translit_selected = MainWindow.month_translit.get(self.month_selected, '')
        self.data = DBManager().get_all_users(group_name=(self.cmb_group.get().strip(),), month_translit=self.month_translit_selected)

        self.disciplines: list = [] 
        for key in self.pairs_disciplines.keys():
            if self.group_selected in list(key):  
                self.disciplines.extend(self.pairs_disciplines.get(key, ''))

        self.disciplines.append('Добавить дисциплину...')
        self.disciplines.append('Удалить дисциплину...')
        self.disciplines.append('Изменить дисциплину...')

        self.init_filters()
        self.init_scrollbar()
        self.init_tree()

        self.binds()

    # Метод Диалогового окна (универсальное под разные задачи) 
    def create_dialog(self, title: str):
        dialog = tk.Toplevel(self.root)
        dialog.iconbitmap('icon.ico')
        dialog.title(title)
        dialog.geometry('300x120')
        dialog.resizable(False, False)
        dialog.grab_set()

        frame = tk.Frame(dialog)
        frame.pack(side='bottom')

        return dialog, frame

    # Получение месяца из combobox'а
    def get_month(self, event=None):
        self.month_selected = self.cmb_month.get().strip()
        self.update_widgets()

    # Получение дисциплины из combobox'а
    def get_discipline(self, event=None):
        self.group_selected = self.cmb_discipline.get().strip()

        # Если пользователь выбрал удаление дисциплины
        if self.group_selected == 'Удалить дисциплину...':
            dialog, frame = self.create_dialog(title='Удаление дисциплины...')

            frame2 = tk.Frame(dialog)
            frame2.pack(fill='x')

            tk.Label(frame, text='Введите дисциплину для удаления: ').pack(side='left')

            entry_discipline = ttk.Entry(frame, width=25)
            entry_discipline.pack(padx=(5,5), pady=(5,3), side='left')
            entry_discipline.focus()

            tk.Label(frame2, text='Введите группу для удаления: ').pack(side='left')

            entry_group = ttk.Entry(frame2, width=25)
            entry_group.pack(padx=(0,5), pady=(3,4), side='right')

            # Удаление дисциплины
            def delete_discipline(event=None):  
                delete_name = entry_discipline.get().strip()
                group = entry_group.get().strip()

                if not group:
                    messagebox.showerror('Ошибка', 'Поле группы пустое', parent=dialog)
                    return 
  
                if delete_name not in self.disciplines:                    
                    messagebox.showerror('Ошибка', 'Такой дисциплины не существует', parent=dialog)
                    return
                else:
                    group = ','.join(group.split())
                    DBManager().delete_discipline(data=(delete_name, group))
                    self.disciplines.insert(0, delete_name)
                    self.cmb_discipline.set(self.disciplines[0])
                    self.update_widgets()
                    return

            entry_discipline.bind('<Return>', delete_discipline)
            entry_group.bind('<Return>', delete_discipline)
            ttk.Button(dialog, text='Удалить', command=delete_discipline).pack(side='bottom', pady=(0,2))

        # Если пользователь выбрал изменение дисциплины
        elif self.group_selected == 'Изменить дисциплину...':
            dialog, frame = self.create_dialog(title='Изменение дисциплины...')

            frame2 = tk.Frame(dialog)
            frame2.pack(fill='x')

            tk.Label(frame, text='Введите дисциплину для изменения названия: ').pack(side='left')

            entry_discipline = ttk.Entry(frame, width=25)
            entry_discipline.pack(padx=(5,0), pady=(5,3), side='left')
            entry_discipline.focus()

            tk.Label(frame2, text='Введите новое название: ').pack(side='left')

            entry_new_name = ttk.Entry(frame2, width=25)
            entry_new_name.pack(padx=(0,5), pady=(3,4), side='right')

            def edit_discipline(event=None):  
                edit_name = entry_discipline.get().strip()
                new = entry_new_name.get().strip()

                if not new:
                    messagebox.showerror('Ошибка', 'Поле нового название пустое', parent=dialog)
                    return 
  
                if edit_name not in self.disciplines:                    
                    messagebox.showerror('Ошибка', 'Такой дисциплины не существует', parent=dialog)
                    return
                else:
                    DBManager().edit_discipline(data=(new, edit_name))
                    self.disciplines.insert(0, edit_name)
                    self.cmb_discipline.set(self.disciplines[0])
                    self.update_widgets()
                    return

            entry_discipline.bind('<Return>', edit_discipline)
            entry_new_name.bind('<Return>', edit_discipline)
            ttk.Button(dialog, text='Изменить', command=edit_discipline).pack(side='bottom', pady=(0,2))

        # Если пользователь выбрал добавление дисциплины
        elif self.group_selected == 'Добавить дисциплину...':
            dialog, frame = self.create_dialog(title='Добавление новой дисциплины...')

            frame2 = tk.Frame(dialog)
            frame2.pack(fill='x')

            tk.Label(frame, text='Введите новую дисциплину: ').pack(side='left')

            entry_add_discipline = ttk.Entry(frame, width=25)
            entry_add_discipline.pack(padx=(5,0), pady=(5,3), side='left')
            entry_add_discipline.focus()

            tk.Label(frame2, text='Введите группу: ').pack(side='left')

            entry_group = ttk.Combobox(frame2, textvariable=self.group_var, values=self.group, width=25)
            entry_group.pack(padx=(0,5), pady=(3,4), side='right')

            def save_disciplines(event=None):  
                new = entry_add_discipline.get().strip()
                group = entry_group.get().strip()

                if not group:
                    messagebox.showerror('Ошибка', 'Поле группы пустое', parent=dialog)
                    return 
  
                if new not in self.disciplines:
                    group = ','.join(group.split())
                    DBManager().add_discipline(data=(new, group))
                    self.disciplines.insert(0, new)
                    # self.cmb_discipline.set(self.disciplines[0])
                    entry_add_discipline.delete(0, tk.END)
                    self.update_widgets()
                    return
                else:
                    messagebox.showerror('Ошибка', 'Такая дисциплина уже существует', parent=dialog)
                    return

            entry_add_discipline.bind('<Return>', save_disciplines)
            entry_group.bind('<<ComboboxSelected>>', save_disciplines)
            ttk.Button(dialog, text='Добавить', command=save_disciplines).pack(side='bottom', pady=(0,2))

            self.root.wait_window(dialog)
        else:
            self.update_widgets()

    # Получение группы из combobox'а
    def get_group(self, event):
        self.group_selected = self.cmb_group.get().strip()

        if self.group_selected == 'Добавить группу...':
            dialog, frame = self.create_dialog(title='Добавление новой группы...')

            tk.Label(dialog, text='Введите новую группу: ').pack(side='left')

            entry_add_group = ttk.Entry(dialog, width=25)
            entry_add_group.pack(padx=(5,0), pady=(5,5), side='left')
            entry_add_group.focus()

            def save_group(event=None):
                new = entry_add_group.get().strip()

                if new not in self.group:
                    self.group.insert(0, new)
                    self.cmb_group.set(self.group[0])
                    self.group_selected = self.cmb_group.get()
                    self.group_var.set(self.group[0])
                    self.update_widgets()
                    return
                else:
                    messagebox.showerror('Ошибка', 'Такая группа уже существует', parent=dialog)
                    return

            entry_add_group.bind('<Return>', save_group)
            ttk.Button(frame, text='Добавить', command=save_group).pack(side='bottom', pady=(0,2))
            self.update_widgets()
            
            self.root.wait_window(dialog)
        else:
            self.update_widgets()

    # Инициализация полос прокрутки
    def init_scrollbar(self):
        # Безопасное удаление полос прокрутки если они существуют (для удаления повторных полос прокрутки)
        try:
            self.scrl_bar.destroy()
            self.scrl_bar_horizont.destroy()
        except AttributeError:
            pass
            
        self.scrl_bar = tk.Scrollbar(self.root, orient='vertical')
        self.scrl_bar.pack(side='right', fill='y')
        
        self.scrl_bar_horizont = tk.Scrollbar(self.root, orient='horizontal')
        self.scrl_bar_horizont.pack(side='bottom', fill='x')

    # Инициализация таблиц (Дерево TreeView)
    def init_tree(self):
        # Безопасное удаление таблиц если они существуют (для обновления таблиц)
        try:
            self.tree1.destroy()
            self.tree2.destroy()
            self.tree3.destroy()
        except AttributeError:
            pass 

        # Treeview - 1 ()
        self.discipline: list = [self.discipline_selected]
        self.headings = ['discipline']

        self.tree1 = ttk.Treeview(self.root, columns=self.headings, show='headings', height=0)
        self.tree1.pack()

        for var, heading in zip(self.headings, self.discipline):
            self.tree1.heading(var, text=heading)
            self.tree1.column(var, stretch=True, width=1000)

        # Treeview - 2 ()
        self.columns: list = ['', self.month_selected, '']
        self.tree2 = ttk.Treeview(self.root, columns=self.columns, show='headings', height=0)
        self.tree2.pack(pady=(1,0), fill='both')

        for heading, column in zip(self.columns, self.columns):
            self.tree2.heading(heading, text=heading)

        # Treeview - 3 ()
        date = [str(_) for _ in range(1, 32)]
        self.date: list = ['№'] + ['Обучающиеся'] + date + ['Ср. балл'] + ['Процент успеваемости']
        get_count_students_group = DBManager().get_count_students_group(data=self.group_selected)

        self.tree3 = ttk.Treeview(self.root, columns=self.date, show='headings')
        self.tree3.pack(fill='both')
        self.scrl_bar.configure(command=self.tree3.yview)
        self.scrl_bar_horizont.configure(command=self.tree3.xview)
        self.tree3.configure(yscrollcommand=self.scrl_bar.set, xscrollcommand=self.scrl_bar_horizont.set)
        
        for heading in self.date:
            self.tree3.heading(heading, text=heading)
            self.tree3.column(heading, stretch=False, width=932)

        self.tree3.column('№', width=25)
        self.tree3.column('Обучающиеся', width=210)

        for date in date:
            self.tree3.column(date, width=48)

        self.tree3.column('Ср. балл', width=70)
        self.tree3.column('Процент успеваемости', width=150)

        # Функция получения чисел из строки
        def parse_int(s: str):
            try:
                return int(s)
            except ValueError:
                return None

        # Функция расчёта сред. балла
        def avg_mark(i: int = 0):
            leng = len(mark_list[i])
            try:
                sums = sum(list(float(s) for inner_list in mark_list[i] for s in inner_list if parse_int(s)))
                return round(sums / leng, 2)
            except ZeroDivisionError:
                return 0

        # Список оценок
        mark_list = [[item for item in self.data[i][2].split(',') if item.isdigit()] for i in range(len(self.data))]

        # Список с данными о пользователях
        self.data_format: list = [
            (
                i+1,
                self.data[i][1],
                *self.data[i][2].split(','),
                avg_mark(i),
                '0%'
            )
            for i in range(len(self.data))
        ]

        print('data_format: ', self.data_format)

        # Вставка данных о пользователе
        for data in self.data_format:
            self.tree3.insert('', tk.END, values=data)

    # Метод изменения значения в поле таблице
    def edit_value(self, event):
        # Список неизменяемых колонок
        non_editable_cols: list = ['№', 'Ср. балл', 'Процент успеваемости']

        item = self.tree3.identify_row(event.y)
        col = self.tree3.identify_column(event.x)

        try:
            x, y, width, height = self.tree3.bbox(item, col)
            col_indx = int(col.replace('#', '')) - 1 
            col_name = self.tree3['columns'][col_indx]
        except ValueError:
            return

        if col_name in non_editable_cols:
            return 

        values = list(self.tree3.item(item, 'values'))
        
        # Если не колонка Обучающиеся ttk.Combobox
        if col_name != 'Обучающиеся':
            cmb_value = ttk.Combobox(textvariable=self.mark_var, values=self.mark)
            cmb_value.place(x=x, y=y, width=width+1, height=height, in_=self.tree3)
            cmb_value.focus()
        else:
            # Если колонка Обучающиеся разместить ttk.Entry
            cmb_value = ttk.Entry()
            cmb_value.place(x=x, y=y, width=width, height=height, in_=self.tree3)
            cmb_value.focus()
            cmb_value.insert(0, values[col_indx])

        # Метод сохранения значения в поле таблицы
        def save_value(event=None):
            values[col_indx] = cmb_value.get().strip()

            # Если ФИО пользователя было стёрто полностью
            if col_name == 'Обучающиеся' and cmb_value.get().strip() == '' or cmb_value.get().strip() == ' ':
                msg = messagebox.askyesno('Предупреждение', 'Вы стёрли информацию о студенте, вы хотите удалить этого студента из таблицы?')
                if msg:
                    iid = self.tree3.selection()
                    if iid:
                        val = self.group_var.get().strip()
                        val2 = self.tree3.set(iid, 'Обучающиеся')

                    data = (val2, val)
                    
                    DBManager().delete_user(data)
                    self.update_widgets()
                else:
                    return 

            # Изменить данные о пользователе если значение в этой ячейки можно поменять 
            if col_name not in non_editable_cols:
                self.tree3.item(item, values=values)
                iid = self.tree3.selection()

                fio = self.tree3.set(iid, 'Обучающиеся')
                print('fio: ', fio)

                get_id_by_user = DBManager().get_id_by_users(data=(self.group_selected, fio))[0][0]

                # Если изменения произошли в колонке ФИО 
                if col_name == 'Обучающиеся':
                    DBManager().edit_fio(data=(cmb_value.get(),  get_id_by_user))
                else:
                    # Если изменения произошли в колонках оценок 
                    marks_by_days: list = [self.tree3.set(iid, day) for day in range(1, 32)]
                    format_marks = ','.join(marks_by_days)
                    data = (format_marks, get_id_by_user)

                    month_translit_selected = MainWindow.get(self.month_selected, '')
                    DBManager().update_mark(month_translit=month_translit_selected, data=data)
                    
            self.update_widgets()
            cmb_value.destroy()
        
        # Горячие клавиши при различных действиях в режиме изменения значения в поле таблицы
        cmb_value.bind('<Return>', save_value)
        cmb_value.bind('<FocusOut>', lambda e: cmb_value.destroy())
        cmb_value.bind('<Escape>', lambda e: cmb_value.destroy())

# Главная функция
def main():
    db = DBManager().create_db()

    root = tk.Tk()
    root.iconbitmap('icon.ico')
    root.state('zoomed')
    root.title('Электронный дневник студента (ЭДС)')
    root.configure(bg='white')

    app = MainWindow(root)

    root.mainloop()

# Конструкция гарантирующая правильный запуск программы. Входная точка запуска программы.
if __name__ == '__main__':
    main()