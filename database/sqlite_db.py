import sqlite3
from .tables import query_tables, query_users, query_spaces


class Database():
    '''Класс БД SQLite'''

    def __init__(self, db_name):
        '''Метод инициализации'''
        self.query_users = query_users
        self.query_tables = query_tables
        self.query_spaces = query_spaces
        self.conn = sqlite3.connect(db_name)  #Устанавливаем связь с бд
        self.cur = self.conn.cursor()
        self.execute_new(self.query_users)
        self.execute_new(self.query_tables)
        self.execute_new(self.query_spaces)

    def execute(self, query, params):
        '''Метод выполнения SQL-запросов'''
        self.cur.execute(query, params)
        self.conn.commit()

    def execute_new(self, query):
        '''Метод выполнения SQL-запросов'''
        self.cur.execute(query)
        self.conn.commit()

    def commit(self):
        '''Метод сохранения изменений'''
        self.conn.commit()

    def close(self):
        '''Метод закрытия соединения с базой данных'''
        self.conn.close()

    def get_all(self, table_name):
        '''Метод получения всех записей из таблицы'''
        self.execute(f"SELECT * FROM {table_name}")
        return self.cur.fetchall()

    def get_table_ids(self, tg_id):
        ''' Метод получения ID доски'''
        self.execute(f"SELECT KAITEN_BOARD_ID \
                     FROM tables \
                     WHERE TG_ID = ?",
                    (tg_id, ))
        return self.cur.fetchall()
    
    def get_space_ids(self, tg_id):
        ''' Метод получения ID пространства'''
        self.execute(f"SELECT KAITEN_SPACE_ID \
                     FROM spaces \
                     WHERE TG_ID = ?",
                    (tg_id, ))
        return self.cur.fetchall()

    def add_table(self, tg_id, board_id):
        ''' Метод добавления доски'''
        self.execute(f'INSERT \
                     INTO tables (TG_ID, KAITEN_BOARD_ID) \
                     VALUES (?, ?)', 
                    (tg_id, board_id, ))
    
    def add_space(self, tg_id, space_id):
        ''' Метод добавления пространства'''
        self.execute(f'INSERT \
                     INTO spaces (TG_ID, KAITEN_SPACE_ID) \
                     VALUES (?, ?)', 
                    (tg_id, space_id, ))

    def remove_table(self, tg_id, board_id):
        ''' Метод удаление доски'''
        self.execute(f'DELETE \
                    FROM tables \
                    WHERE TG_ID = ? \
                    AND KAITEN_BOARD_ID = ?', 
                    (tg_id, board_id, ))
        
    def remove_space(self, tg_id, space_id):
        ''' Метод удаление доски'''
        self.execute(f'DELETE \
                    FROM spaces \
                    WHERE TG_ID = ? \
                    AND KAITEN_SPACE_ID = ?', 
                    (tg_id, space_id, ))

    def get_api_key(self, tg_id):
        '''Метод добавления api ключа'''
        self.execute(f'SELECT KAITEN_API \
                     FROM users \
                     WHERE TG_ID = ?',
                    (tg_id, ))
        return self.cur.fetchone()

    def get_domain(self, tg_id):
        '''Метод добавления домена'''
        self.execute(f'SELECT KAITEN_DOMAIN \
                     FROM users \
                     WHERE TG_ID = ?',
                    (tg_id, ))
        return self.cur.fetchone()

    def add_record(self, table_name: str, record):
        '''Метод добавления записи в таблицу'''
        placeholders = ', '.join(['?' for _ in range(len(record))])
        self.execute(f"INSERT \
                    INTO {table_name} (TG_ID, KAITEN_API, KAITEN_DOMAIN, STATUS, NAME) \
                    VALUES ({placeholders})",
                    record)

    def add_api_kaiten(self, api_key: str, tg_id: int):
        ''' Метод обновления api ключа'''
        self.execute(f"UPDATE users \
                     SET KAITEN_API = ? \
                     WHERE TG_ID = ?", 
                    (api_key, tg_id, ))

    def add_domain_kaiten(self, domain: str, tg_id: int):
        ''' Метод обновления токена'''
        self.execute(f"UPDATE users \
                     SET KAITEN_DOMAIN = ? \
                     WHERE TG_ID = ?", 
                    (domain, tg_id, ))

    def check_user(self, TG_ID: int, table: str) -> bool:
        '''Проверяем есть ли такой пользователь'''
        with self.conn:
            return bool(
                len(
                    self.cur.execute(f"SELECT * \
                                     FROM '{table}' \
                                     WHERE TG_ID = ?",
                                    (TG_ID, )).fetchall()))

    def check_api(self, TG_ID: int, table: str) -> bool:
        '''Проверяем есть ли запись в таблице'''
        with self.conn:
            return not str(
                self.cur.execute(f"SELECT KAITEN_API \
                                FROM '{table}' \
                                WHERE TG_ID = ?",
                                (TG_ID, )).fetchone()[0]) == 'token'

    def check_domain(self, TG_ID: int, table: str) -> bool:
        '''Проверяем есть ли запись в таблице'''
        with self.conn:
            return not str(
                self.cur.execute(f"SELECT KAITEN_DOMAIN \
                                 FROM '{table}' \
                                 WHERE TG_ID = ?",
                                (TG_ID, )).fetchone()[0]) == 'token'
