"""Script for verifying successful installation"""

import argparse
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
import torch
import torchvision


def parse_args():
    """Function to parse script arguments"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-model", dest="MODEL", default="vit_h", help="Model used")
    parser.add_argument(
        "-checkpoint",
        dest="MODEL_CHECKPOINT",
        default="models/sam_vit_h_4b8939.pth",
        help="Path to checkpoint file",
    )
    parser.add_argument(
        "-image",
        dest="IMAGE",
        default="sample/98518549.jpg",
        help="Path to image",
    )
    args = parser.parse_args()
    return args


def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x["area"]), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones(
        (
            sorted_anns[0]["segmentation"].shape[0],
            sorted_anns[0]["segmentation"].shape[1],
            4,
        )
    )
    img[:, :, 3] = 0
    for ann in sorted_anns:
        m = ann["segmentation"]
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)


def main(a):
    """Main function to print verification details"""

    print("PyTorch version:", torch.__version__)
    print("Torchvision version:", torchvision.__version__)
    print("CUDA is available:", torch.cuda.is_available())

    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    sam = sam_model_registry[a.MODEL](checkpoint=a.MODEL_CHECKPOINT)
    sam.to(device="cuda")
    mask_generator = SamAutomaticMaskGenerator(sam)
    image = cv2.imread(a.IMAGE)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    masks = mask_generator.generate(image)
    plt.figure(figsize=(20, 20))
    plt.imshow(image)
    show_anns(masks)
    plt.axis("off")
    plt.show()


main(parse_args())
