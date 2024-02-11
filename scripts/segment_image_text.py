"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import os

import cv2
import numpy as np
import pytesseract
from segment_anything import SamPredictor, sam_model_registry
import torch

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in", dest="INPUT_FILES", default="sample/posters/*.jpg", help="Path to images"
    )
    parser.add_argument("-model", dest="MODEL", default="vit_h", help="Model used")
    parser.add_argument(
        "-checkpoint",
        dest="MODEL_CHECKPOINT",
        default="models/sam_vit_h_4b8939.pth",
        help="Path to checkpoint file",
    )
    parser.add_argument(
        "-maxd",
        dest="MAX_IMAGE_DIMENSION",
        type=int,
        default=4000,
        help="Max dimension of a source image; image will be resized before processing",
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_DIR",
        default="output/sample-text-segments/",
        help="Output directory",
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


def show_boxes(image, boxes):
    """Display bounding boxes on image"""
    h, w, _ = image.shape
    for box in boxes:
        symbol, x1, y1, x2, y2 = box
        image = cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(
            image, symbol, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3
        )

    cv2.imshow("image", image)
    cv2.waitKey(0)


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

    predictor = SamPredictor(sam)

    for i, fn in enumerate(filenames):
        existing_files = get_filenames(f"{a.OUTPUT_DIR}/**/{get_basename(fn)}-*.png")
        if len(existing_files) > 0:
            print(f"Already processed {i+1} of {file_count}: {fn}")
            continue
        print(f"Processing {i+1} of {file_count}: {fn}")

        image = cv2.imread(fn)
        im_h, im_w, im_c = image.shape
        im_d = max(im_h, im_w)

        # Resize if necessary
        if im_d > a.MAX_IMAGE_DIMENSION:
            scale = 1.0 * a.MAX_IMAGE_DIMENSION / im_d
            im_h = round_int(im_h * scale)
            im_w = round_int(im_w * scale)
            image = cv2.resize(image, (im_w, im_h))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Do OCR
        boxes = pytesseract.image_to_boxes(image)
        # print(boxes)
        boxes = [line.split(" ") for line in boxes.splitlines()]
        # put into format (symbol, x1, y1, x2, y2)
        boxes = [
            (b[0], int(b[1]), im_h - int(b[4]), int(b[3]), im_h - int(b[2]))
            for b in boxes
        ]

        # Show bounding boxes if debug
        if a.DEBUG:
            show_boxes(image, boxes)
            break

        # Add transparency
        image_rgba = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)

        # Do segmentation for each symbol
        is_first = True
        counts = {}
        for bbox in boxes:
            symbol, x1, y1, x2, y2 = bbox
            masks = []

            # only process alpha numeric symbols
            if not symbol.isalnum():
                continue

            # Do the prediction with the symbol's bounding box
            try:
                if is_first:
                    predictor.reset_image()
                    predictor.set_image(image)
                    is_first = False

                input_box = np.array([x1, y1, x2, y2])[None, :]
                masks, _, _ = predictor.predict(
                    point_coords=None,
                    point_labels=None,
                    box=input_box,
                    multimask_output=False,
                )
            except RuntimeError as error:
                print(f"Error with segmentation: {error}")

            if len(masks) == 0:
                continue

            # Convert mask to int
            mask = masks[0]
            segment_mask = mask.astype(np.uint8)
            segment_mask *= 255

            # Mask and crop the image
            masked_image = cv2.bitwise_and(image_rgba, image_rgba, mask=segment_mask)
            cropped_image = masked_image[y1:y2, x1:x2]

            # Write the image to file
            if symbol not in counts:
                counts[symbol] = 0
            counts[symbol] += 1
            count = counts[symbol]
            segment_fn = (
                f"{a.OUTPUT_DIR}{symbol.lower()}/{get_basename(fn)}-{count}.png"
            )
            make_directories(segment_fn)
            cv2.imwrite(segment_fn, cropped_image)


main(parse_args())
