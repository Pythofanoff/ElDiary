# Валидация данных и проверка уникальных записей при записи в бд
# Проблема с названиями в два слова, в окнах добавления
# Оптимизация кода: уменьшение потребления ОЗУ, Hot Update данных при любом изменении и моментальная подгрузка с БД
# Добавить подсчёт процента успеваемости студента
# Добавить возможность удалять дисциплины 
# Добавить возможность описания и сводки всех данных о студенте (подробно), добавить эту фичу вниз таблицы
# Подсветка оценок (2 - красный, 3 - оранжевый, 4 - жёлтый, 5 - зелёный)
# Добавить разлиновку полей 

# Импорт всех нужных библиотек
import tkinter as tk
from tkinter import ttk, messagebox 
import sqlite3 


# Класс для работы с БД
class DBManager:
    # Глобальная переменная пути к файлу БД
    PATH = 'electronic_diary.db'

    # Метод создания бд и таблиц         
    def create_db(self):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            group_name TEXT NOT NULL,
            sep_month TEXT DEFAULT '',
            oct_month TEXT DEFAULT '',
            nov_month TEXT DEFAULT '',
            dec_month TEXT DEFAULT '',
            jan_month TEXT DEFAULT '',
            feb_month TEXT DEFAULT '',
            mar_month TEXT DEFAULT '',
            apr_month TEXT DEFAULT '',
            may_month TEXT DEFAULT '',
            jun_month TEXT NULL
            );
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS disciplines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            group_name TEXT NOT NULL);
            ''')

    # Метод добавления пользователей
    def add_user(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO students (
                fio, 
                group_name,
                sep_month,
                oct_month,
                nov_month,
                dec_month,
                jan_month,
                feb_month,
                mar_month,
                apr_month,
                may_month,
                jun_month
            ) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            ''', data)

    # Метод добавления дисциплины в БД
    def add_discipline(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO disciplines (name, group_name) VALUES (?, ?);
            ''', data)

    # Метод получения пользователей из БД
    def get_all_users(self, group_name, month_translit):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT id, fio, {month_translit} '
                f'FROM students '
                f'WHERE group_name = ?',
                (group_name[0],)
            )

        return cursor.fetchall()

    # Получение всех групп из БД
    def get_all_groups(self):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT DISTINCT group_name FROM students 
            ''')

        return cursor.fetchall()
    
    # Получение всех дисциплин из БД
    def get_all_disciplines(self):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT DISTINCT name FROM disciplines 
            ''')

        return cursor.fetchall()
    
    # Метод удаления пользователя
    def delete_user(self, data):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM students WHERE fio = ? AND group_name = ?', data)

    # Метод изменения ФИО в БД
    def edit_fio(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE students
                SET fio = ?
                WHERE id = ?;
            """, data)
    
    # Метод изменения оценки(ок) в БД
    def update_mark(self, month_translit, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(f'UPDATE students SET {month_translit} = ? WHERE id = ?;', data)

# Главный класс
class MainWindow(tk.Frame):
    # Инициализация важных компонентов 
    def __init__(self, root): 
        self.root = root 

        # Создание переменной для combobox'а 
        self.months = ['Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь', 'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь']
        self.month_var = tk.StringVar(self.root, value=self.months[0])
        self.month_selected = 'Сентябрь'
        
        # Создание переменной для combobox'а 
        self.disciplines = [*DBManager().get_all_disciplines(), 'Добавить дисциплину...']
        self.discipline_var = tk.StringVar(self.root, value=self.disciplines[0])
        self.discipline_selected = 'Добавить дисциплину...'

        # Создание переменной для combobox'а 
        self.mark = ['н\б', 2, 3, 4, 5]
        self.mark_var = tk.StringVar(value=self.mark[0])

        # Создание переменной для combobox'а 
        self.group = [*DBManager().get_all_groups(), 'Добавить группу...'] # + [''.join(*DBManager().get_all_groups().strip())] 
        self.group_var = tk.StringVar(value=self.group[0])
        self.group_selected = self.group[0]

        self.month_translit: dict = {
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

        self.month_translit_selected = self.month_translit.get(self.month_selected, '')

        self.data = DBManager().get_all_users(group_name=self.group_selected, month_translit=self.month_translit_selected)

        # Первоначальный запуск функций 
        self.init_filters()
        self.group_selected = self.cmb_month.get()
        self.init_scrollbar()
        self.init_tree()

        self.binds()

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
        dialog = tk.Toplevel(self.root)
        dialog.title('Добавление нового студента...')
        dialog.geometry('320x100')
        dialog.resizable(False, False)
        dialog.grab_set()

        frame1 = tk.Frame(dialog)
        frame1.pack(padx=4, fill='x')

        tk.Label(frame1, text='Введите нового студента: ').pack(side='left', padx=4)

        entry_add_user = ttk.Entry(frame1, width=25)
        entry_add_user.pack(padx=(3,0), pady=(5,5), side='left', anchor='e')
        entry_add_user.focus()

        frame2 = tk.Frame(dialog)
        frame2.pack(padx=4, fill='x')

        lbl = tk.Label(frame2, text='Введите группу: ')
        lbl.pack(side='left', padx=4)

        entry_add_group = ttk.Entry(frame2, width=25)
        entry_add_group.pack(padx=(5,0), pady=(5,5), side='right', anchor='e')
        entry_add_group.focus()

        def save(): 
            data = (entry_add_user.get().strip(), entry_add_group.get().strip()) + (','*30,)*10

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
        self.cmb_group.bind('<<ComboboxSelected>>', self.get_group)

        self.tree3.bind('<Button-1>', self.edit_value)
        
        self.root.bind('<Control-S>', self.update_widgets)
        self.root.bind('<Control-s>', self.update_widgets)
        self.root.bind('<Control-A>', self.add_students)
        self.root.bind('<Control-a>', self.add_students)
        self.root.bind('<Control-D>', self.delete_students)
        self.root.bind('<Control-d>', self.delete_students)

    # Вспомогательная метод для правильного закрытия окна
    def dismiss(self, window):
        window.grab_release() 
        window.destroy()

    def update_widgets(self, event=None):
        self.month_selected = self.month_var.get()
        self.discipline_selected = self.discipline_var.get()
        self.group_selected = self.group_var.get()

        self.month_translit_selected = self.month_translit.get(self.month_selected, '')
        self.data = DBManager().get_all_users(group_name=(self.cmb_group.get(),), month_translit=self.month_translit_selected)
        
        self.init_filters()
        self.init_scrollbar()
        self.init_tree()

        self.binds()

    # Получение месяца из combobox'а
    def get_month(self, event=None):
        self.month_selected = self.cmb_month.get()
        self.update_widgets()

    # Получение дисциплины из combobox'а
    def get_discipline(self, event=None):
        self.group_selected = self.cmb_discipline.get()

        if self.group_selected == 'Добавить дисциплину...':
            dialog = tk.Toplevel(self.root)
            dialog.title('Добавление новой дисциплины...')
            dialog.geometry('330x120')
            dialog.resizable(False, False)
            dialog.grab_set()

            frame = tk.Frame(dialog)
            frame.pack(fill='x')

            frame2 = tk.Frame(dialog)
            frame2.pack(fill='x')

            tk.Label(frame, text='Введите новую дисциплину: ').pack(side='left')

            entry_add_discipline = ttk.Entry(frame, width=25)
            entry_add_discipline.pack(padx=(5,0), pady=(5,3), side='left')
            entry_add_discipline.focus()

            tk.Label(frame2, text='Введите группу: ').pack(side='left')

            entry_group = ttk.Entry(frame2, width=25)
            entry_group.pack(padx=(0,5), pady=(3,4), side='right')

            def save_disciplines(event=None):
                new = entry_add_discipline.get().strip()
                group = entry_group.get()

                if new:
                    dialog.destroy()
                    self.disciplines.insert(0, new)

                    data: tuple = (new, group)
                    DBManager().add_discipline(data=data)
                    self.update_widgets()
                    
                    return

                if new in self.disciplines:
                    messagebox.showerror('Ошибка', 'Такая дисциплина уже существует', parent=dialog)
                    return

                self.disciplines.insert(0, new)
                dialog.destroy()
                self.cmb_discipline.set(new)
                self.update_widgets()

            entry_add_discipline.bind('<Return>', save_disciplines)
            entry_group.bind('<Return>', save_disciplines)
            ttk.Button(dialog, text='Добавить', command=save_disciplines).pack(side='bottom', pady=(0,2))

            self.root.wait_window(dialog)
        else:
            self.update_widgets()
    
    # Получение группы из combobox'а
    def get_group(self, event):
        self.group_selected = self.cmb_group.get()
        if self.group_selected == 'Добавить группу...':
            dialog = tk.Toplevel(self.root)
            dialog.title('Добавление новой группы...')
            dialog.geometry('300x120')
            dialog.resizable(False, False)
            dialog.grab_set()

            tk.Label(dialog, text='Введите новую группу: ').pack(side='left')

            entry_add_group = ttk.Entry(dialog, width=25)
            entry_add_group.pack(padx=(5,0), pady=(5,5), side='left')
            entry_add_group.focus()

            def save_group(event=None):
                new = entry_add_group.get().strip()
                if not new:
                    dialog.destroy()
                    self.cmb_group.set(self.group_selected if self.group_selected else (self.group[0] if self.group else ""))
                    return
                if new in self.group:
                    messagebox.showerror('Ошибка', 'Такая группа уже существует', parent=dialog)
                    return

                self.group.insert(0, new)
                dialog.destroy()
                self.cmb_group.set(new)
                self.update_widgets()

            entry_add_group.bind('<Return>', save_group)
            self.root.wait_window(dialog)
        else:
            self.update_widgets()

    # Инитиализация скроллбаров
    def init_scrollbar(self):
        try:
            self.scrl_bar.destroy()
            self.scrl_bar_horizont.destroy()
        except AttributeError:
            pass
            
        self.scrl_bar = tk.Scrollbar(self.root, orient='vertical')
        self.scrl_bar.pack(side='right', fill='y')
        
        self.scrl_bar_horizont = tk.Scrollbar(self.root, orient='horizontal')
        self.scrl_bar_horizont.pack(side='bottom', fill='x')

    # Инитиализация таблица (Дерева TreeView)
    def init_tree(self):
        try:
            self.tree1.destroy()
            self.tree3.destroy()
            self.tree2.destroy()
        except AttributeError:
            pass 

        # Treeview - 2 ()
        self.discipline: list = [self.discipline_selected]
        self.headings = ['discipline']

        self.tree2 = ttk.Treeview(self.root, columns=self.headings, show='headings', height=0)
        self.tree2.pack()

        for var, heading in zip(self.headings, self.discipline):
            self.tree2.heading(var, text=heading)
            self.tree2.column(var, stretch=True, width=1000)

        # Treeview - 1 ()
        self.columns: list = ['', self.month_selected, '']
        self.tree1 = ttk.Treeview(self.root, columns=self.columns, show='headings', height=0)
        self.tree1.pack(pady=(1,0), fill='both')

        for heading, column in zip(self.columns, self.columns):
            self.tree1.heading(heading, text=heading)


        # Treeview - 3 ()
        date = [str(_) for _ in range(1, 32)]
        self.date: list = ['№'] + ['Обучающиеся'] + date + ['Ср. балл'] + ['Процент успеваемости']
        self.headings: list = ['num', 'students', 'discipline', 'avgmarker', 'percentdo']

        self.tree3 = ttk.Treeview(self.root, columns=self.date, show='headings')
        self.tree3.pack(fill='both')
        self.scrl_bar.configure(command=self.tree3.yview)
        self.scrl_bar_horizont.configure(command=self.tree3.xview)
        self.tree3.configure(yscrollcommand=self.scrl_bar.set, xscrollcommand=self.scrl_bar_horizont.set)
        
        for heading in self.date:
            self.tree3.heading(heading, text=heading)
            self.tree3.column(heading, stretch=False, width=932)

        self.tree3.column('№', width=25)
        self.tree3.column('Обучающиеся', width=234)

        for date in date:
            self.tree3.column(date, width=25)

        self.tree3.column('Ср. балл', width=99)
        self.tree3.column('Процент успеваемости', width=214)

        data_format: list = [
            (
                self.data[i][0], 
                self.data[i][1], 
                *self.data[i][2].split(','),
                round(sum(float(x) for x in self.data[i][2].split(',') if x.isdigit()) / len(self.data[i][2].split(',')), 2),
                '0%'
            )
            for i in range(len(self.data))
        ]

        for data in data_format:
            self.tree3.insert('', tk.END, values=data)

    # Метод изменения значения в поле таблице
    def edit_value(self, event):
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
        
        if col_name != 'Обучающиеся':
            cmb_value = ttk.Combobox(textvariable=self.mark_var, values=self.mark)
            cmb_value.place(x=x, y=y, width=width+1, height=height, in_=self.tree3)
            cmb_value.focus()
        else:
            cmb_value = ttk.Entry()
            cmb_value.place(x=x, y=y, width=width, height=height, in_=self.tree3)
            cmb_value.focus()
            cmb_value.insert(0, values[col_indx])

        # Метод сохранения значения в поле таблицы
        def save_value(event=None):
            values[col_indx] = cmb_value.get()
            if cmb_value.get() == '' or cmb_value.get() == ' ':
                msg = messagebox.askyesno('Предупреждение', 'Вы стёрли информацию о студенте, вы хотите удалить этого студента из таблицы?')
                if msg:
                    iid = self.tree3.selection()
                    if iid:
                        val = self.group_var.get()
                        val2 = self.tree3.set(iid, 'Обучающиеся')

                    data = (val2, val)
                    print('data: ', data)
                    
                    DBManager().delete_user(data)
                    self.update_widgets()
                else:
                    return 

            if col_name not in non_editable_cols:
                self.tree3.item(item, values=values)
                iid = self.tree3.selection()
                id_iid = self.tree3.set(iid, '№')

                if col_name == 'Обучающиеся':
                    DBManager().edit_fio(data=(cmb_value.get(),  id_iid))
                else:
                    marks_by_days: list = [self.tree3.set(iid, day) for day in range(1, 32)]
                    format_marks = ','.join(marks_by_days)
                    data = (format_marks, id_iid)

                    month_translit_selected = self.month_translit.get(self.month_selected, '')
                    DBManager().update_mark(month_translit=month_translit_selected, data=data)

            cmb_value.destroy()
        
        # Горячие клавиши при различных действиях в режиме изменения значения в поле таблицы
        cmb_value.bind('<Return>', save_value)
        cmb_value.bind('<FocusOut>', lambda e: cmb_value.destroy())
        cmb_value.bind('<Escape>', lambda e: cmb_value.destroy())

# Главная функция main(). Входная точка запуска всей программы.
def main():
    db = DBManager().create_db()

    root = tk.Tk()
    root.state('zoomed')
    root.title('Электронный дневник студента (ЭДС)')
    root.configure(bg='white')

    app = MainWindow(root)

    root.mainloop()

# Конструкция гарантирующая правильный запуск программы 
if __name__ == '__main__':
    main()