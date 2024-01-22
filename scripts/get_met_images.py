"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import time

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
        "-query",
        dest="QUERY_STRING",
        default='`Object Name` == "Sculpture"',
        help="A Pandas query string to filter by. https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-query",
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
    parser.add_argument(
        "-debug",
        dest="DEBUG",
        action="store_true",
        help="Output debug info",
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

    # Filter data by query
    if a.QUERY_STRING != "":
        pd_items = pd_items.query(a.QUERY_STRING)
        total_pd_items = pd_items.shape[0]
        print(f"{total_pd_items:,} items after filtering with query: {a.QUERY_STRING}")

    # Iterate through items
    item_cache = load_cache_file(f"{a.CACHE_DIRECTORY}item_cache.p", {})
    for i, item in pd_items.iterrows():
        object_id = str(item["Object ID"])

        # Check to see if item data is cached
        item_data = item_cache[object_id] if object_id in item_cache else None
        if item_data is None:
            # Request data from API
            api_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
            fields_to_cache = ["primaryImage"]
            response = json_request(api_url)
            if "error" in response:
                print(f"{response['error']} error when requesting {api_url}")
                continue

            # Load data from response
            item_data = {}
            for field in fields_to_cache:
                if field in response:
                    item_data[field] = response[field]

            # Save response to cache
            item_cache[object_id] = item_data
            save_cache_file(f"{a.CACHE_DIRECTORY}item_cache.p", item_cache)

            # Wait a second before doing another request
            time.sleep(1)


main(parse_args())
