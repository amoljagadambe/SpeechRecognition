import numpy as np
from numpy import array, zeros, argmin, inf
from fuzzywuzzy import fuzz
from nltk.util import ngrams
from difflib import SequenceMatcher as SM


def text_matching(text1, text2):
    test1 = str(text1).lower()
    test2 = str(text2).lower()
    # rate = fuzz.partial_ratio(test1, test2)
    rate = fuzz.ratio(test1, test2)  # partial_ratio
    # print("Matching score: {}".format(rate))
    return rate


def text_partial_matching(text1, text2):
    test1 = str(text1).lower()
    test2 = str(text2).lower()
    rate = fuzz.partial_ratio(test1, test2)
    # rate = fuzz.ratio(test1, test2)  # partial_ratio
    # print("Matching score: {}".format(rate))
    return rate


def text_dtw(dist_mat, warp=1):
    r, c = len(dist_mat), len(dist_mat[0])
    D0 = zeros((r + 1, c + 1))
    D0[0, 1:] = inf
    D0[1:, 0] = inf
    # D1 = dist_mat
    D1 = D0[1:, 1:]
    for i in range(r):
        for j in range(c):
            D1[i, j] = dist_mat[i, j]
    C = D1.copy()
    for i in range(r):
        for j in range(c):
            min_list = [D0[i, j]]
            for k in range(1, warp + 1):
                i_k = min(i + k, r - 1)
                j_k = min(j + k, c - 1)
                min_list += [D0[i_k, j], D0[i, j_k]]
            D1[i, j] += min(min_list)

    path = _traceback(D0)

    return D1[-1, -1] / sum(D1.shape), C, D1, path


def _traceback(D):
    i, j = array(D.shape) - 2
    p, q = [i], [j]
    while (i > 0) or (j > 0):
        tb = argmin((D[i, j], D[i, j+1], D[i+1, j]))
        if tb == 0:
            i -= 1
            j -= 1
        elif tb == 1:
            i -= 1
        else:  # (tb == 2):
            j -= 1
        p.insert(0, i)
        q.insert(0, j)
    return array(p), array(q)


def get_DTW_path_from_strings(sentence1, sentence2):
    # calculate distance matrix between sentence1 and sentence2
    text1 = str(sentence1).split(' ')
    text2 = str(sentence2).split(' ')

    return get_DTW_path(text1, text2)


def get_DTW_path(list1, list2):
    dim1 = len(list1)
    dim2 = len(list2)
    dist_mat = np.zeros((dim1, dim2))
    for x in range(dim1):
        for y in range(dim2):
            sc = text_matching(list1[x], list2[y])
            sc = 100 - sc
            dist_mat[x][y] = sc

    # find segment alignment using DTW
    dist, cost, acc, path = text_dtw(dist_mat)
    return path

