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
        "-out",
        dest="OUTPUT_DIR",
        default="output/met-sculptures/",
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

    make_directories([a.CACHE_DIRECTORY, a.OUTPUT_DIR])

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

    # Reset the index
    pd_items = pd_items.reset_index()

    # Iterate through items
    item_cache = load_cache_file(f"{a.CACHE_DIRECTORY}item_cache.p", {})
    for i, item in pd_items.iterrows():
        object_id = str(item["Object ID"])
        image_filename = f"{a.OUTPUT_DIR}{object_id}.jpg"

        if os.path.isfile(image_filename):
            continue

        # Check to see if item data is cached
        item_data = item_cache[object_id] if object_id in item_cache else None
        if item_data is None:
            # Request data from API
            api_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
            fields_to_cache = [
                "title",
                "artistDisplayName",
                "objectDate",
                "objectURL",
                "primaryImage",
            ]
            response = json_request(api_url)
            if "error" in response:
                print(f"{response['error']} error when requesting {api_url}")
                continue

            # Load data from response
            item_data = {}
            for field in fields_to_cache:
                if field in response:
                    item_data[field] = str(response[field]).strip()
                else:
                    item_data[field] = ""

            # Save response to cache
            item_cache[object_id] = item_data
            save_cache_file(f"{a.CACHE_DIRECTORY}item_cache.p", item_cache)

        # Download and save the image
        if "primaryImage" in item_data:
            download(item_data["primaryImage"], image_filename, verbose=False)
            if not os.path.isfile(image_filename):
                time.sleep(1)
                continue

            # Write metadata to the image file
            write_meta_to_image(
                image_filename,
                [
                    ("ImageDescription", item_data["title"]),
                    ("Artist", item_data["artistDisplayName"]),
                    ("DateTime", item_data["objectDate"]),
                    ("ImageID", item_data["objectURL"]),
                ],
            )
            print(
                f"{i+1} of {total_pd_items} ({round(100.0*i/total_pd_items,2)}%) Saved {image_filename}"
            )


main(parse_args())
