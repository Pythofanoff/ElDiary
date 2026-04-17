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


    # Метод получения id пользователя по группе и фио
    def get_id_by_users(self, data):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT id '
                f'FROM students '
                f'WHERE group_name = ? AND fio = ?',
                data
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
            SELECT group_name, name FROM disciplines 
            ''')

        return cursor.fetchall()

    # Метод удаления пользователя
    def delete_user(self, data):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM students WHERE fio = ? AND group_name = ?', data)

    # Метод удаления дисциплин
    def delete_discipline(self, data):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM disciplines WHERE name = ? AND group_name = ?', data)

    # Метод изменения ФИО в БД
    def edit_fio(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE students
                SET fio = ?
                WHERE id = ?;
            """, data)
    
    # Метод изменения названия дисциплины в БД
    def edit_discipline(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE disciplines
                SET name = ?
                WHERE name = ?;
            """, data)

    # Метод изменения оценки(ок) в БД
    def update_mark(self, month_translit, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(f'UPDATE students SET {month_translit} = ? WHERE id = ?;', data)

    def get_count_students_group(self, data):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM students WHERE group_name = ?', (data,))

        return cursor.fetchall()
