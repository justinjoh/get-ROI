""" Contains the methods necessary to process one image,
i.e. image --> rectangular ROI
Main usage is in trim.process_single """
import sys
import os
import cv2
import numpy as np
from cleanup_methods import cleanup


def get_lines(grayimg, num_chambers):
    """ Return a list of lines, i.e. 4-tuples in the form:
    (x1, y1, x2, y2)
    General form from:
    http://opencv-python-tutroals.readthedocs.io/en/latest/
    py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    """
    # TODO need a method that will discard lines that don't fit with the others
    edges = cv2.Canny(grayimg, 40, 120)  # Change these params, or create auto-method
    hough_param = 220
    lines_list = []
    # Keep calling with less-restrictive hough_param until get the correct number of chamber lines
    while len(lines_list) < num_chambers*2+1:
        lines_list = []  # start list over
        lines = cv2.HoughLines(edges, 1, np.pi/180, hough_param)

        for i in range(len(lines)):
            for rho, theta in lines[i]:
                a = np.cos(theta)
                b = np.sin(theta)
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 10000 * (-b))
                y1 = int(y0 + 10000 * (a))
                x2 = int(x0 - 10000 * (-b))
                y2 = int(y0 - 10000 * (a))

                # cv2.line(grayimg, (x1, y1), (x2, y2), (255, 0, 0), 2)
            line = (x1, y1, x2, y2)
            print(str(float(slope(line))))
            if len(lines_list) == 0:
                lines_list.append(line)
            if len(lines_list) == 2:
                pass

            if len(lines_list) > 0 and ((slope(line))-(slope(lines_list[i-1]))) <= 1:
                lines_list.append(line)
        hough_param += -1

    for i in range(len(lines_list)):
        cur_line = lines_list[i]
        x1 = cur_line[0]; y1 = cur_line[1]; x2 = cur_line[2]; y2 = cur_line[3]
        cv2.line(grayimg, (x1, y1), (x2, y2), (255, 0, 0), 0)


def with_most_orth(lines_list):
    """ Might not actually need this for anything
    Return the line in lines_list that is perp to the greatest number of lines
    in the list
    Known uses: find the line parallel to the flow chamber """
    best_index = 0
    best_score = 0
    for i in range(len(lines_list)):
        i_score = 0
        for j in range(len(lines_list)):
            if are_orth(lines_list[i], lines_list[j]):
                i_score += 1
        if i_score > best_score:
            best_index = i
    return lines_list[best_index]


def are_orth(l1, l2):
    """ Return boolean: l1, l2 are close enough to perpendicular """
    s1 = slope(l1)
    s2 = slope(l2)
    if s1 == float("inf") or s2 == float("inf"):
        if (-.1 <= s1 <= .1) or (-.1 <= s1 <= .1):
            return True
    if -1.1 <= s1*s2 <= -.9:
        return True
    else:
        return False


def slope(l):
    """ Return the slope of line. If vertical, return infinity """
    if l[2] == l[0]:
        return float("inf")
    else:
        return float(l[3]-l[1])/float(l[2]-l[0])


def get_rect(image, l1, l2):
    """ Might not actually need this in the current form: first want to rotate entire image
    to the right angle
    Precondition: l1 and l2 do actually correspond to a desired ROI"""
    # First, create largest possible rectangle -> np matrix
    # Apply Hough line transform to this
    #   Use this new line to

    pass


def showImage(image):
    cv2.imshow('showImage', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
