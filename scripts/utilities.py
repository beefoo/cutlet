"""Utility functions to support all scripts"""

import glob
import json
import os
import pickle
import re
import struct

import cv2
import numpy as np
from PIL import Image
import piexif
import requests


def bbox_contains(bbox_a, bbox_b):
    """Check if bounding box A contains bounding box B"""
    a_x1, a_y1, a_w, a_h = bbox_a
    b_x1, b_y1, b_w, b_h = bbox_b
    a_x2 = a_x1 + a_w
    a_y2 = a_y1 + a_h
    b_x2 = b_x1 + b_w
    b_y2 = b_y1 + b_h

    return b_x1 >= a_x1 and b_x2 <= a_x2 and b_y1 >= a_y1 and b_y2 <= a_y2


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
    except requests.exceptions.MissingSchema:
        print(f"Schema error when trying to get image {url}")
    except requests.HTTPError:
        print(f"HTTP error when trying to get {url}")
    except requests.Timeout:
        print(f"Timeout when trying to get {url}")


def download_and_read_image(url):
    """Download and read an image without saving to file"""
    im = False
    try:
        im = Image.open(requests.get(url, stream=True, timeout=60).raw)
    except requests.HTTPError:
        print(f"HTTP error when trying to get image {url}")
    except requests.exceptions.MissingSchema:
        print(f"Schema error when trying to get image {url}")
    except requests.Timeout:
        print(f"Timeout when trying to get image {url}")
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


def get_largest_mask_segment(mask_image, debug=False):
    """Function to return the mask and bounding box of the largest segment in the image"""

    # Try to get the largest segment
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        mask_image, connectivity=4
    )
    sizes = stats[:, -1]
    max_label = 1
    max_size = sizes[1]
    for i in range(1, nb_components):
        if sizes[i] > max_size:
            max_label = i
            max_size = sizes[i]
    mask_with_largest_segment = np.zeros(output.shape)
    mask_with_largest_segment[output == max_label] = 255

    # Display mask
    if debug:
        scale = 0.333
        cv2.imshow(
            "Biggest component",
            cv2.resize(mask_with_largest_segment, (0, 0), fx=scale, fy=scale),
        )
        cv2.waitKey(0)

    # get bounding box
    width = stats[max_label, cv2.CC_STAT_WIDTH]
    height = stats[max_label, cv2.CC_STAT_HEIGHT]
    x = stats[max_label, cv2.CC_STAT_LEFT]
    y = stats[max_label, cv2.CC_STAT_TOP]

    return {"mask": mask_with_largest_segment, "bbox": (x, y, width, height)}


def get_nested_value(root, nodes, default_value=""):
    """Get a value from a nested dict"""
    value = default_value
    found = True
    if not isinstance(nodes, list):
        nodes = [nodes]

    for node in nodes:
        if isinstance(node, int):
            if isinstance(root, list) and len(root) > node:
                root = root[node]
            else:
                found = False
                break
        elif node in root:
            root = root[node]
        else:
            found = False
            break

    if found:
        value = root

    return value


def get_where(arr, return_key, condition, default_value=""):
    """Return a value from a list based on a condition"""
    value = default_value
    condition_key, condition_value = condition
    for item in arr:
        if (
            condition_key in item
            and item[condition_key] == condition_value
            and return_key in item
        ):
            value = item[return_key]
            break
    return value


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


def read_image_meta(image_filename, meta):
    """Read exif metadata from image file"""
    exif_dict = piexif.load(image_filename)
    values = {}
    for field_from, field_to in meta:
        value = exif_dict["0th"][getattr(piexif.ImageIFD, field_from)].decode()
        values[field_to] = value
    return values


def read_line_delimited_json(filename):
    """Read a line-delimted json file"""
    results = []
    with open(filename, "rb") as f:
        for line in f:
            item = json.loads(line.decode())
            results.append(item)
    return results


def read_lines(filename):
    """Read lines from file"""
    lines = []
    with open(filename, "rb") as f:
        lines = [line.decode().rstrip() for line in f]
    return lines


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


def string_to_filename(string):
    """Converts an arbitrary string into a valid filename"""

    s = re.sub("[^0-9a-z]+", "_", str(string).lower())
    filename = re.sub(r"\_+", "_", s)
    return filename


def write_meta_to_image(image_filename, meta):
    """Write exif metadata to image file"""
    try:
        exif_dict = piexif.load(image_filename)
        for field, value in meta:
            if value and value != "":
                exif_dict["0th"][getattr(piexif.ImageIFD, field)] = string_to_ascii(
                    value
                )
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_filename)
        return True

    except (
        struct.error,
        piexif._exceptions.InvalidImageDataError,
    ) as error:
        print(
            f" Error ({error}) trying to write meta to {image_filename}. Trying again."
        )
        return False
