import numpy as np
import cv2


def mean_deviation(image):
    return 1 - np.abs(np.mean(image) - 128) / 128


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


def BIE(image, block_size=15):
    # Calculate the number of blocks in the image
    num_blocks_height = image.shape[0] // block_size
    num_blocks_width = image.shape[1] // block_size

    block_entropies = []
    block_contrasts = []

    # Iterate through blocks and calculate entropy
    for i in range(num_blocks_height):
        for j in range(num_blocks_width):
            block = image[i * block_size:(i + 1) * block_size, j * block_size:(j + 1) * block_size]
            block_entropy = shannon_entropy(block)
            block_contrast = np.std(block)
            block_entropies.append(block_entropy)
            block_contrasts.append(block_contrast)

    # Calculate mean entropy across blocks
    mean_block_entropy = np.mean(block_entropies)
    mean_block_contrast = np.mean(block_contrasts)

    # Calculate AME of the entire image
    image_entropy = AME(image, block_size, modified=True)

    std = np.std(image)

    print("image entropy", image_entropy, "mean_block_entropy", mean_block_entropy,
          "sdt", std, "block_sdt", mean_block_contrast)

    m = mean_deviation(image)

    p = m * std / (np.mean(block_contrasts) + 1)

    # Calculate the metric
    metric = p * image_entropy / (1 + mean_block_entropy)
    return metric

def main(image_path, block_size=15):
    image = cv2.imread(image_path)
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return BIE(grayscale_image, block_size=block_size)
