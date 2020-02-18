import os
import shutil
import sqlite3


class KeywordFilter:
    def __init__(self, keywords, recorder, report_dir):
        self.conn = recorder.conn
        self.cursor = self.conn.cursor()
        self.keywords = {
            'first': keywords['first'],
            'second': keywords['second'] if 'second' in keywords.keys() else None
        }
        self.report_dir = report_dir

        self.keyword_first_result_dir = os.path.join(self.report_dir, 'diff_keyword_first')
        self.keyword_second_result_dir = os.path.join(self.report_dir, 'diff_keyword_second')

        field_string_set = {
            'hash text primary key not null',
            'parent_hash text not null',
            'summary text not null',
            'description text',
            'date text',
            'author text'
        }
        recorder.create_db_table_if_not_exists('keyword_first', field_string_set)
        recorder.create_db_table_if_not_exists('keyword_second', field_string_set)

    def filter_keyword(self, keyword_list, is_keyword_first):
        if is_keyword_first:
            if not os.path.exists(self.keyword_first_result_dir):
                os.makedirs(self.keyword_first_result_dir)
        else:
            if not os.path.exists(self.keyword_second_result_dir):
                os.makedirs(self.keyword_second_result_dir)

        commit_count = 0
        for keyword in keyword_list:
            if keyword is None:
                keyword = 'null'
            result = self.filter(keyword, is_keyword_first=is_keyword_first)

            print('Saving records for keyword `{}` to table {}...'.format(
                'keyword_first' if is_keyword_first else 'keyword_second', keyword))
            for item in result:
                self.add_db_record(item, is_keyword_first=is_keyword_first)
                commit_count += 1
                print('{}/{}'.format(commit_count, len(result)))
            print('Done saving records for keyword `{}`'.format(keyword))

    def filter(self, like_what, is_keyword_first=True):
        if is_keyword_first:
            from_table = 'restrict'
            to_table = 'keyword_first'
        else:
            from_table = 'keyword_first'
            to_table = 'keyword_second'
        print('Start filtering from table {} to table {} with keyword `{}`'.format(from_table, to_table, like_what))

        assert type(like_what) is str
        like_str = '"%{}%"'.format('%'.join(like_what.split(' ')))
        filter_str = 'select * from {} where summary like {}'.format(
            'record' if is_keyword_first else 'keyword_first', like_str)
        result = self.cursor.execute(filter_str)
        result_list = []

        for row in result:
            record = {}
            for i in range(len(result.description)):
                record[result.description[i][0]] = row[i]
            if 'hash' in record.keys():
                if is_keyword_first:
                    source_dir = os.path.join(self.report_dir, 'diff_restrict', record['hash'])
                    dest_dir = os.path.join(self.keyword_first_result_dir, record['hash'])
                else:
                    source_dir = os.path.join(self.keyword_first_result_dir, record['hash'])
                    dest_dir = os.path.join(self.keyword_second_result_dir, record['hash'])
                try:
                    if os.path.exists(source_dir):
                        shutil.copytree(source_dir, dest_dir)
                except FileExistsError:
                    pass
            result_list.append(record)

        print('Done with keyword `{}` from T. {} to T. {}'.format(like_what, from_table, to_table))
        return result_list

    def add_db_record(self, row, is_keyword_first=True):
        assert row is not None and type(row) is dict
        assert self.cursor is not None
        question_marks = ['?' for _ in row.keys()]
        table_name = 'keyword_first' if is_keyword_first else 'keyword_second'
        sql_str = 'insert into {}({}) values ({})'.format(table_name, ','.join(row.keys()), ','.join(question_marks))
        try:
            self.cursor.execute(sql_str, tuple(row.values()))
            self.conn.commit()
        except sqlite3.DatabaseError:
            # row already exists, do nothing
            pass
