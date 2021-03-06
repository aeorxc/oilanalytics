import glob
import os


def find_latest_file(fold):
    list_of_files = glob.glob(fold)
    list_of_files = [x for x in list_of_files if "~" not in x]
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file
