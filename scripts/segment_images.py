"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import torch

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in", dest="INPUT_FILES", default="sample/faces/*.jpg", help="Path to images"
    )
    parser.add_argument("-model", dest="MODEL", default="vit_h", help="Model used")
    parser.add_argument(
        "-checkpoint",
        dest="MODEL_CHECKPOINT",
        default="models/sam_vit_h_4b8939.pth",
        help="Path to checkpoint file",
    )
    parser.add_argument(
        "-segments", dest="MAX_SEGMENTS", default=5, help="Max segments per image"
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
    """Main function to segment a directory of images"""

    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    if not a.DEBUG:
        # Make sure output dirs exist
        make_directories(a.OUTPUT_DIR)

    filenames = get_filenames(a.INPUT_FILES)
    fileCount = len(filenames)
    print(f"{fileCount} files found.")

    sam = sam_model_registry[a.MODEL](checkpoint=a.MODEL_CHECKPOINT)
    if torch.cuda.is_available():
        print("CUDA is available")
        sam.to(device="cuda")
    mask_generator = SamAutomaticMaskGenerator(sam)

    for i, fn in enumerate(filenames):
        print(f"Processing {i+1} of {fileCount}: {fn}")
        image = cv2.imread(fn)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        masks = mask_generator.generate(image)
        masks = sorted(masks, key=(lambda x: x["area"]), reverse=True)
        sampleSize = a.MAX_SEGMENTS
        if len(masks) > sampleSize:
            masks = masks[:sampleSize]
        if len(masks) == 0:
            continue
        image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)  # add transparency
        for j, mask in enumerate(masks):
            bbox = mask["bbox"]
            x, y, w, h = tuple(bbox)
            segment = mask["segmentation"]
            # print(bbox, segment.shape, segment.dtype)
            # bg = np.zeros(image.shape, image.dtype)
            segment_mask = segment.astype(np.uint8)
            segment_mask *= 255
            masked_image = cv2.bitwise_and(image, image, mask=segment_mask)
            cropped_image = masked_image[y : y + h, x : x + w]
            segmentFn = f"{a.OUTPUT_DIR}/{getBasename(fn)}-{j+1}.png"
            cv2.imwrite(segmentFn, cropped_image)


main(parse_args())
