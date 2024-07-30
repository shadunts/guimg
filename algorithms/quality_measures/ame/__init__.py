import cv2
import numpy as np

def AME(image, block_size=15, epsilon=1e-6, modified=False):
    # Initialize an empty list to store the metric values for each block
    metric_values = []

    image = image.astype(np.float32)
    # Iterate over blocks of the image
    height, width = image.shape
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            # Extract the block from the image
            block = image[i:i + block_size, j:j + block_size]

            # Calculate A for the block
            Imin = np.min(block)
            Imax = np.max(block)
            if modified:
                A = epsilon + (Imax - Imin) / 255
            else:
                A = epsilon + (Imax - Imin) / (Imax + Imin + epsilon)

            metric_value = A * np.log(A)

            # Append the metric value to the list
            metric_values.append(metric_value)

    # Calculate the mean of metric values across all blocks
    mean_metric = np.abs(np.nanmean(metric_values))

    return mean_metric

def main(image_path):
    image = cv2.imread(image_path)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return AME(grayscale_image)
