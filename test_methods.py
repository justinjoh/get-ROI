# import sys
# import os
# import cv2
# import numpy as np
import argparse
from main import *
from process_methods import *

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("NumberOfChambers", help="The number of chambers that are in the images", type=int)
args = parser.parse_args()
print("Running with " + str(args.NumberOfChambers) + " chambers")

if __name__ == '__main__':
    flist = get_file_list()  # returns the list of file names
    namecounter = 0
    for img_name in flist:
        f = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)  # Read in the file as grayscale
        lines_list = get_lines(f, num_chambers=args.NumberOfChambers)  # Create lines_list for later use
        assert len(lines_list) == 10, "didn't fin    # might want to add options for other argumentsd correct number of lines"
        showImage_with_lines(f, lines_list)    # might want to add options for other arguments
        xsorted = sort_by_xpos(lines_list)  # TODO where is xsorted even used?
        rotated = rotate_to_vert(cv2.imread(img_name, cv2.IMREAD_GRAYSCALE), lines_list)
        # showImage_with_lines(rotated, get_lines(rotated, num_chambers=args.NumberOfChambers))
        firstcol, w, h = get_first_column(rotated, num_chambers=args.NumberOfChambers, determined_chamber_width=75)
        # showImage_with_lines(firstcol, get_lines(firstcol, num_chambers=1))
        showImage(firstcol)

        rect = get_rect_from_column_threshold(firstcol)
        showImage(rect)
        cv2.imwrite(str(namecounter) + '.png', rect)
        print(np.shape(rect))
        namecounter += 1
