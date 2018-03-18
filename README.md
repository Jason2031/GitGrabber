# GitGrabber
A script to grab specific info from specific git repo

#### Grab process

*Extract* git repo with specific restrict (commit count, or commit datetime interval) 👉 *Filter* git commit  using key words

#### Prerequisites

* python3
  * gitpython
  * pyyaml

Install them using pip or else.

* A handy sqlite browser - to view the result

#### How to use?

1. Download the git repo which you want to grab infomation from.
2. Download this repo.
3. Edit the config.yml file. Set the `working_dir` and `output.dir` fields and other fields that interests you.
4. `cd` to this repo.
5. Run script with `python main.py` or `python main.py --config config.yml`.
6. Extract result will be stored in the path you specified in `config.yml`.

#### The result folder

result

* report.db (or name you specified in `config.yml`) - sqlite file storing meta data of each commit extracted
* diff_xxx - folder storing patches of each commit (`diff_all` for all commits, `diff_mid` for middle result from first level key words, `diff_result` for final result from second level key words)
  * description.txt - json-formatted file storing description data of this commit (same as corresponding row in report.db)
  * 1234…abcd - folder storing patch files of corresponding commit
    * a.diff - patch file
    * b.diff
  * abcd…1234
    * a.diff

#### The report.db

There are 3 tables after `All done!` prompt. The relationship among these 3 tables is as follow:

original git repo =====filter.restrict=====> `record` table =====filter.key_words.first=====> `mid` table =====filter.key_words.second=====> result

#### Note

1. sqlite in python can't use question marks ("?") in LIKE sentence, so MAY CAUSE SQL INJECTION ATTACK IN KEYWORD FIELD!!!
2. Filter process may suffer from performance problem.