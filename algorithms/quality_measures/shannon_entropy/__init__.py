import numpy as np
import cv2


def shannon_entropy(image):
    # Convert image to grayscale
    if len(image.shape) == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image

    # Calculate histogram
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])

    # Compute probability of each intensity level
    hist = hist.ravel() / hist.sum()

    # Compute Shannon entropy
    entropy = -np.sum(hist * np.log2(hist + 1e-10))  # Adding a small value to avoid log(0)

    return entropy


def main(image_path):
    image = cv2.imread(image_path)
    return shannon_entropy(image)
