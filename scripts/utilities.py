"""Utility functions to support all scripts"""

import glob
import os


def get_filenames(file_string, verbose=False):
    """Function for retrieve a list of files given a string."""
    files = []
    if "**" in file_string:
        files = glob.glob(file_string, recursive=True)
    if "*" in file_string:
        files = glob.glob(file_string)
    else:
        files = [file_string]
    file_count = len(files)
    files = sorted(files)
    if verbose:
        print(f"Found {file_count} files")
    return files


def make_directories(filenames):
    """Function for creating directories if they do not exist."""
    if not isinstance(filenames, list):
        filenames = [filenames]
    for filename in filenames:
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
