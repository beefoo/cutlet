"""Script for retrieving dates from transcripts"""

# -*- coding: utf-8 -*-

import argparse
import numpy as np
import matplotlib.pyplot as plt
import torch
from torchvision.io import read_image
from torchvision.models.detection import (
    maskrcnn_resnet50_fpn,
    MaskRCNN_ResNet50_FPN_Weights,
)
from torchvision.transforms.functional import to_pil_image
from torchvision.utils import draw_segmentation_masks

from utilities import *


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-in", dest="INPUT_FILES", default="sample/faces/*.jpg", help="Path to images"
    )
    parser.add_argument(
        "-out",
        dest="OUTPUT_DIR",
        default="output/sample-semantic-segments/",
        help="Output directory",
    )
    parser.add_argument(
        "-threshold",
        dest="SEGMENT_THRESHOLD",
        type=float,
        default=0.95,
        help="Threshold for considering something a threshold (0-1, where 0 gives you everything)",
    )
    parser.add_argument(
        "-mask",
        dest="MASK_THRESHOLD",
        type=float,
        default=0.5,
        help="Threshold for cropping mask",
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


def show(imgs):
    if not isinstance(imgs, list):
        imgs = [imgs]
    fig, axs = plt.subplots(ncols=len(imgs), squeeze=False)
    for i, img in enumerate(imgs):
        img = img.detach()
        img = to_pil_image(img)
        axs[0, i].imshow(np.asarray(img))
        axs[0, i].set(xticklabels=[], yticklabels=[], xticks=[], yticks=[])
    plt.show()


def main(a):
    """Main function to segment a directory of images"""

    if not a.DEBUG:
        # Make sure output dirs exist
        make_directories(a.OUTPUT_DIR)

    if a.CLEAN:
        empty_directory(a.OUTPUT_DIR)

    plt.rcParams["savefig.bbox"] = "tight"

    filenames = get_filenames(a.INPUT_FILES)
    fileCount = len(filenames)
    print(f"{fileCount} files found.")

    weights = MaskRCNN_ResNet50_FPN_Weights.DEFAULT
    transforms = weights.transforms()

    model = maskrcnn_resnet50_fpn(weights=weights, progress=False)
    model = model.eval()

    for i, fn in enumerate(filenames):
        existsFn = f"{a.OUTPUT_DIR}/{get_basename(fn)}-1.png"
        if os.path.isfile(existsFn):
            print(f"Already processed {i+1} of {fileCount}: {fn}")
            continue
        print(f"Processing {i+1} of {fileCount}: {fn}")

        img = transforms(read_image(fn))
        output = model([img])
        output = output[0]
        masks = output["masks"][output["scores"] > a.SEGMENT_THRESHOLD]
        # masks = masks > a.MASK_THRESHOLD
        masks = masks.squeeze(1)

        for mask in masks:
            print(mask.dtype)
            segment_image = to_pil_image(mask)
            print(segment_image.size)
            segment_image.show()
        break


main(parse_args())
