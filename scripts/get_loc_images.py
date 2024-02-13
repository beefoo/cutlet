"""Script for retrieving high resolution images from the Library of Congress"""

# -*- coding: utf-8 -*-

import argparse
import os
import time

import pandas as pd

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-src",
        dest="DATA_SOURCE",
        default="data/loc/posters-wpa-posters-2024-02-11.csv",
        help="Path to LoC collection data",
    )
    parser.add_argument(
        "-query",
        dest="QUERY_STRING",
        default="",
        help="A Pandas query string to filter by. https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-query",
    )
    parser.add_argument(
        "-cachedir",
        dest="CACHE_DIRECTORY",
        default="cache/loc/",
        help="Cache directory",
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_DIR",
        default="output/loc-posters/",
        help="Output directory",
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

    # Read the data
    items = pd.read_csv(a.DATA_SOURCE)
    total_items = items.shape[0]
    print(f"{total_items:,} items found.")

    # Filter data by query
    if a.QUERY_STRING != "":
        items = items.query(a.QUERY_STRING)
        total_items = items.shape[0]
        print(f"{total_items:,} items after filtering with query: {a.QUERY_STRING}")

        # Reset the index
        items = items.reset_index()

    # Iterate through items
    item_cache = load_cache_file(f"{a.CACHE_DIRECTORY}item_cache.p", {})
    errors = 0
    for i, item in items.iterrows():
        id = str(item["id"])
        url = str(item["url"])

        image_filename = f"{a.OUTPUT_DIR}loc-{id}.jpg"

        if os.path.isfile(image_filename):
            continue

        # Check to see if item data is cached
        item_data = item_cache[id] if id in item_cache else None
        if item_data is None:
            # Request data from API
            api_url = f"{url}?fo=json"
            response = json_request(api_url)
            if "error" in response:
                print(f"{response['error']} error when requesting {api_url}. Skipping.")
                errors += 1
                time.sleep(1)
                continue

            # Retrieve resource list from API response
            resources = get_nested_value(response, ["resources", 0, "files", 0], [])
            if not isinstance(resources, list) or len(resources) == 0:
                print(f"No resources found for {api_url}")
                continue

            # Filter out non-images
            resources = [
                r
                for r in resources
                if "mimetype" in r
                and r["mimetype"] in ["image/jpeg", "image/tiff"]
                and "size" in r
                and "url" in r
            ]
            if len(resources) == 0:
                print(f"No image resources for {api_url}")
                continue

            # Sort by size
            resources = sorted(resources, key=lambda r: -r["size"])
            largest_resource = resources[0]
            item_data = {"resource_url": largest_resource["url"]}

            # Save response to cache
            item_cache[id] = item_data
            save_cache_file(f"{a.CACHE_DIRECTORY}item_cache.p", item_cache)

        # Download and save the image
        if "resource_url" in item_data:
            image_url = item_data["resource_url"]

            # Get the file extensions of the source and destination
            src_fn, src_ext = os.path.splitext(image_url)
            dest_fn, dest_ext = os.path.splitext(image_filename)

            # Check for hash
            if "#" in src_ext:
                src_ext, _ = tuple(src_ext.split("#", 1))

            # Source and destination file extension is the same, just download
            if src_ext.lower() == dest_ext.lower():
                download(image_url, image_filename, verbose=False)

            # Source and destination file extension is different, download and convert
            else:
                image = download_and_read_image(image_url)
                try:
                    image.save(image_filename)
                except OSError:
                    print(f"Invalid image: OSError with {image_url}")
                except KeyError:
                    print(f"Invalid image: KeyError with {image_url}")

            if not os.path.isfile(image_filename):
                errors += 1
                time.sleep(1)
                continue

            print(
                f"{i+1} of {total_items} ({round(100.0*i/total_items,2)}%) Saved {image_filename}"
            )

    if errors > 0:
        print(f"Completed with {errors} errors. Re-run to retry failed image downloads")
    else:
        print("Finished with no errors")


main(parse_args())
