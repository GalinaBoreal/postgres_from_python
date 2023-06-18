import os
import psycopg2
from psycopg2.extensions import AsIs
from dotenv import load_dotenv

load_dotenv()


class ConnectDB:

    def __init__(self):
        self.info_db = {"database": "client_db",
                        "user": "postgres",
                        "host": "localhost",
                        "password": os.getenv('PASSWORD')}
        self.conn = psycopg2.connect(**self.info_db)
        self.cursor = self.conn.cursor()

    def execute(self, fill):
        self.cursor.execute(fill)
        self.conn.commit()
        print(self.cursor.statusmessage)

    def execute_safity(self, fill, safe):
        self.cursor.execute(fill, safe)
        self.conn.commit()
        print(self.cursor.statusmessage)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchmany(self, number):
        return self.cursor.fetchmany(number)

    def fetchall(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()


class Use:
    def __init__(self):
        self.cursor = ConnectDB()

    def create_table_from_file(self):
        """Создание таблиц чтением файла create_table.sql"""
        try:
            self.cursor.execute(open("create_table.sql", "r").read())
        except (Exception, psycopg2.DatabaseError):
            print('Что-то пошло не так')

    def add_from_file(self):
        """Добавление данных в таблицы чтением файла insert_table.sql"""
        try:
            self.cursor.execute(open("insert_table.sql", "r", encoding='utf-8').read())
        except (Exception, psycopg2.DatabaseError):
            print('Что-то пошло не так')

    def create_table(self):
        """Создание таблиц написанием create-запроса"""
        try:
            fill = """CREATE TABLE IF NOT EXISTS Client(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR (30) NOT NULL,
            last_name VARCHAR (30) NOT NULL,
            email VARCHAR (30) NOT NULL UNIQUE CONSTRAINT check_email CHECK (email like '%@%')
            );
            CREATE TABLE IF NOT EXISTS Phone(
            id SERIAL PRIMARY KEY,
            number_phone INTEGER UNIQUE NOT NULL,
            client_id INTEGER REFERENCES Client(id) not null
            );
            """
            self.cursor.execute(fill)
        except (Exception, psycopg2.DatabaseError):
            print('Что-то пошло не так')

    def add_client(self, client_id, first_name, last_name, email):
        """Добавление данных в таблицу Client написаниеем insert-запроса"""
        try:
            fill = """INSERT INTO Client(id, first_name, last_name, email)
            VALUES(%s, %s, %s, %s);"""
            safe = (int(client_id), str(first_name), str(last_name), str(email))
            self.cursor.execute_safity(fill, safe)
        except (Exception, psycopg2.DatabaseError):
            print('Введены неверные данные или что-то пошло не так')

    def add_phone(self, phone_id, number_phone, client_id):
        """Добавление данных в таблицу Phone написаниеем insert-запроса"""
        try:
            fill = """INSERT INTO Phone(id, number_phone, client_id)
            VALUES(%s, %s, %s);"""
            safe = (int(phone_id), int(number_phone), int(client_id))
            self.cursor.execute_safity(fill, safe)
        except (Exception, psycopg2.DatabaseError):
            print('Возможно, это телефон не существующего клиента, либо введены неверные данные')

    def update(self, table, change_column, new_data, defines_column, defines_data):
        """Изменение данных любой таблицы по любому параметру"""
        try:
            fill = """UPDATE %s SET %s = %s WHERE %s = %s;"""
            safe = (AsIs(table), AsIs(change_column), new_data, AsIs(defines_column), defines_data)
            self.cursor.execute_safity(fill, safe)
        except (Exception, psycopg2.DatabaseError):
            print('Введены неверные данные или что-то пошло не так')

    def delete(self, table, defines_column, defines_data):
        """Удаление данных любой таблицы по любому параметру"""
        try:
            fill = """DELETE FROM %s WHERE %s = %s;"""
            safe = (AsIs(table), AsIs(defines_column), defines_data)
            self.cursor.execute_safity(fill, safe)
        except (Exception, psycopg2.DatabaseError):
            print('Либо нужно вначале удалить телефон, либо введены неверные данные')

    def search_by_one(self, table, defines_column, search_data):
        """Поиск клиента по одному аргументу с указанием таблицы поиска"""
        try:
            fill = """SELECT Client.id, Client.first_name, Client.last_name, Phone.number_phone
            FROM Client
            JOIN Phone ON Phone.client_id = Client.id
            WHERE %s.%s = %s;"""
            safe = (AsIs(table), AsIs(defines_column), search_data)
            self.cursor.execute_safity(fill, safe)
            print(self.cursor.fetchall())
        except (Exception, psycopg2.DatabaseError):
            print('Введены неверные данные или что-то пошло не так')

    def search(self, first_name=None, last_name=None, email=None, number_phone=None, client_id=None):
        """Поиск клиента по любым данным"""
        if first_name is None and last_name is None and email is None and number_phone is None and client_id is None:
            print('Вы не ввели ни одного аргумента')
            return

        fill = 'SELECT c.id, c.first_name, c.last_name, p.number_phone FROM Client AS c JOIN Phone AS p ON ' \
               'p.client_id = c.id'
        v_safe = []
        v_count = 0
        v_str = ''

        if first_name is not None:
            v_safe.append(first_name)
            v_str = 'c.first_name = %s '
            v_count = 1

        if last_name is not None:
            v_safe.append(last_name)
            if v_count == 0:
                v_str = 'c.last_name = %s '
                v_count = 1
            else:
                v_str = v_str + ' AND c.last_name = %s '
                v_count += 1

        if email is not None:
            v_safe.append(email)
            if v_count == 0:
                v_str = 'c.email = %s '
                v_count = 1
            else:
                v_str = v_str + ' AND c.email = %s '
                v_count += 1

        if number_phone is not None:
            v_safe.append(number_phone)
            if v_count == 0:
                v_str = 'p.number_phone = %s '
                v_count += 1
            else:
                v_str = v_str + ' AND p.number_phone = %s '
                v_count += 1

        if v_str != '':
            fill = fill + ' WHERE ' + v_str
        fill = fill + ';'
        safe = tuple(v_safe)
        try:
            self.cursor.execute_safity(fill, safe)
            print(self.cursor.fetchall())
        except (Exception, psycopg2.DatabaseError):
            print('Введены неверные данные или что-то пошло не так')

    def __del__(self):
        self.cursor.close()

if __name__ == "__main__":
    data = Use()

    # # создание таблиц напрямую
    # data.create_table()

    # создание таблиц из файла
    data.create_table_from_file()

    # заполнение таблиц из файла
    data.add_from_file()

    # заполнение таблиц напрямую
    data.add_client('4', 'Анастасия', 'Петрова', 'sun@yandex.ru')
    data.add_phone('4', '113311', '3')

    # изменение данных
    data.update('Client', 'first_name', 'Александр', 'id', 1)
    data.update('Client', 'email', 'ivanova-1989@mail.ru', 'last_name', 'Иванова')
    data.update('Phone', 'number_phone', '332233', 'number_phone', 223322)
    data.update('Client', 'last_name', 'Петрова', 'email', 'ivanova-1989@mail.ru')

    # поиск клиента по однному аргументу
    data.search_by_one('Client', 'id', 3)
    data.search_by_one('Client', 'first_name', 'Александр')
    data.search_by_one('Phone', 'number_phone', 224422)

    # поиск клиента по любому параменту
    data.search(first_name='Александр', number_phone=224422)
    data.search(first_name='Александр')
    data.search()

    # удаление клиента или телефона
    data.delete('Client', 'id', 4)
    data.delete('Phone', 'number_phone', 332233)
    data.delete('Client', 'id', 3)
