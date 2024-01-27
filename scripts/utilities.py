"""Utility functions to support all scripts"""

import glob
import os
from PIL import Image
import pickle
import piexif
import requests


def download(url, filename, overwrite=False, verbose=True):
    """Function for downloading an arbitrary file as binary file."""
    if os.path.isfile(filename) and not overwrite:
        if verbose:
            print(f"{filename} already exists.")
        return
    if verbose:
        print(f"Downloading file from {url}...")
    try:
        r = requests.get(url, stream=True, timeout=30)
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        if verbose:
            print(f"Downloaded {url}")
    except requests.HTTPError:
        print(f"HTTP error when trying to get {url}")
    except requests.Timeout:
        print(f"Timeout when trying to get {url}")


def download_and_read_image(url):
    """Download and read an image without saving to file"""
    im = None
    try:
        im = Image.open(requests.get(url, stream=True, timeout=60).raw)
    except requests.HTTPError:
        print(f"HTTP error when trying to get image {url}")
        im = False
    except requests.Timeout:
        print(f"Timeout when trying to get image {url}")
        im = False
    return im


def empty_directory(dirname):
    """Function for emptying a directory"""
    dirname = dirname.strip("/")
    files = f"{dirname}/*"
    remove_files(files)


def get_basename(fn):
    """Function to return the name of the filename without an extension"""
    return os.path.splitext(os.path.basename(fn))[0]


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


def json_request(url):
    """Make a JSON request"""
    data = {}
    try:
        response = requests.get(url, timeout=30)
        data = response.json()
    except requests.HTTPError:
        data = {"error": "HTTPError"}
    except requests.Timeout:
        data = {"error": "Timeout"}
    except requests.JSONDecodeError:
        data = {"error": "JSONDecodeError"}
    return data


def load_cache_file(filename, defaultValue={}):
    """Load a pickle file"""
    if os.path.isfile(filename):
        return pickle.load(open(filename, "rb"))
    else:
        return defaultValue


def make_directories(filenames):
    """Function for creating directories if they do not exist."""
    if not isinstance(filenames, list):
        filenames = [filenames]
    for filename in filenames:
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)


def remove_files(listOrString):
    """Function for removing a list of files given a string or list."""
    filenames = listOrString
    if not isinstance(listOrString, list) and "*" in listOrString:
        filenames = glob.glob(listOrString)
    elif not isinstance(listOrString, list):
        filenames = [listOrString]
    print(f"Removing {len(filenames)} files")
    for fn in filenames:
        if os.path.isfile(fn):
            os.remove(fn)


def round_int(value):
    """Round a value and convert to integer"""
    return int(round(value))


def save_cache_file(filename, data):
    """Save a pickle file"""
    pickle.dump(data, open(filename, "wb"))


def string_to_ascii(string):
    """Convert a string to ascii"""
    return string.encode("ascii", "ignore")


def write_meta_to_image(image_filename, meta):
    """Write exif metadata to image file"""
    exif_dict = piexif.load(image_filename)
    for field, value in meta:
        if value and value != "":
            exif_dict["0th"][getattr(piexif.ImageIFD, field)] = string_to_ascii(value)
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, image_filename)
