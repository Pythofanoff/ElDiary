import sqlite3
from datetime import datetime


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
            group_name TEXT NOT NULL
            );
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS disciplines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                group_name TEXT NOT NULL);
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                discipline_id INTEGER NOT NULL,
                sep_month TEXT DEFAULT '',
                oct_month TEXT DEFAULT '',
                nov_month TEXT DEFAULT '',
                dec_month TEXT DEFAULT '',
                jan_month TEXT DEFAULT '',
                feb_month TEXT DEFAULT '',
                mar_month TEXT DEFAULT '',
                apr_month TEXT DEFAULT '',
                may_month TEXT DEFAULT '',
                jun_month TEXT NULL,
                date TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (discipline_id) REFERENCES disciplines(id));
            ''')

    # Метод добавления пользователей
    def add_user(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO students (
                fio, 
                group_name
            ) 
            VALUES (?, ?);
            ''', data)

    # Метод добавления дисциплины в БД
    def add_discipline(self, data: tuple):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            INSERT INTO disciplines (name, group_name) VALUES (?, ?);
            ''', data)

    def save_or_update_grade(self, student_id, discipline_id, grade, month_translit):
        conn = sqlite3.connect(self.PATH)
        cursor = conn.cursor()

        # Проверяем, есть ли уже оценка для этого студента по данной дисциплине
        cursor.execute('''
            SELECT id FROM grades WHERE student_id=? AND discipline_id=?
        ''', (student_id, discipline_id))
        result = cursor.fetchone()

        if result:
            # Если есть — обновляем оценку
            cursor.execute(f'''
                UPDATE grades SET {month_translit}=?, date=? WHERE id=?
            ''', (grade, datetime.now().strftime('%Y-%m-%d'), result[0]))
        else:
            # Если нет — вставляем новую
            cursor.execute(f'''
                INSERT INTO grades (student_id, discipline_id, {month_translit}, date)
                VALUES (?, ?, ?, ?)
            ''', (student_id, discipline_id, grade, datetime.now().strftime('%Y-%m-%d')))
        
        conn.commit()
        conn.close()

    def get_marks_by_id(self, student_id, month_translit):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT {month_translit} '
                f'FROM grades '
                f'WHERE student_id = ?',
                (student_id,)
            )

        return cursor.fetchall()

    def get_discipline_id(self, discipline, group):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT id '
                f'FROM disciplines '
                f'WHERE group_name = ? AND name = ?',
                (group, discipline)
            )

        return cursor.fetchone()

    # Метод получения пользователей из БД
    def get_all_users(self, group_name):
        with sqlite3.connect(DBManager.PATH) as conn:
            cursor = conn.cursor()

            cursor.execute(
                f'SELECT id, fio '
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
                f'WHERE group_name = ?',
                (data,)
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
