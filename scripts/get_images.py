"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import os
import struct
import time

import pandas as pd
import piexif

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-src",
        dest="DATA_SOURCE",
        default="output/si-chndm-pd.csv",
        help="Path to csv data file",
    )
    parser.add_argument(
        "-image",
        dest="IMAGE_COLUMN",
        default="image",
        help="The column name that contains the image URL",
    )
    parser.add_argument(
        "-query",
        dest="QUERY_STRING",
        default="",
        help="A Pandas query string to filter by. https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-query",
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_FILE",
        default="output/si-cultery/si-{id}.jpg",
        help="Output data file",
    )
    parser.add_argument(
        "-probe",
        dest="PROBE",
        action="store_true",
        help="Only output info and do not perform downloads",
    )
    args = parser.parse_args()
    return args


def main(a):
    """Main function retrieve images"""

    # Read the data
    items = pd.read_csv(a.DATA_SOURCE)
    total_items = items.shape[0]
    print(f"{total_items:,} items found.")

    # Filter data by query
    if a.QUERY_STRING != "":
        items = items.query(a.QUERY_STRING)
        total_items = items.shape[0]
        print(f"{total_items:,} items after filtering with query: {a.QUERY_STRING}")

    # Filter out rows with no image
    items = items[items[a.IMAGE_COLUMN].notnull()]
    total_items = items.shape[0]
    print(f"{total_items:,} items after filtering out items with no image")

    # Probe
    if a.PROBE:
        return

    # Make directories
    make_directories(a.OUTPUT_FILE)

    # Reset the index
    items = items.reset_index()

    # Iterate through items
    errors = 0
    for i, item in items.iterrows():
        image_filename = a.OUTPUT_FILE.format(**item)

        if os.path.isfile(image_filename):
            continue

        # Download and save the image
        image_url = item[a.IMAGE_COLUMN]

        # Get the file extensions of the source and destination
        src_fn, src_ext = os.path.splitext(image_url)
        dest_fn, dest_ext = os.path.splitext(image_filename)

        # Check for hash
        if "#" in src_ext:
            src_ext, _ = tuple(src_ext.split("#", 1))

        # print(src_ext, dest_ext)
        # break

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

        # If no image was downloaded, assume an error
        if not os.path.isfile(image_filename):
            errors += 1
            continue

        print(
            f"{i+1} of {total_items} ({round(100.0*i/total_items,2)}%) Saved {image_filename}"
        )

    if errors > 0:
        print(f"Completed with {errors} errors. Re-run to retry failed image downloads")
    else:
        print("Finished with no errors")


main(parse_args())
