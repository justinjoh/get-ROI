import sys
import os
import cv2
import numpy as np
from main import *
from process_methods import *


if __name__ == '__main__':
    flist = get_file_list() # returns the list of file names
    for img_name in flist:

        f = cv2.imread(img_name, cv2.IMREAD_GRAYSCALE)
        lines_list = get_lines(f, num_chambers=5)
        # showImage(f)
        rotated = rotate_to_vert(cv2.imread(img_name, cv2.IMREAD_GRAYSCALE), lines_list)
        showImage(rotated)

#        test_list = get_lines(f, num_chambers=10)
#        showImage()

        # At this point, image is properly oriented.
        #    Can do hough line again to get exact vertical slice coordinates
        # Something here to get individual numpy matrices
        # Need to figure out where to slice horizontally, in each numpy matrix

    pass


