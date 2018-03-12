import os
import sqlite3


class DBRecorder:
    def __init__(self, config):
        self.config = config
        self.conn = None
        self.cursor = None
        self.fields = config['output']['content']

    def connect_db(self):
        if not os.path.exists(self.config['output']['dir']):
            os.makedirs(self.config['output']['dir'])
        conn = sqlite3.connect(os.path.join(self.config['output']['dir'], self.config['output']['file_name']))
        if not conn:
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
        self.cursor.execute('create table record({})'.format(','.join(create_strs)))

    def add_record(self, row):
        if not self.conn:
            self.connect_db()
        assert row is dict
        question_marks = ['?' for _ in row.keys()]
        self.cursor.execute('insert into record({}) values ({})'.format(row.keys(), ','.join(question_marks)),
                            row.values())
