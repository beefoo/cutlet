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
        default="cache/met-open-access-objects/MetObjects.csv",
        help="Path to csv data file",
    )
    parser.add_argument(
        "-query",
        dest="QUERY_STRING",
        default="",
        help="A Pandas query string to filter by. https://pandas.pydata.org/docs/user_guide/indexing.html#indexing-query",
    )
    parser.add_argument(
        "-cols",
        dest="COLUMN_NAMES",
        default="Object Name,Medium",
        help="Comma separated list of column names to create counts for",
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_FILE",
        default="output/met_{id}.csv",
        help="Output data file pattern",
    )
    args = parser.parse_args()
    return args


def main(a):
    """Main function retrieve stats from a csv data file"""

    # Read the data
    items = pd.read_csv(a.DATA_SOURCE)
    total_items = items.shape[0]
    print(f"{total_items:,} items found.")

    # Filter data by query
    if a.QUERY_STRING != "":
        items.query(a.QUERY_STRING, inplace=True)
        total_items = items.shape[0]
        print(f"{total_items:,} items after filtering with query string.")

    cols = [col.strip() for col in a.COLUMN_NAMES.split(",")]

    for col in cols:
        if col in items.columns:
            col_id = string_to_filename(col)
            filename = a.OUTPUT_FILE.format(id=col_id)
            value_counts = items[col].value_counts()
            value_counts.to_csv(filename)
            print(f"Created {filename}")
        else:
            print(f"Could not find column {col} in data")

    print("Done.")


main(parse_args())
