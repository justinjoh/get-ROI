""" Contains the methods necessary to process one image,
i.e. image --> rectangular ROI
Main usage is in trim.process_single """
# import sys
# import os
import cv2
import numpy as np
import math
# from cleanup_methods import cleanup


def get_lines(grayimg, num_chambers):
    """ Return a list of lines, i.e. 4-tuples in the form:
    (x1, y1, x2, y2)
    General form from:
    http://opencv-python-tutroals.readthedocs.io/en/latest/
    py_tutorials/py_imgproc/py_houghlines/py_houghlines.html
    """

    # Blur to reduce influence of lines between cells, then get edges
    blurred_grayimg = cv2.medianBlur(grayimg, 5)
    blurred_grayimg = cv2.medianBlur(blurred_grayimg, 5)
    blurred_grayimg = cv2.medianBlur(blurred_grayimg, 5)
    edges = cv2.Canny(blurred_grayimg, 40, 120)  # Change these params, or create auto-method

    hough_param = 220
    lines_list = []
    # Keep calling with less-restrictive hough_param until get the correct number of chamber lines
    while len(lines_list) < num_chambers*2:
        lines_list = []  # start list over
        lines = cv2.HoughLines(edges, 1, np.pi/180, hough_param)  # find all lines with relaxed param
        # TODO
        # this try/except clause is a clumsy way of avoiding TypeError when lines is initially NoneType
        # Consider changing it
        try:
            for i in range(len(lines)):
                for rho, theta in lines[i]:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 10000 * (-b))
                    y1 = int(y0 + 10000 * a)
                    x2 = int(x0 - 10000 * (-b))
                    y2 = int(y0 - 10000 * a)
                    line = (x1, y1, x2, y2)
                # Now, have candidate line "line". Subject to battery of tests to ensure that "line" is reasonable

                # Always append the "strongest" line as a starting point
                if len(lines_list) == 0:
                    lines_list.append(line)

                # Now, there is  least one line in the list
                # Check for similar slope to first line before trying to add "line"
                elif len(lines_list) > 0 and (abs((slope(line))-(slope(lines_list[0]))) <= 1 or (abs(slope(line)) > 20
                                              and abs(slope(lines_list[0])) > 20)):
                    # determine whether to compare against horiz or vert dim of field
                    if math.atan(slope(lines_list[0])) > 1:
                        min_dist = np.shape(grayimg)[0]/(num_chambers*4)
                    else:
                        min_dist = np.shape(grayimg)[1]/(num_chambers*4)
                    # Perform duplicate check against all lines already in list
                    line_not_duplicate = True
                    for lprev in lines_list:
                        # Perform check of line against lprev
                        # Heuristic: [dist between midpoints of segment] > [min_dist] (min_dist is specified above)
                        p_line = ((line[0]+line[2])/2, (line[1]+line[3])/2)
                        p_lprev = ((lprev[0]+lprev[2])/2, (lprev[1]+lprev[3])/2)
                        dist = math.sqrt((p_line[0]-p_lprev[0])**2 + (p_line[1]-p_lprev[1])**2)
                        if dist >= min_dist:
                            # This line is valid, will append
                            pass
                        else:
                            line_not_duplicate = False
                            break
                    if line_not_duplicate:
                        lines_list.append(line)
                    else:
                        pass
                else:
                    pass
        except Exception as e:
            # print (e)
            pass
        # Relax the parameter used for hough transform (Will cycle again thru "while" if didn't find enough lines)
        hough_param += -2
    return lines_list[0:num_chambers*2]  # hough_param


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
    # TODO can probably keep avg_angle as just the first angle
    rows, cols = image.shape
    tot_angle = float(0)
    for l in lines_list:
        tot_angle = tot_angle + float(math.atan(slope(l)))
    if len(lines_list) == 0:
        avg_angle = 0
    else:
        avg_angle = float(tot_angle)/float(len(lines_list))
    avg_angle = float(math.atan(slope(lines_list[0])))
    M = cv2.getRotationMatrix2D((float(cols/2), float(rows/2)), float(-avg_angle), 1)
    rotated = cv2.warpAffine(image, M, (cols, rows))
    return rotated


def get_first_column(vert_img, num_chambers, **kwargs):
    """ vert_img is properly oriented
    Return the longest possible (along axis of l1 and l2) numpy matrix (extends past
    the longitudinal bounds of the channel, but is not wider than the channel
    Unless directly calling for debugging, should be used in get_column_list"""
    # TODO: ensure that columns are the correct width
    # For now, can assume that all chambers are the same size

    vert_lines = get_lines(vert_img, num_chambers)  # Transforming old x-coords would be messy
    sorted_vert = sort_by_xpos(vert_lines)  # Now have list of left-to-right sorted vertical lines
    lL = sorted_vert[0]
    lR = sorted_vert[1]
    lx = (float(lL[0]) + float(lL[2]))/2
    rx = (float(lR[0]) + float(lR[2]))/2

    if "determined_chamber_width" not in kwargs:
        if lx < rx:
            column = vert_img[:, lx:rx]  # [y1:y2, x1:x2]
        else:
            column = vert_img[:, rx:lx]  # [y1:y2, x1:x2]
        print("width: " + str(abs(rx-lx)))
        height = np.shape(column)[1]
        return column, abs(rx-lx), height
    else:  # "determined_chamber_width" kwarg was passed, i.e. already know what the chamber width is
        width = kwargs["determined_chamber_width"]
        if lx < rx:
            column = vert_img[:, lx-1:lx+width+1]
        else:
            column = vert_img[:, rx-1:rx+width+1]
        height = np.shape(column)[1]
        return column, width, height


def get_column_list(vert_img, num_chambers, **kwargs):
    """ Return a list of all columns (i.e. numpy matrices)
    vert_img should already be properly oriented
    Uses the get_first_column function as the standard """
    columns_list = []
    firstcol, w, h = get_first_column(vert_img, num_chambers)
    # Give option to use an already-determined width
    if "width" in kwargs:
        w = kwargs["width"]
    columns_list.append(firstcol)
    # Now, use the width that has been found to get other chambers
    for c in range(2, num_chambers*2, 2):
        vert_lines = get_lines(vert_img, num_chambers)
        sorted_vert = sort_by_xpos(vert_lines)
        lL = sorted_vert[c]
        lR = sorted_vert[c+1]
        lx = (float(lL[0]) + float(lL[2])) / 2
        rx = (float(lR[0]) + float(lR[2])) / 2
        if lx < rx:
            column = vert_img[:, lx-1:lx+w+1]
        else:
            column = vert_img[:, rx-1:rx+w+1]
        columns_list.append(column)
    return columns_list, w, h


def get_rect_from_column_threshold(column, **kwargs):
    """ Input: single column containing a chamber, e.g. from get_column
    Return the column, but cropped at the "dead end" of the chamber,
    and also the length to which other columns will be cropped if not already found.
    Call with "maxheight" kwarg when already know desired length of chamber
    Note that this only modifies longitudinal dimension """
    # First, find the longitudinal direction of the column
    # TODO also find the correct direction to run from
    # Actually maybe not - should not have to account for 180 degree turns
    # Could run horizontal hough single time and find "center" of image, though
    # could simply take "samples" and go in direction with more stuff
    z = max(np.shape(column)[0], np.shape(column)[1])
    r = min(np.shape(column)[0], np.shape(column)[1])

    if is_upside_down(column):  # If column is "upside down" then just flip along longitudinal axis
        column = column[:][::-1]

    # TODO what might be a better way to calculate threshold?
    transpose = False
    if z == np.shape(column)[0]:  # z is the x-direction
        transpose = True
        column = np.transpose(column)  # transpose column to avoid indexing issues
    threshold = np.mean(column)
    print("get_rect_from_column threshold: " + str(int(threshold)))
    for zpos in range(z):
        row = column[0:r][zpos]
        if ensure_not_text(row) and row_mean > threshold/2:
            # Now know where boundary is
                if "maxheight" in kwargs:
                    h = kwargs["maxheight"]
                    if transpose:
                        return np.transpose(column[:, zpos:zpos+h])
                    else:
                        return column[:, zpos:zpos+h]
                else:
                    if transpose:
                        return np.transpose(column[:, zpos::])
                    else:
                        return column[:, zpos::]

def get_rect_from_column_houghmethod(column, hough_param):
    """ Input: single column containing a chamber, e.g. from get_column
    Return the column, but cropped at the dead end of the chamber.
    Attempts hough line transform at hough parameter that was successful in get_lines """
    raise NotImplementedError


def sort_by_xpos(lines_list):
    """ Input: any valid lines_list, possibly in default format (sorted by decreasing confidence)
    Return the same list of lines but sorted from left to right in image """
    x1_list = []
    for l in lines_list:
        x1_list.append(l[0]+l[2])
    keys = np.argsort(x1_list)
    l2r_lineslist = []
    for key in keys:
        l2r_lineslist.append(lines_list[key])
    return l2r_lineslist


def showImage(image):
    cv2.imshow('showImage', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def showQuickly(image):
    cv2.imshow('showQuickly', image)
    cv2.waitKey(250)
    cv2.destroyAllWindows()


def slope(l):
    """ Return the slope of line 4-tuple. If vertical, return infinity float """
    if l[2] == l[0]:
        return float("inf")
    else:
        return (float(l[3])-float(l[1]))/(float(l[2])-float(l[0]))


def showImage_with_lines(image, lines_list):
    """ Show an image with a given list of lines applied to it"""
    for l in lines_list:
        x1 = l[0]
        y1 = l[1]
        x2 = l[2]
        y2 = l[3]
        cv2.line(image, (x1, y1), (x2, y2), (255, 255, 0), 1)
    showImage(image)


def ensure_not_text(transverse_set):
    """ Return true iff the encountered segment (aligned in transverse direction) does not appear to be text.
    Likely not useful with raw images, but not computationally expensive either.
    heuristic: max colors should not be too small/large"""
    set_max = np.max(transverse_set)
    if set_max >= 254:  # Highly unlikely that near-abs white appears in normal fluo. microscopy images
        return False
    return True
    pass


def is_upside_down(column):
    """ Return true iff the dead end of the chamber is at the bottom of the column """
    # 1. run horizontal hough a single time:
    edges = cv2.Canny(column, 40, 120)
    hough_param = 220
    found = False
    x, y = np.shape(column)
    while not found:
        lines = cv2.HoughLines(edges, 1, np.pi/180, hough_param)
        for i in range(len(lines)):
            for rho, theta in lines[i]:
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 10000 * (-b))
                y1 = int(y0 + 10000 * a)
                x2 = int(x0 - 10000 * (-b))
                y2 = int(y0 - 10000 * a)
                line = (x1, y1, x2, y2)
                if abs(slope(line)) <= .2:
                    zpos = (y1+y2)/2
                    if zpos >= y/2:
                        return False
                    else:
                        return True
        hough_param += -1
    # 2. find the "center" of the image
    # 3. compare the
