import numpy as np
import cv2


def mean_deviation(image):
    return 1 - np.abs(np.mean(image) - 128) / 128

def main(image_path):
    image = cv2.imread(image_path)
    return mean_deviation(image)
