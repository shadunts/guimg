# Image Processor GUI

## Overview

The Image Processor GUI is a Python application that allows users to upload images, apply various image processing
algorithms, and display the results.

## Features

- Upload and display images
- Apply preprocessing algorithms to images
- Apply quality measure algorithms and display results in a table
- Display multiple processed images in a grid
- Run algorithms in a pipeline

## Requirements

- Python 3.11 or higher
- Required Python packages:
    - `tkinter`
    - `PIL`
    - `opencv-python`
    - `torch`
    - `torchvision`
    - `numpy`

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Set the algorithms directory in `main.py` to your local path:**
    ```python
    ALGORITHMS_DIRECTORY = "<SET YOUR PATH HERE>"
    ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Code Structure

- `main.py`: Main application file containing the GUI logic and functionality.
- `algorithms/`: Directory containing categories of algorithms(preprocessing, quality measures, etc.).

## Developer Notes

- **Package Structure**: Each package should contain a `__init__.py` file with a `main` function. The `main` function
  should take `image_path` as its first argument and return either a processed image or a numerical result. Additional
  arguments (args/kwargs) can be passed from the user through the GUI.

- **Importing Modules**: When importing modules within your packages, ensure that you use the full path starting from
  the `algorithms` directory. For example:
  ```python
  from algorithms.preprocessing.Zero_DCE.lowlight_test import lowlight
  ```
- **Adding New Categories**: If you are adding a new category of algorithms (a direct subdirectory
  within `ALGORITHMS_DIRECTORY`), ensure you include the category name in the `PROCESSING_ORDER` list in `main.py`.
- **Adding New Packages**: When adding a new package to an existing category, update the `ALGORITHMS_MAP` dictionary
  in `main.py`. Add the new package name as a key and its parent category name as the value.
