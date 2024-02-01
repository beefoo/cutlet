# -*- coding: utf-8 -*-

from utilities import *

filenames = get_filenames("output/met-sculptures/*.jpg")
for filename in filenames:
    meta = read_image_meta(
        filename,
        [
            ("ImageDescription", "title"),
            ("Artist", "artistDisplayName"),
            ("DateTime", "objectDate"),
            ("ImageID", "objectURL"),
        ],
    )
    print(filename)
    print(meta)
    print("----------------------")
