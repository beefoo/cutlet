"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import pandas as pd

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-src",
        dest="DATA_SOURCE",
        default="https://github.com/metmuseum/openaccess/raw/master/MetObjects.csv",
        help="URL to Met collection data",
    )
    parser.add_argument(
        "-cachedir",
        dest="CACHE_DIRECTORY",
        default="cache/met-open-access-objects/",
        help="Cache directory",
    )
    parser.add_argument(
        "-dout",
        dest="OUTPUT_DATA_FILE",
        default="output/met-open-access-objects.csv",
        help="Output data file",
    )
    parser.add_argument(
        "-clean",
        dest="CLEAN",
        action="store_true",
        help="Clear the cache before processing?",
    )
    args = parser.parse_args()
    return args


def main(a):
    """Main function retrieve open access Met images"""

    make_directories(a.CACHE_DIRECTORY)

    if a.CLEAN:
        empty_directory(a.CACHE_DIRECTORY)

    # Download the data
    data_source_url = a.DATA_SOURCE
    data_source_fn = data_source_url.split("/")[-1]
    data_source_file = f"{a.CACHE_DIRECTORY}{data_source_fn}"
    download(data_source_url, data_source_file)

    # Read the data
    items = pd.read_csv(data_source_file)
    total_items = items.shape[0]
    print(f"{total_items:,} items found.")

    # Filter data
    pd_items = items.loc[items["Is Public Domain"]]
    total_pd_items = pd_items.shape[0]
    print(f"{total_pd_items:,} public domain items found.")


main(parse_args())
