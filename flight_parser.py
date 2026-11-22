# ressources used  for this file : 
    
    # argparse : https://www.youtube.com/watch?v=88pl8TuuKz0
    # json in python : https://www.youtube.com/watch?v=-51jxlQaxyA
    # parsing in json : https://www.youtube.com/watch?v=nKtyWfqNmr8



""" validate flight csv files  save a json database answer queries  """

import argparse    # reads the arguments typed in the command line
import json     # to read and write json files
import logging   # it write errors.log
import os    # for file and folder paths
import sys    # used for the error messages and to quit the program
from datetime import datetime   # current time for the response file name

from validator import load_airports  # we import some functions from other files
from csv_loader import parse_files
from query import run_queries

# replace with infos

STUDENT_ID = "260ADB193"
FIRST_NAME = "Emma"
LAST_NAME = "Fazilleau"


def build_parser() -> argparse.ArgumentParser :
    """ this function creates the argument parser with the options"""

    # the parser knows which options the user can type
    parser = argparse.ArgumentParser(prog = "flight_parser.py", description = "Validate flight CSV files, save a JSON database and answer queries.", allow_abbrev = False)

    # one data source is required  -i  -d  or  -j
    #the useer can only chose one of them
    
# ---------- AI generated ------------------------------------------------------------------------------------
    
    source = parser.add_mutually_exclusive_group(required = True)
    source.add_argument("-i", metavar = "FILE", help = "read a csv file")
    source.add_argument("-d", metavar = "FOLDER", help = "extract every csv file from the folder")
    source.add_argument("-j", metavar = "FILE", help = "it loads an existing json database")

    # other options
    parser.add_argument("-a", metavar = "FILE", help = "airports list file")
    parser.add_argument("-o", metavar = "FILE", help = "output path of the json database")
    parser.add_argument("-q", metavar = "FILE", help = "json file with the queries to run")
    parser.add_argument("-r", metavar = "FOLDER", default = ".", help = "folder of the response file")

    return parser


# ------------------------------------------------------------------------------------------------------------

def _read_json_file(path : str) :
    """this function reads a json file and return the content also it raises errors """

    # we open the file and try to read the json inside
    with open(path, encoding = "utf-8") as f :
        try :
            return json.load(f)
        except json.JSONDecodeError :
            # the file exists but the json is broken
            raise ValueError(f"'{path}' is not valid json")


def _write_json_file(path: str, data) -> None :
    """it writes data to a json file."""

    # "w" means we write in the file
    with open(path, "w", encoding = "utf-8") as f :
        json.dump(data, f, indent = 2)


def _find_csv_files(folder : str) -> list[str] :
    """this function returns the paths of the csv files in the folder  """

    # the folder must exist
    if not os.path.isdir(folder) :
        raise ValueError(f"'{folder}' is'nt a folder")

    names = []
    # sorted() puts the files in alphabetical order
    for name in sorted(os.listdir(folder)) :
        
        # we build the path folder + file name
        path = os.path.join(folder, name)
        
        # only files with a name that ends with csv
        if name.endswith(".csv") :
            # it must be a file not a sub-folder
            if os.path.isfile(path) :
                names.append(path)

    # if the list is empty there is nothing to read
    if not names :
        raise ValueError(f"no csv file found in '{folder}'")

    return names


def _write_error_log(log_path : str, errors : list[str]) -> None :
    """ this function writes one warning line per error """

    # we get the logger called "flight_parser" and we set its level
    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)

    # mode = "w" creates or empties the file even if there's no errors
    handler = logging.FileHandler(log_path, mode = "w", encoding = "utf-8")

    # the formatter decides how each line appears - date, level and message
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt = "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try :
        for message in errors :     # one warning line for each error
            logger.warning(message)
    finally :
        
        logger.removeHandler(handler)     # always remove and close the handler
        handler.close()


def _load_database(path : str) -> list[dict] :
    """ this function load a sjon database -j must be a list of objects """

    data = _read_json_file(path)

    # 1 the data must be a list
    is_valid = isinstance(data, list)

    # 2 every item of the list must be a dictionary 
    if is_valid :
        for item in data :
            if not isinstance(item, dict) :
                is_valid = False

    # if one check failed we raise an error
    if not is_valid :
        raise ValueError(f"'{path}' must contain a json array of objects")

    return data


def _load_queries(path : str) :
    """this function loads the query file -q it must be one object or list of objects  """
    

    data = _read_json_file(path)

     
    if isinstance(data, dict) :   # case 1 one single query
        return data

    # case 2 list of queries, every item must be an object
    if isinstance(data, list) :
        all_objects = True
        for item in data :
            if not isinstance(item, dict) :
                all_objects = False

        if all_objects :
            return data

    # any other case is error
    raise ValueError(f"'{path}' must contain a json object or an array of objects")


def _exit_code(exc : SystemExit) -> int :
    """it turns the SystemExit raised by argparse into a number."""

    if exc.code is None :
        return 0
    
    # argparse gives a number 0 for -h, 2 for a usage error
    if isinstance(exc.code, int) :
        return exc.code
    return 1


def main(argv : list[str] | None = None) -> int :
    """it runs the whole program and return the exit code 0, 1 or 2 """

    parser = build_parser()

    # argparse stops the program with SystemExit when the usage is wrong

    try :
        args = parser.parse_args(argv)

        # rules that argparse cannot express alone
        if args.j is None and args.a is None :
            parser.error("-a is required with -i and -d")
            
        if args.j is not None and args.o is not None :
            parser.error("-o cannot be used with -j")
    except SystemExit as exc :
        return _exit_code(exc)

    try :
        if args.j is not None :
            # database loaded from json : no database written
            db = _load_database(args.j)
        else :
            # parse the CSV file(s)
            airports = load_airports(args.a)
            if args.i is not None :
                paths = [args.i]
            else :
                paths = _find_csv_files(args.d)
            records, errors = parse_files(paths, airports)

            # write the database and errors.log in the same folder
            # by default the database is called db.json unless -o is given
            db_path = "db.json"
            if args.o is not None :
                db_path = args.o
            _write_json_file(db_path, records)

            # errors.log goes in the same folder as the database
            full_db_path = os.path.abspath(db_path)
            db_folder = os.path.dirname(full_db_path)
            log_path = os.path.join(db_folder, "errors.log")
            _write_error_log(log_path, errors)

            print(f"{len(records)} valid flights, {len(errors)} invalid rows")
            db = records

        # run the queries only if -q was given
        if args.q is not None :
            queries = _load_queries(args.q)
            results = run_queries(db, queries)

            # the file name contains the date and the time : YYYYMMDD_HHMM
            now = datetime.now()
            stamp = now.strftime("%Y%m%d_%H%M")
            file_name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            _write_json_file(os.path.join(args.r, file_name), results)
            print(f"{len(results)} queries answered")

    except (OSError, ValueError) as exc :
        # expected problems : a clean message, no traceback
        message = str(exc).replace("\n", " ")
        print(f"Error: {message}", file = sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())