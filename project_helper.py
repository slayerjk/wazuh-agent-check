"""
Various Helper functions:
 - files_rotate
 - count estimated time
 - check dir exist
 - check file exist
"""

from pathlib import Path
from os import remove, mkdir, path
from datetime import datetime


# FILES ROTATION (LOGS/OTHER)
def files_rotate(path_to_rotate, num_of_files_to_keep, log_name):
    """
    This function is for log rotation.
    ARGS:
        path_to_rotate: absolute PATH of logs location
        num_of_files_to_keep: number of LOGS to keep
            delete rest
        log_name: wich log file to use to write in
    """
    with open(log_name, 'a') as output:
        print(f'{datetime.now()} - INFO - STARTED: log rotation', file=output)
        count_files_to_keep = 1
        basepath = sorted(Path(path_to_rotate).iterdir(), key=path.getctime, reverse=True)
        for entry in basepath:
            if count_files_to_keep > num_of_files_to_keep:
                remove(entry)
                print(f'{datetime.now()} - REMOVED: {entry}', file=output)
            count_files_to_keep += 1
        print(f'{datetime.now()} - SUCCEEDED: log rotation', file=output)


# ESTIMATED TIME
def count_estimated_time(start_datetime):
    """
    This function is for count script estimated time
    """
    end_time = datetime.now()
    return 'Estimated time is: ' + str(end_time - start_datetime)


# CHECK FILE EXIST
def check_file(file_path):
    return path.isfile(file_path)


# CHECK DIR EXIST
def check_create_dir(dir_path):
    if not path.isdir(dir_path):
        mkdir(dir_path)