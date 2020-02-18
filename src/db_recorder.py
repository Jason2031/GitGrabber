import os
import sqlite3


class DBRecorder:
    def __init__(self, report_dir):
        self.report_dir = report_dir
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        self.conn = None
        self.cursor = None

    def connect_db(self):
        self.conn = sqlite3.connect(os.path.join(self.report_dir, 'report.db'))
        self.cursor = self.conn.cursor()
        if not self.conn or not self.cursor:
            print('Fail to connect to sqlite db')
            exit(-1)

    def create_db_table_if_not_exists(self, table_name, field_string_set):
        if not self.conn:
            self.connect_db()
        try:
            self.cursor.execute('create table {}({})'.format(table_name, ','.join(field_string_set)))
        except sqlite3.OperationalError:
            # table already exists, do nothing
            pass

    def clear_table(self, table_name):
        if not self.conn:
            self.connect_db()
        try:
            self.cursor.execute('delete from {}'.format(table_name))
        except sqlite3.OperationalError:
            pass

    def add_db_record(self, row):
        if not self.conn:
            self.connect_db()
        question_marks = ['?' for _ in row.keys()]
        sql_str = 'insert into record({}) values ({})'.format(','.join(row.keys()), ','.join(question_marks))
        try:
            self.cursor.execute(sql_str, tuple(row.values()))
            self.conn.commit()
        except sqlite3.DatabaseError:
            # row already exists, do nothing
            pass

    def close(self):
        self.cursor.close()
        self.conn.close()
