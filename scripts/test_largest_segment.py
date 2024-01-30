# -*- coding: utf-8 -*-

import argparse
import cv2
from utilities import *

parser = argparse.ArgumentParser()
parser.add_argument(
    "-in",
    dest="INPUT_FILE",
    default="output/met-sculptures/10766.jpg",
    help="Input image file",
)
args = parser.parse_args()

im = cv2.imread(args.INPUT_FILE)

get_largest_segment_bb(im, debug=True)
