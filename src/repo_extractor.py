import datetime
import json
import os

from git import Repo, GitCommandError, NULL_TREE


class RepoExtractor:
    def __init__(self, repo_location, branch_name, from_date, to_date,
                 commit_count_limit, number_of_files, recorder, report_dir):
        self.repo = Repo(repo_location)
        self.branch_name = branch_name
        self.from_date = datetime.datetime.strptime(
            '1970-01-01' if from_date == -1 else str(from_date), '%Y-%m-%d')
        self.to_date = datetime.datetime.strptime(
            str(datetime.date.today() + datetime.timedelta(days=1)) if to_date == -1 else str(to_date), '%Y-%m-%d')
        self.commit_count_limit = commit_count_limit
        self.number_of_files = number_of_files
        self.recorder = recorder
        self.diff_restrict_dir = os.path.join(report_dir, 'diff_restrict')
        self.page_size = 100

        field_string_set = {
            'hash text primary key not null',
            'parent_hash text not null',
            'summary text not null',
            'description text',
            'date text',
            'author text'
        }
        self.recorder.create_db_table_if_not_exists('record', field_string_set)

    def start_extracting(self):
        can_continue = True
        skip = 0
        commit_count = 0

        print('Start extracting...')
        while can_continue:
            try:
                commit_page = list(self.repo.iter_commits(self.branch_name, max_count=self.page_size, skip=skip))
            except GitCommandError:
                print('No such branch or other error(s) happened.')
                exit(-1)

            last_commit_in_page = commit_page[-1]
            if last_commit_in_page.committed_datetime.replace(tzinfo=None) > self.to_date:
                skip += len(commit_page)
                continue
            for commit in commit_page:
                if self.commit_count_limit == -1 or commit_count < self.commit_count_limit:
                    commit_date = commit.committed_datetime.replace(tzinfo=None)
                    if commit_date > self.to_date:
                        continue

                    if self.from_date <= commit_date:
                        record = {
                            'hash': commit.hexsha,
                            'summary': commit.summary,
                            'description': commit.message,
                            'date': str(commit_date),
                            'author': commit.author.name
                        }

                        parents = commit.parents
                        if len(parents) > 1:
                            # not tested
                            sorted_parents = sorted(parents, key=lambda x: x.committed_datetime)
                            latest = sorted_parents[-1]
                            diffs = latest.diff(commit, create_patch=True)
                            record['parent_hash'] = latest.hexsha
                        elif len(parents) == 1:
                            diffs = parents[0].diff(commit, create_patch=True)
                            record['parent_hash'] = parents[0].hexsha
                        else:
                            diffs = commit.diff(NULL_TREE, create_patch=True)

                        if self.number_of_files < 0 or len(diffs) > self.number_of_files:
                            continue

                        diff_dir = os.path.join(self.diff_restrict_dir, commit.hexsha)
                        for diff in diffs:
                            if not os.path.exists(diff_dir):
                                os.makedirs(diff_dir)

                            file_name = diff.b_path if diff.a_path is None else diff.a_path
                            with open(os.path.join(diff_dir, file_name.replace('/', '\\') + '.diff'), 'w') as f:
                                f.write(str(diff))
                        with open(os.path.join(diff_dir, 'description.txt'), 'w') as f:
                            f.write(json.dumps(record, indent=4))

                        commit_count += 1
                        self.recorder.add_db_record(record)
                    else:
                        can_continue = False
                        break
                else:
                    can_continue = False
                    break
                print('{} [{}][{}]'.format(commit_count, record['date'], record['summary']))
            if len(commit_page) == 0:
                break
            skip += len(commit_page)
        print('Done extracting ...')
