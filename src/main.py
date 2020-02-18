import argparse
import os
import shutil

import yaml

from db_recorder import DBRecorder
from file_checkouter import FileCheckOuter
from file_filter import FileFilter
from keyword_filter import KeywordFilter
from repo_extractor import RepoExtractor


def get_args():
    parser = argparse.ArgumentParser(description='Grab useful message from git repository')
    parser.add_argument('--config',
                        dest='config_file',
                        help='location of config.yml file',
                        default='../config/openssl_config.yml',
                        type=str)
    parser.add_argument('--skip_restrict',
                        dest='skip_restrict',
                        help='whether to skip commit_count, from_date, to_date restrictions in config file',
                        default=False,
                        type=bool)
    parser.add_argument('--skip_first_keywords',
                        dest='skip_first_keywords',
                        help='whether to skip first layer of keywords filtering',
                        default=False,
                        type=bool)
    parser.add_argument('--skip_second_keywords',
                        dest='skip_second_keywords',
                        help='whether to skip second layer of keywords filtering',
                        default=False,
                        type=bool)
    return parser.parse_args()


def main():
    args = get_args()

    if not os.path.exists(args.config_file):
        print('No such config file!')
        exit(-1)

    with open(args.config_file) as f:
        config = yaml.load(f.read())

    working_dir = os.path.abspath(os.path.expanduser(config['working_dir']))
    if not os.path.exists(working_dir):
        print('No such working directory!')
        exit(-1)

    report_dir = os.path.join(working_dir, '.gitgrabber_report')
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)

    recorder = DBRecorder(report_dir)
    recorder.connect_db()

    extract_result_dir = os.path.join(report_dir, 'diff_restrict')
    if not args.skip_restrict or not os.path.exists(extract_result_dir):
        shutil.rmtree(extract_result_dir, ignore_errors=True)
        recorder.clear_table('record')

        extractor = RepoExtractor(
            repo_location=config['working_dir'],
            branch_name=config['filter']['branch'],
            from_date=config['filter']['restrict']['from_date'],
            to_date=config['filter']['restrict']['to_date'],
            commit_count_limit=int(config['filter']['restrict']['commit_count']),
            number_of_files=config['filter']['restrict']['NOF'],
            recorder=recorder,
            report_dir=report_dir
        )
        extractor.start_extracting()

    if config['checkout']:
        checkouter = FileCheckOuter(config['working_dir'])
        checkouter.start_checking_out(extract_result_dir)

    keyword_map = config['filter']['keywords']
    db_filter = KeywordFilter(
        keywords=keyword_map,
        recorder=recorder,
        report_dir=report_dir
    )

    keyword_first_dir = os.path.join(report_dir, 'diff_keyword_first')
    if not args.skip_first_keywords or not os.path.exists(keyword_first_dir):
        shutil.rmtree(keyword_first_dir, ignore_errors=True)
        recorder.clear_table('keyword_first')
        db_filter.filter_keyword(keyword_map['first'], is_keyword_first=True)

    keyword_second_dir = os.path.join(report_dir, 'diff_keyword_second')
    if not args.skip_second_keywords or not os.path.exists(keyword_second_dir):
        shutil.rmtree(keyword_second_dir, ignore_errors=True)
        recorder.clear_table('keyword_second')
        db_filter.filter_keyword(keyword_map['second'], is_keyword_first=False)

    file_filter = FileFilter(
        report_dir=report_dir,
        lines_of_code=config['filter']['LOC'],
        discard_file_name_list=config['filter']['discard_file_names'],
        ignore_case=config['filter']['ignore_case']
    )
    file_filter.start_filtering()

    recorder.close()
    print('All done!')


if __name__ == '__main__':
    main()
