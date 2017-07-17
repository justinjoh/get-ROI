""" Contains the methods necessary to process one image,
i.e. image --> rectangular ROI
Main usage is in trim.process_single """
import sys
import os
import cv2
import numpy as np

def get_lines(grayimg):
    """ Return a list of lines, i.e. 4-tuples in the form:
    (x1, y1, x2, y2)
    General form from:
    http://opencv-python-tutroals.readthedocs.io/en/latest/
    py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    """

    edges = cv2.Canny(grayimg, 15, 45)  # Change these params, or create auto-method
    lines = cv2.Houghlines(edges, 1, np.pi/180, 200)  # May need to change params
    lines_list = []
    for i in len(lines):
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
        line = (x1, y1, x2, y2)
        lines_list.append(line)
    print("Found " + len(lines_list) + " lines")
    return lines_list


def with_most_orth(lines_list):
    """ Return the line in lines_list that is perp to the greatest number of lines
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
    if l[1] == l[0]:
        return float("inf")
    else:
        return (l[3]-l[2])/(l[1]-l[0])

def get_rect(b, s1, s2):
    """ Precondition: b, s1, s2 are such that
    b is perp to s1, s2 (i.e. are_orth)
    s1
    -------------
     b  |
        |
    -------------
    s2
    Will return the longest possible rectangular region that appears to contain cells
    "longest possible" => cuts off at end of image
    "appears to contain cells" => extends to the side of b where there is variance in
        the intensity above some threshold
    """

    pass
