"""Create a new folder of images that consist of only the cell chamber
Name of save folder is specified in commandline"""
import sys
import os
import cv2
import numpy as np

if __name__ == '__main__':
    # might want to add options for other arguments
    assert len(sys.argv) == 2
    saveFolderName = sys.argv[1]
    # call a function that will return a list of numpy matrices
    # create the folder
    if not os.path.exists(saveFolderName):
        os.makedirs(saveFolderName)
    # for np matrix in list, save

    pass


def return_numpy_list():
    """Return list of np matrices representing each image ROI"""
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


def process_single(fname):
    f = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)  # Need grayscale for Hough line transform

    pass
