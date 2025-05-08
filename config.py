import os

# Base directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset configuration
DATASET_PATH ='dataset'
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
IMG_SIZE = 160  # Image size for model input
MIN_SAMPLES_PER_CLASS = 20  # Minimum images per student
AUGMENTATION_FACTOR = 4  # How many augmented versions to create per image

# Face detection/recognition configuration
FACE_CONFIG = {
    'camera_index': 1,  # Default camera index
}

# UI configuration
UI_CONFIG = {
    'preview_size': (640, 480),
    'button_colors': {
        'capture': ('#4CC9F0', '#4895EF'),
        'train': ('#7209B7', '#560BAD'),
        'stop': ('#F72585', '#B5179E')
    }
}
TOTAL_IMAGES = 50