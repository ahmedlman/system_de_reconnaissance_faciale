import os

# Base directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset configuration
DATASET_PATH = os.path.join(BASE_DIR, 'dataset')
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
IMG_SIZE = 160  # Image size for model input
MIN_SAMPLES_PER_CLASS = 20  # Minimum images per student
AUGMENTATION_FACTOR = 4  # How many augmented versions to create per image

# Model configuration
MODEL_PATH = os.path.join(BASE_DIR, 'face_model.h5')
LABEL_MAP_PATH = os.path.join(BASE_DIR, 'label_map.npy')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'student_management'
}

# Face detection/recognition configuration
FACE_CONFIG = {
    'camera_index': 0,  # Default camera index
    'total_images': 50,  # Number of images to capture per student
    'recognition_threshold': 0.8  # Confidence threshold for recognition
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