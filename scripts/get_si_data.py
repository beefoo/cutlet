"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import os

import pandas as pd

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-src",
        dest="DATA_SOURCE",
        default="https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/chndm/index.txt",
        help="URL to SI collection data",
    )
    parser.add_argument(
        "-query",
        dest="QUERY_STRING",
        default='access == "CC0"',
        help="A Pandas query string to filter by. https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-query",
    )
    parser.add_argument(
        "-cachedir",
        dest="CACHE_DIRECTORY",
        default="cache/si-chndm/",
        help="Cache directory",
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_FILE",
        default="output/si-chndm-pd.csv",
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


def parse_si_json(json_data):
    """Convert a JSON data item to flat row"""
    row = {}

    descriptive = get_nested_value(
        json_data, ["content", "descriptiveNonRepeating"], {}
    )
    structured = get_nested_value(json_data, ["content", "indexedStructured"], {})
    freetext = get_nested_value(json_data, ["content", "freetext"], {})

    row["id"] = get_nested_value(descriptive, "record_ID")
    row["title"] = get_nested_value(json_data, "title", "Untitled")
    row["unit_code"] = get_nested_value(json_data, "unitCode")
    row["record_link"] = get_nested_value(descriptive, "record_link")
    row["access"] = get_nested_value(descriptive, ["metadata_usage", "access"])
    row["data_source"] = get_nested_value(descriptive, "data_source")
    row["date"] = get_nested_value(structured, ["date", 0])
    row["name"] = get_nested_value(structured, ["name", 0])
    row["object_type"] = get_nested_value(structured, ["object_type", 0])
    row["place"] = get_nested_value(structured, ["place", 0])

    sets = get_nested_value(freetext, "setName", [])
    row["group"] = sets[-1]["content"] if len(sets) > 0 else ""

    notes = get_nested_value(freetext, "notes", [])
    row["description"] = get_where(notes, "content", ("label", "Description"))

    physical_descriptions = get_nested_value(freetext, "physicalDescription", [])
    row["medium"] = get_where(physical_descriptions, "content", ("label", "Medium"))
    row["dimensions"] = get_where(
        physical_descriptions, "content", ("label", "Dimensions")
    )

    resources = get_nested_value(
        descriptive, ["online_media", "media", 0, "resources"], []
    )
    resources = [r for r in resources if "height" in r]
    if len(resources) > 0:
        resources = sorted(resources, key=lambda r: -r["height"])
        largest_resource = resources[0]
        row["image"] = largest_resource["url"]
        row["image_width"] = largest_resource["width"]
        row["image_height"] = largest_resource["height"]

    return row


def main(a):
    """Main function retrieve open access SI data"""

    make_directories([a.CACHE_DIRECTORY, a.OUTPUT_FILE])

    if a.CLEAN:
        empty_directory(a.CACHE_DIRECTORY)

    index_filename = f"{a.CACHE_DIRECTORY}index.txt"
    download(a.DATA_SOURCE, index_filename)

    if not os.path.isfile(index_filename):
        print(f"Could not download index file: {a.DATA_SOURCE}")
        return

    # Download data from each URL
    data_urls = read_lines(index_filename)
    data_rows = []
    for url in data_urls:
        basename = os.path.basename(url)
        data_filename = f"{a.CACHE_DIRECTORY}{basename}"
        download(url, data_filename)

        if not os.path.isfile(data_filename):
            print(f"Could not download data file: {url}")
            continue

        data = read_line_delimited_json(data_filename)
        for row in data:
            data_row = parse_si_json(row)
            data_rows.append(data_row)

    # Convert to a DataFrame
    df = pd.DataFrame(data_rows)
    total_items = df.shape[0]
    print(f"{total_items:,} items found.")

    # Filter data by query
    if a.QUERY_STRING != "":
        df = df.query(a.QUERY_STRING)
        total_items = df.shape[0]
        print(f"{total_items:,} items after filtering with query: {a.QUERY_STRING}")

    # Write to file
    df.to_csv(a.OUTPUT_FILE)
    print(f"Wrote items to {a.OUTPUT_FILE}")


main(parse_args())
