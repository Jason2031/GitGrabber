import codecs
import os
import re
import shutil

diff_pattern = re.compile('@@ -\d+,\d+ \+\d+,(\d+) @@')


class FileFilter:
    def __init__(self, report_dir, lines_of_code, discard_file_name_list, ignore_case):
        self.report_dir = report_dir
        self.final_dir = os.path.join(self.report_dir, 'diff_final')
        self.LOC = lines_of_code
        self.discard_file_name_list = discard_file_name_list
        self.ignore_case = ignore_case
        self.discard_file_name_re = [re.compile('[\s\S]*{}[\s\S]*'.format(name), re.I if self.ignore_case else 0)
                                     for name in discard_file_name_list]
        if not os.path.exists(self.final_dir):
            os.makedirs(self.final_dir)

    def start_filtering(self):
        filter_folder = os.path.join(self.report_dir, 'diff_keyword_second')
        if not os.path.exists(filter_folder):
            filter_folder = os.path.join(self.report_dir, 'diff_keyword_first')
        if not os.path.exists(filter_folder):
            print('No diff_result record, filter diff_restrict? (y/n)')
            raw_input = input()
            while raw_input != 'y' or raw_input != 'n' or raw_input != 'yes' or raw_input != 'no':
                print('Wrong input, try again. (y/n)')
                raw_input = input()
            if raw_input == 'n' or raw_input == 'no':
                print('Goodbye!')
                exit(0)
            else:
                filter_folder = os.path.join(self.report_dir, 'diff_restrict')

        count = 0
        if not os.path.exists(filter_folder):
            print('No diff record!')
            exit(-1)

        for _, dirs, _ in os.walk(filter_folder):
            for commit_dir in dirs:
                for _, _, file_names in os.walk(os.path.join(filter_folder, commit_dir)):
                    file_list = []
                    file_names.remove('description.txt')
                    for diff in file_names:
                        result = None
                        for pattern in self.discard_file_name_re:
                            result = pattern.search(diff) if result is None else result
                        if result is None:  # no match
                            file_list.append(diff)

                    loc_list = []
                    for file in file_list:
                        with codecs.open(os.path.join(filter_folder, commit_dir, file), 'r', encoding='utf-8',
                                         errors='ignore') as f:
                            content = f.read()
                            diff_result = diff_pattern.findall(content)
                            loc = 0
                            for diff_loc in diff_result:
                                loc += int(diff_loc)
                            loc_list.append(loc)
                    if len(loc_list) == 0:
                        continue
                    if self.LOC < 0 or sorted(loc_list)[-1] <= self.LOC:
                        shutil.copytree(os.path.join(filter_folder, commit_dir),
                                        os.path.join(self.final_dir, commit_dir))
                        count += 1
                        print(count)
