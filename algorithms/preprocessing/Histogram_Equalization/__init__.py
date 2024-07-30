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


def main(image):
    img = cv2.imread(image, 1)
    # Covert to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split((hsv))
    hist_v = hist_equalization(v)
    # Merge back the channel
    merged_hist = cv2.merge((h, s, hist_v))
    hist = cv2.cvtColor(merged_hist, cv2.COLOR_HSV2BGR)

    return hist
