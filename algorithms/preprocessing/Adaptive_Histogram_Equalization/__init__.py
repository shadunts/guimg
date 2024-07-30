import cv2
import numpy as pb
import os


def hist_equalization(img):
    """ Normal Histogram Equalization

    Args:
        img : image input with single channel

    Returns:
        : Equalized Image
    """
    array = pb.asarray(img)
    bin_cont = pb.bincount(array.flatten(), minlength=256)
    pixels = pb.sum(bin_cont)
    bin_cont = bin_cont / pixels
    cumulative_sumhist = pb.cumsum(bin_cont)
    map = pb.floor(255 * cumulative_sumhist).astype(pb.uint8)
    arr_list = list(array.flatten())
    eq_arr = [map[p] for p in arr_list]
    arr_back = pb.reshape(pb.asarray(eq_arr), array.shape)
    return arr_back


def ahe(img, rx=136, ry=185):
    """ Adaptive Histogram Equalization

    Args:
        img : image input with single channel
        rx (int, optional): to divide horizontal regions, Note: Should be divisible by image size in x . Defaults to 136.
        ry (int, optional): to divide vertical regions, Note: Should be divisible by image size in y. Defaults to 185.

    Returns:
        : Equalized Image
    """
    v = img
    img_eq = pb.empty((v.shape[0], v.shape[1]), dtype=pb.uint8)
    for i in range(0, v.shape[1], rx):
        for j in range(0, v.shape[0], ry):
            t = v[j:j + ry, i:i + rx]
            c = hist_equalization(t)
            img_eq[j:j + ry, i:i + rx] = c
    return img_eq


def main(image):
    img = cv2.imread(image, 1)
    # Covert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split((hsv))
    ahe_v = ahe(v)
    merged_ahe = cv2.merge((h, s, ahe_v))
    ahe_img = cv2.cvtColor(merged_ahe, cv2.COLOR_HSV2BGR)

    return ahe_img
