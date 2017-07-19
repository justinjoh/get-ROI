""" Contains the methods necessary to process one image,
i.e. image --> rectangular ROI
Main usage is in trim.process_single """
import sys
import os
import cv2
import numpy as np
import math
from cleanup_methods import cleanup


def get_lines(grayimg, num_chambers):
    """ Return a list of lines, i.e. 4-tuples in the form:
    (x1, y1, x2, y2)
    General form from:
    http://opencv-python-tutroals.readthedocs.io/en/latest/
    py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    """
    # TODO apply a blurring-type filter first
    blurred_grayimg = cv2.medianBlur(grayimg, 5)
    blurred_grayimg = cv2.medianBlur(blurred_grayimg, 5)
    showImage(blurred_grayimg)
    edges = cv2.Canny(blurred_grayimg, 40, 120)  # Change these params, or create auto-method
    hough_param = 220
    lines_list = []
    # Keep calling with less-restrictive hough_param until get the correct number of chamber lines
    while len(lines_list) < num_chambers*2:
        lines_list = []  # start list over
        lines = cv2.HoughLines(edges, 1, np.pi/180, hough_param) # find all lines with relaxed param
        try:
            for i in range(len(lines)):
                for rho, theta in lines[i]:
                    a = np.cos(theta); b = np.sin(theta)
                    x0 = a * rho; y0 = b * rho
                    x1 = int(x0 + 10000 * (-b)); y1 = int(y0 + 10000 * (a))
                    x2 = int(x0 - 10000 * (-b)); y2 = int(y0 - 10000 * (a))

                    # cv2.line(grayimg, (x1, y1), (x2, y2), (255, 0, 0), 2)
                line = (x1, y1, x2, y2)
                if len(lines_list) == 0:  # Always append the "strongest" line, which is found first
                    lines_list.append(line)

                elif len(lines_list) > 0 and ((slope(line))-(slope(lines_list[-1]))) <= 1:
                    lines_list.append(line)

        except Exception as e:
            print (e)
        hough_param += -2
    # This block just displays the image with lines
    for i in range(len(lines_list)):
        cur_line = lines_list[i]
        x1 = cur_line[0]; y1 = cur_line[1]; x2 = cur_line[2]; y2 = cur_line[3]
        cv2.line(grayimg, (x1, y1), (x2, y2), (255, 255, 0), 1)
    return lines_list


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
    """ Return boolean: l1, l2 are close enough to perpendicular
    Predicted usage: to find end of an individual chamber """
    s1 = slope(l1)
    s2 = slope(l2)
    if s1 == float("inf") or s2 == float("inf"):
        if (-.1 <= s1 <= .1) or (-.1 <= s1 <= .1):
            return True
    if -1.1 <= s1*s2 <= -.9:
        return True
    else:
        return False


def rotate_to_vert(image, lines_list):
    rows, cols = image.shape
    tot_angle = float(0)
    for l in lines_list:
        tot_angle = tot_angle + float(math.atan(slope(l)))
    if len(lines_list) == 0:
        avg_angle = 0
    else:
        avg_angle = float(tot_angle)/float(len(lines_list))
    M = cv2.getRotationMatrix2D((float(cols/2), float(rows/2)), -avg_angle, 1)
    rotated = cv2.warpAffine(image, M, (cols, rows))
    return rotated


def get_first_column(vert_img, l_L, l_R):
    """ vert_img is properly oriented, l_L and l_R are left and right bounds of a channel
    Return the longest possible (along axis of l1 and l2) numpy matrix (extends past
    the longitudinal bounds of the channel, but is not wider than the channel
    Intended usage: probably somewhere near top-level"""
    # TODO vert_lines is not working properly
    vert_lines = get_lines(vert_img, 5)  # Transforming old x-coords would be messy
    sorted_vert = sort_by_xpos(vert_lines)  # Now have list of left-to-right sorted vertical lines
    showImage(vert_img)
    lL = sorted_vert[0]; lR = sorted_vert[1]
    lx = (float(lL[0]) + float(lL[2]))/2
    rx = (float(lR[0]) + float(lR[2]))/2
    print("lx: " + str(lx))
    print("rx: " + str(rx))
    # lx = (float(l_L[0]) + float(l_L[2]))/2
    # rx = (float(l_R[0]) + float(l_R[2]))/2
    try:
        column = vert_img[:, lx:rx]  # [y1:y2, x1:x2]
        print("showing column from get_first_column")
        print("------- vert_lines " + str(vert_lines))
        showImage(column)
    except Exception as e:
        column = vert_img[:, rx:lx]  # [y1:y2, x1:x2]
        print("showing column from get_first_column")
        print("------- vert_lines " + str(vert_lines))
        showImage(column)
    return column


def get_rect_from_column(column):
    """ Input: column, e.g. from get_column
    Return the column, but cropped at the dead end of the column. """
    pass


def sort_by_xpos(lines_list):
    """ Input: valid lines_list, possibly in default format (sorted by confidence)
    Return the same list of lines but sorted from left to right """
    x1_list = []
    for l in lines_list:
        x1_list.append(l[0])
    keys = np.argsort(x1_list)
    l2r_lineslist = []
    for key in keys:
        l2r_lineslist.append(lines_list[key])
    return l2r_lineslist


def showImage(image):
    cv2.imshow('showImage', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def slope(l):
    """ Return the slope of line. If vertical, return infinity float """
    if l[2] == l[0]:
        return float("inf")
    else:
        return (float(l[3])-float(l[1]))/(float(l[2])-float(l[0]))
