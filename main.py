"""Create a new folder of images that consist of only the cell chamber
Name of save folder is specified in commandline"""
import sys
import os
import cv2
import numpy as np

from process_methods import *

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("NumberOfChambers", help="The number of chambers that are in the images",
                    type=int)
parser.add_argument("SaveFolderName", help="The folder where sets of chambers will be saved",
                    type=str)
args = parser.parse_args()
print("Running with " + str(args.NumberOfChambers) + " chambers")
print("Will save to (possibly new) folder " + args.SaveFolderName + " within current directory")


def get_numpy_list():
    """Return list of lists of np matrices representing each image's ROIs"""
    # TODO may not actually need this
    numpy_list = []
    # get files from other function
    # process each file, append result to list
    return numpy_list


def get_file_list():
    """Return list of all .tif files in the current directory"""
    file_list = []
    for fname in os.listdir("./"):
        if fname.endswith(".tif"):
            print("Found " + fname)
            file_list.append(fname)
    return file_list


def process_single(fname, **kwargs):
    """ Return a list of np matrices for one image.
    Call with kwargs width and height if dimensions of chamber known"""
    # TODO distinction between pixel and actual dimensions
    #   Might not be within this function
    numchambers = args.NumberOfChambers
    # TODO put this in later location
    nplist_from_single = []  # will return this
    f = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)  # Need grayscale for Hough line transform
    lines_list = get_lines(f, num_chambers=numchambers)
    rotated = rotate_to_vert(f, lines_list)
    hlist = []
    rlist = []
    # Case 1: neither width nor height known
    # TODO this is computationally wasteful, consider adding function to find maxheight
    if "width" not in kwargs and "height" not in kwargs:
        print("neither width nor height specified for " + str(fname))
        column_list, w, h = get_column_list(rotated, num_chambers=numchambers)
        for col in column_list:
            r = get_rect_from_column_threshold(col)
            hlist.append(np.shape(r)[0])
        h = min(hlist)  # height to use again in get_rect_from column
        for i in range(len(hlist)):
            rnew = get_rect_from_column_threshold(column_list[i], maxheight=h)
            nplist_from_single.append(rnew)
        return nplist_from_single, w, h
    elif "width" in kwargs and "height" in kwargs:
        column_list, _, _ = get_column_list(rotated, numchambers=numchambers)
        for col in column_list:
            r = get_rect_from_column_threshold(col, maxheight=kwargs["height"])
            rlist.append(r)
        return rlist, kwargs["width"], kwargs["height"]
    else:  # if one specified and not the other
        raise NotImplementedError, "process_single: specify either both height and width or neither"


if __name__ == '__main__':
    # TODO should call with kwargs at some point
    # TODO figure out how to handle text better
    flist = get_file_list()
    if not os.path.exists(args.SaveFolderName):
        os.makedirs(args.SaveFolderName)
    for img_name in flist:
        matlist, _, _ = process_single(img_name)
        for l in matlist:
            showQuickly(l)
    pass
