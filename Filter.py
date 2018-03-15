import argparse
import sqlite3

import yaml

from Recorder import DBRecorder


class DBFilter:
    def __init__(self, config, db_conn):
        self.config = config
        self.conn = db_conn
        self.cursor = self.conn.cursor()
        self.fields = config['output']['content']
        self.keywords = {
            'first': config['filter']['key_words']['first'],
            'second': config['filter']['key_words']['second'] if 'second' in config['filter']['key_words'].keys()
            else None
        }

    def create_db(self):
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
        try:
            self.cursor.execute('create table mid({})'.format(','.join(create_strs)))
            self.cursor.execute('create table result({})'.format(','.join(create_strs)))
        except sqlite3.OperationalError:
            # table already exists, do nothing
            pass

    def filter(self, like_what, from_mid=False):
        assert type(like_what) is str
        if from_mid:
            filter_str = 'select * from mid where summary like "%{}%"'
        else:
            filter_str = 'select * from record where summary like "%{}%"'
        result = self.cursor.execute(filter_str.format(like_what))
        result_list = []
        for row in result:
            record = {}
            for i in range(len(result.description)):
                record[result.description[i][0]] = row[i]
            result_list.append(record)
        return result_list

    def add_db_record(self, row, is_final_result=True):
        assert row is not None and type(row) is dict
        assert self.cursor is not None
        question_marks = ['?' for _ in row.keys()]
        if is_final_result:
            sql_str = 'insert into result({}) values ({})'.format(','.join(row.keys()), ','.join(question_marks))
        else:
            sql_str = 'insert into mid({}) values ({})'.format(','.join(row.keys()), ','.join(question_marks))
        try:
            self.cursor.execute(sql_str, tuple(row.values()))
            self.conn.commit()
        except sqlite3.DatabaseError:
            # row already exists, do nothing
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grab useful message from git repository')
    parser.add_argument('--config',
                        dest='config_file',
                        help='location of config.yml file',
                        default='./config.yml',
                        type=str)
    args = parser.parse_args()
    config_file = None
    with open(args.config_file) as f:
        config_file = yaml.load(f.read())

    db_recorder = DBRecorder(config_file)
    db_recorder.connect_db()

    db_filter = DBFilter(config_file, db_recorder.conn)
    db_filter.create_db()

    commit_count = 0
    for first_level_keyword in config_file['filter']['key_words']['first']:
        filter_result = db_filter.filter(first_level_keyword, from_mid=False)
        for item in filter_result:
            db_filter.add_db_record(item, is_final_result=False)
            commit_count += 1
            print(commit_count)

    commit_count = 0
    for second_level_keyword in config_file['filter']['key_words']['second']:
        filter_result = db_filter.filter(second_level_keyword, from_mid=True)
        for item in filter_result:
            db_filter.add_db_record(item, is_final_result=True)
            commit_count += 1
            print(commit_count)

    db_recorder.close()
    print('All done!')
