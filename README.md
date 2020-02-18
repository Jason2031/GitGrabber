# GitGrabber
A script to grab specific info from specific git repo

#### Grab process

*Extract* git repo with specific restrict (commit count, or commit datetime interval) & *Filter* git commit  using key words

#### Prerequisites

* python3
  * gitpython
  * pyyaml
  * sqlite3

Install them using pip or else.

* A handy sqlite browser - to view the result

#### How to use?

1. Download the git repo which you want to grab infomation from.

2. Download this repo.

3. Edit `config/config.yml` file, or provide your own `config.yml`. Set the `working_dir` field and other fields that interests you.

4. `cd` to `this_repo/src`.

5. Run script with `python3 main.py` or `python3 main.py --config=path/to/config.yml`.

6. Extract result will be stored in the path you specified in `config.yml.working_dir/.gitgrabber_report`.

7. All script parameters:

   ```
     --config CONFIG_FILE(string)  location of config.yml file
     --skip_restrict SKIP_RESTRICT(bool)
                           whether to skip commit_count, from_date, to_date
                           restrictions in config file
     --skip_first_keywords SKIP_FIRST_KEYWORDS(bool)
                           whether to skip first layer of keywords filtering
     --skip_second_keywords SKIP_SECOND_KEYWORDS(bool)
                           whether to skip second layer of keywords filtering
   
   ```

   

   ##### The config file

   The config file is in yaml format.

   * `working_dir` denotes the path to the target git repo, this should point to the folder containing `.git` folder.
   * `filter` denotes the `extractor` conditions.
     * `branch` denotes the target branch name.
     * `restrict` denotes the extractor restriction.
       * `commit_count` denotes extractor commit count, possible values: `-1` meaning unlimited or `[actual number]`.
       * `from_date` & `to_date` denote extractor time interval, possible values: `-1` meaning unlimited or `[actual date]` with `%Y-%m-%d` format.
     * `keywords` denotes the `keyword_filter` restriction.
       * `first` denotes the first-level key word filter, usually some borad words.
       * `second` denotes the second-level key word filter, usually some specific words.
     * `LOC` is a part of the `file_filter` restrictoins, it denotes the lines of diff code bound for each file. Those files whose lines of diff code is larger than this number will be discarded.
     * `NOF` is also a part of the `file_filter` restrictions, it denotes the number of diff files bound for each commit. Those commits whose number of diff files is larger than this number will be discarded.
     * `discard_file_names` is also a part of the `file_filter` restrictions, it denotes those files whose name contains these words will be discarded.
     * `ignore_case` indicates whether to ignore case when discarding file using `discard_file_names`.
   * `checkout` denotes whether to checkout changed files in commit (old and new version)

#### The result folder

original git repo =====filter.restrict=====> `diff_restrict` =====filter.keywords.first=====> `diff_keyword_first` =====filter.keywords.second=====> `dif_second` =====filter.LOC & NOF & file_name & ignore_case =====> `diff_final`

`.gitgrabber_report` folder

* report.db - sqlite file storing meta data of each commit extracted
* diff_xxx - folder storing patches of each commit (see description mentioned above)
  * `1234…abcd`(hash) - folder storing patch files of corresponding commit
    * `description.txt` - json-formatted file storing description data of this commit (same as corresponding row in report.db)
    * `a.diff` - patch file
    * `b.diff`
  * `abcd…1234`
    * `description.txt`
    * `a.diff`
  * ...

#### The report.db

There are 3 tables after `All done!` prompt. The relationship among these 3 tables is as follow:

original git repo =====filter.restrict=====> `record` =====filter.keywords.first=====> `keyword_first` =====filter.key_words.second=====> `keyword_second`

#### Note

1. sqlite in python can't use question marks ("?") in LIKE sentence, so MAY CAUSE SQL INJECTION ATTACK IN KEYWORD FIELD!!!
2. Filter process may suffer from performance problem.