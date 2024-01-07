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
        "-segments", dest="MAX_SEGMENTS", default=3, help="Max segments per image"
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_DIR",
        default="output/sample-segments/",
        help="Output directory",
    )
    parser.add_argument(
        "-maxd",
        dest="MAX_IMAGE_DIMENSION",
        type=int,
        default=4096,
        help="Max dimension of a source image; image will be resized before processing",
    )
    parser.add_argument(
        "-clean",
        dest="CLEAN",
        action="store_true",
        help="Clear the output directory before processing?",
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

    if a.CLEAN:
        empty_directory(a.OUTPUT_DIR)

    filenames = get_filenames(a.INPUT_FILES)
    file_count = len(filenames)
    print(f"{file_count} files found.")

    sam = sam_model_registry[a.MODEL](checkpoint=a.MODEL_CHECKPOINT)
    if torch.cuda.is_available():
        print("CUDA is available")
        sam.to(device="cuda")
    mask_generator = SamAutomaticMaskGenerator(sam, min_mask_region_area=(32 * 32))

    for i, fn in enumerate(filenames):
        existsFn = f"{a.OUTPUT_DIR}/{get_basename(fn)}-1.png"
        if os.path.isfile(existsFn):
            print(f"Already processed {i+1} of {file_count}: {fn}")
            continue
        print(f"Processing {i+1} of {file_count}: {fn}")
        image = cv2.imread(fn)
        im_h, im_w, im_c = image.shape
        im_d = max(im_h, im_w)
        if im_d > a.MAX_IMAGE_DIMENSION:
            scale = 1.0 * a.MAX_IMAGE_DIMENSION / imD
            im_h = round_int(im_h * scale)
            im_w = round_int(im_w * scale)
            image = cv2.resize(image, (im_w, im_h))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        try:
            masks = mask_generator.generate(image)
        except RuntimeError as error:
            print(f"Error with file {fn}; skipping: {error}")
            continue
        masks = sorted(masks, key=(lambda x: x["area"]), reverse=True)
        # remove masks that are on the edge
        non_edge_masks = []
        for mask in masks:
            edge = max(10, im_h * 0.05, im_w * 0.05)
            x, y, w, h = tuple(mask["bbox"])
            x2 = x + w
            y2 = y + h
            if x > edge and y > edge and x2 < (im_w - edge) and y2 < (im_h - edge):
                non_edge_masks.append(mask)
        masks = non_edge_masks
        sample_size = a.MAX_SEGMENTS
        if len(masks) > sample_size:
            masks = masks[:sample_size]
        if len(masks) == 0:
            continue
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)  # add transparency
        for j, mask in enumerate(masks):
            segment_fn = f"{a.OUTPUT_DIR}/{get_basename(fn)}-{j+1}.png"
            x, y, w, h = tuple(mask["bbox"])
            if x is None or y is None or w is None or h is None:
                continue
            x = int(x)
            y = int(y)
            w = int(w)
            h = int(h)
            x2 = x + w
            y2 = y + h
            segment = mask["segmentation"]
            # print(mask["bbox"], segment.shape, segment.dtype)
            # bg = np.zeros(image.shape, image.dtype)
            segment_mask = segment.astype(np.uint8)
            segment_mask *= 255
            masked_image = cv2.bitwise_and(image, image, mask=segment_mask)
            cropped_image = masked_image[y:y2, x:x2]
            cv2.imwrite(segment_fn, cropped_image)


main(parse_args())
