import argparse
import os

import yaml
from git import Repo

from Recorder import DBRecorder

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grab useful message from git repository')
    parser.add_argument('--config',
                        dest='config_file',
                        help='location of config.yml file',
                        default='./config.yml',
                        type=str)
    args = parser.parse_args()
    if not os.path.exists(args.config_file):
        print('No such config file!')
        exit(-1)
    config = None
    with open(args.config_file) as f:
        config = yaml.load(f.read())
    recorder = DBRecorder(config)
    recorder.create_db_table()
    repo = Repo(config['working_dir'])
    print(repo)
