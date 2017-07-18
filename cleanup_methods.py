""" NOTE: Probably do not actually need any of this
Contains methods used to "clean up" a lines_list, i.e.
remove lines that are likely not actually there """
import numpy as np
from main import *
# from process_methods import *
import math


def cleanup(lines_list, num_chambers):
    assert num_chambers*2 <= lines_list, "Didn't find enough lines (cleanup)"
    # TODO something going wrong here: check slope-related methods
    """ Return list of the actual lines by using only the (num_chambers*2) lowest scores """
    cleaned_list = []
    avgscore_list = []
    for l1 in lines_list:
        score = 0  # smaller score better
        for l2 in lines_list:
            score = score + pairwise_score(l1, l2)
        avgscore = (score/len(lines_list))**-1
        avgscore_list.append(avgscore)
        print("avgscore: " + str(avgscore))

    keylist = np.argsort(avgscore_list)
    i = 0
    while i < num_chambers*2:
        cleaned_list.append(lines_list[keylist[i]])
        i += 1
    return cleaned_list


def pairwise_score(l1, l2):
    """ Might not actually need this
    return how "similar" the slopes are """
    theta1 = math.atan(slope(l1))
    theta2 = math.atan(slope(l2))
    return (theta1-theta2)**2

def slope(l):
    """ Return the slope of line. If vertical, return infinity """
    if l[1] == l[0]:
        return float("inf")
    else:
        return float(l[3]-l[2])/(l[1]-l[0])