"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import os

import cv2
import numpy as np
from segment_anything import SamPredictor, sam_model_registry
from segment_anything.utils.transforms import ResizeLongestSide
import torch

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in", dest="INPUT_FILES", default="sample/figures/*.jpg", help="Path to images"
    )
    parser.add_argument("-model", dest="MODEL", default="vit_h", help="Model used")
    parser.add_argument(
        "-checkpoint",
        dest="MODEL_CHECKPOINT",
        default="models/sam_vit_h_4b8939.pth",
        help="Path to checkpoint file",
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_DIR",
        default="output/figure-segments/",
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


# https://github.com/computational-cell-analytics/micro-sam/blob/83997ff4a471cd2159fda4e26d1445f3be79eb08/micro_sam/prompt_based_segmentation.py#L375-L388
def compute_logits_from_mask(mask, eps=1e-3):
    """Convert a mask to logits"""

    def inv_sigmoid(x):
        return np.log(x / (1 - x))

    logits = np.zeros(mask.shape, dtype="float32")
    logits[mask == 255] = 1 - eps
    logits[mask == 0] = eps
    logits = inv_sigmoid(logits)

    # resize to the expected mask shape of SAM (256x256)
    assert logits.ndim == 2
    expected_shape = (256, 256)

    if logits.shape == expected_shape:  # shape matches, do nothing
        pass

    elif logits.shape[0] == logits.shape[1]:  # shape is square
        trafo = ResizeLongestSide(expected_shape[0])
        logits = trafo.apply_image(logits[..., None])

    else:  # shape is not square
        # resize the longest side to expected shape
        trafo = ResizeLongestSide(expected_shape[0])
        logits = trafo.apply_image(logits[..., None])

        # pad the other side
        h, w = logits.shape
        padh = expected_shape[0] - h
        padw = expected_shape[1] - w
        # IMPORTANT: need to pad with zero, otherwise SAM doesn't understand the padding
        pad_width = ((0, padh), (0, padw))
        logits = np.pad(logits, pad_width, mode="constant", constant_values=0)

    logits = logits[None]
    assert logits.shape == (1, 256, 256), f"{logits.shape}"
    return logits


def do_prediction(predictor, image=False, bbox=None, mask=None, reset=False):
    """Do segmentation prediction"""

    masks = []

    try:
        if reset:
            predictor.reset_image()

        if image is not False:
            predictor.set_image(image)

        input_box = np.array(bbox)[None, :] if bbox is not None else None
        masks, _, _ = predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_box,
            mask_input=mask,
            multimask_output=False,
        )
    except RuntimeError as error:
        print(f"Error with segmentation: {error}")

    return masks


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
        existsFn = f"{a.OUTPUT_DIR}/{get_basename(fn)}.png"
        if os.path.isfile(existsFn):
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

        # Do prediction
        masks = do_prediction(predictor, image, bbox=[0, 0, im_w, im_h], reset=i > 0)
        if len(masks) == 0:
            continue

        # Assume the mask is the background, so invert it to get the foreground
        mask = masks[0]
        mask = np.bitwise_not(mask)

        # Add transparency
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)

        # Convert to int
        segment_mask = mask.astype(np.uint8)
        segment_mask *= 255

        # Get the largest segment
        largest_segment = get_largest_mask_segment(segment_mask)

        # Mask the image
        masked_image = cv2.bitwise_and(
            image, image, mask=largest_segment["mask"].astype(np.uint8)
        )

        # Crop the image
        x, y, w, h = tuple(largest_segment["bbox"])
        x2 = x + w
        y2 = y + h
        cropped_image = masked_image[y:y2, x:x2]

        segment_fn = f"{a.OUTPUT_DIR}/{get_basename(fn)}.png"
        cv2.imwrite(segment_fn, cropped_image)


main(parse_args())
