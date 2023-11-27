"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in", dest="INPUT_FILES", default="sample/*.jpg", help="Path to images"
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_DIR",
        default="output/sample-segments/",
        help="Output directory",
    )
    parser.add_argument(
        "-debug",
        dest="DEBUG",
        action="store_true",
        help="Print debug information and do not process images",
    )
    args = parser.parse_args()
    return args


def main(a):
    """Main function to parse and add dates to transcript data"""

    if not a.DEBUG:
        # Make sure output dirs exist
        make_directories(a.OUTPUT_DIR)

    filenames = get_filenames(a.INPUT_FILE)


main(parse_args())
