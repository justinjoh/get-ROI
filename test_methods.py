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
        showImage(f)
        xsorted = sort_by_xpos(lines_list)
        rotated = rotate_to_vert(cv2.imread(img_name, cv2.IMREAD_GRAYSCALE), lines_list)
        (get_first_column(rotated, xsorted[0], xsorted[1]))

    pass


