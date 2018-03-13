import os
import sqlite3


class DBRecorder:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None
        self.fields = config['output']['content']

    def connect_db(self):
        path = os.path.expanduser(self.config['output']['dir'])
        if not os.path.exists(path):
            os.makedirs(path)
        self.conn = sqlite3.connect(os.path.join(path, self.config['output']['file_name']))
        if not self.conn:
            print('Fail to connect to sqlite db')
            exit(-1)

    def create_db_table(self):
        if not self.conn:
            self.connect_db()
        create_strs = []
        if 'hash' in self.fields:
            create_strs.append('hash text primary key not null')
        if 'summary' in self.fields:
            create_strs.append('summary text not null')
        if 'description' in self.fields:
            create_strs.append('description text')
        if 'date' in self.fields:
            create_strs.append('date text')
        if 'author' in self.fields:
            create_strs.append('author text')
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute('create table record({})'.format(','.join(create_strs)))
        except sqlite3.OperationalError:
            # table already exists, do nothing
            pass

    def add_db_record(self, row):
        if not self.conn:
            self.connect_db()
        question_marks = ['?' for _ in row.keys()]
        sql_str = 'insert into record({}) values ({})'.format(','.join(row.keys()), ','.join(question_marks))
        self.cursor.execute(sql_str, tuple(row.values()))
        self.conn.commit()

    def add_diff_record(self, diff):
        pass

    def close(self):
        self.cursor.close()
        self.conn.close()
