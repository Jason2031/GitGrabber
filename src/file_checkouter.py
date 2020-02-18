import argparse
import json
import os

from git import Repo


class FileCheckOuter:
    def __init__(self, repo):
        assert repo

        repo = os.path.abspath(os.path.expanduser(repo))
        if not os.path.exists(os.path.join(repo, '.git')):
            print('No .git folder found in {}!'.format(repo))
            exit(-1)
        self.repo = Repo(repo)
        self.git = self.repo.git

    def start_checking_out(self, input_dir):
        assert input_dir

        input_dir = os.path.abspath(os.path.expanduser(input_dir))
        if not os.path.exists(input_dir):
            print('`{}` does not exist!'.format(input_dir))
            return

        print('Start checking out old and new versions of files in {}...'.format(input_dir))
        num = 1
        diff_folders = os.listdir(input_dir)
        for diff_folder in diff_folders:
            diff_folder = os.path.join(input_dir, diff_folder)

            des_loc = os.path.join(diff_folder, 'description.txt')
            if not os.path.exists(des_loc):
                continue
            with open(des_loc) as f:
                description = json.loads(f.read())
            this_hash = description['hash']

            if 'parent_hash' not in description.keys():
                continue
            parent_hash = description['parent_hash']

            changed_files = [file_name[:-5].replace('\\', '/') for file_name in os.listdir(diff_folder) if
                             file_name.endswith('.diff')]
            this_tree = self.repo.tree(this_hash)
            parent_tree = self.repo.tree(parent_hash)

            for changed_file in changed_files:
                name, ext = os.path.splitext(changed_file)
                try:
                    fixed_file_name = '{}_fixed{}'.format(name, ext).replace('/', '\\')
                    fixed_file_name = os.path.join(diff_folder, fixed_file_name)
                    if not os.path.exists(fixed_file_name):
                        fixed_file = this_tree[changed_file]
                        fixed_file.stream_data(open(fixed_file_name, 'wb'))
                except ValueError:
                    pass
                except KeyError:
                    pass  # no this file found in fix tree

                try:
                    parent_file_name = changed_file.replace('/', '\\')
                    parent_file_name = os.path.join(diff_folder, parent_file_name)
                    if not os.path.exists(parent_file_name):
                        parent_file = parent_tree[changed_file]
                        parent_file.stream_data(open(parent_file_name, 'wb'))
                except ValueError:
                    pass
                except KeyError:
                    pass  # no this file found in parent tree
                print('{} {}'.format(num, changed_file))
                num += 1


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo_dir', dest='repo_dir', default=None, type=str,
                        help='location of the directory that contains .git file')
    parser.add_argument('--input_dir', dest='input_dir', default=None, type=str,
                        help='directory that contains commit messages')
    return parser.parse_args()


def main():
    args = get_args()

    checkouter = FileCheckOuter(args.repo_dir)
    checkouter.start_checking_out(args.input_dir)


if __name__ == '__main__':
    main()
