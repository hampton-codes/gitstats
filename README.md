# gitstats

gitstats grabs interesting statistics from all projects in the organization

## Example Output
![Example JSON output](sample_output.png)
![Example CSV output](sample_output_csv.png)

## Installation

Prereq: **python3**

Download/clone from github [https://github.com/hampton-code/gitstats](https://github.com/hampton-code/gitstats)

```python
pip install -r requirements.txt
```

## Configuration
Copy `conf/gitstats.ini.example` as `conf/gitstats.ini` and add your configuration

## Run
```python
cd src
python3 gitstats.py -h
usage: gitstats.py [-h] [-c CONFIG] [-r REPOSITORY] [-f FIELDS]
                   [-o ORGANIZATION] [-u USER] [-nl] [-m MODE]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        path to config file. (eg:
                        --config=../conf/gitstats.ini)
  -r REPOSITORY, --repository REPOSITORY
                        path to specific repository. (eg:
                        --repository=hampton-codes/gitstats)
  -f FIELDS, --fields FIELDS
                        fields to collect. comma-separated. (eg:
                        --fields=name,owner.type)
  -o ORGANIZATION, --organization ORGANIZATION
                        all github org repos (eg: --org=hampton-codes)
  -u USER, --user USER  all github user repos (eg: --user=hampton-codes)
  -nl, --nolanguages    do not collect language stats
  -m MODE, --mode MODE  output format. Values: (json|csv)
```