# GitGrabber
A script to grab specific info from specific git repo

#### Extract process

Strip git repo with specific restrict (commit count, or commit datetime interval, finished) 👉 Filter git commit  with key words (TODO)

#### Prerequisites

* python3
  * gitpython
  * yaml

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

| — — report.db (or name you specified in `config.yml`) - sqlite file storing meta data of each commit extracted

| — — diff - folder storing patches of each commit

​               | — — 1234…abcd - folder storing patch files of corresponding commit

​               |               | — — a.diff - patch file

​               |               | — — b.diff

​               | — — abcd…1234

​                               | — — a.diff

#### TODO

1. Filter commit using user-defined key words