import tkinter as tk

from dbmanager import DBManager
from window import MainWindow


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
