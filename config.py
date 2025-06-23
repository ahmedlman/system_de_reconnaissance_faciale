<<<<<<< HEAD
import os

import customtkinter as ctk

# Base directory configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dataset configuration
DATASET_PATH ='dataset'
display_photo='photo'
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png')
IMG_SIZE = 160  # Image size for model input
MIN_SAMPLES_PER_CLASS = 20  # Minimum images per student
AUGMENTATION_FACTOR = 4  # How many augmented versions to create per image

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

class Theme:
    def set_application_theme(self):
        """Set the application-wide theme using lavender.json and custom styles"""
        # Set global customtkinter theme
        ctk.set_default_color_theme("lavender.json")  # Apply lavender theme
        self.theme = {
            "primary": ["#B19CD9", "#9370DB"],  # From lavender.json CTkButton fg_color
            "secondary": ["gray10", "#DCE4EE"],  # From lavender.json CTkLabel text_color
            "success": "#2ecc71",  # For add buttons, from other files
            "warning": "#f39c12",  # For update buttons, from other files
            "danger": "#e74c3c",  # For delete buttons, from other files
            "background": ["#F9F9FA", "#343638"],  # From lavender.json CTkEntry fg_color
            "sidebar": ["gray86", "gray17"],  # From lavender.json CTkFrame fg_color
            "button_hover": ["#9370DB", "#7A5DC7"],  # From lavender.json CTkButton hover_color
            "font_title": ("Arial", 14, "bold"),  # Match other files
            "font_normal": ("Arial", 12, "bold"),  # Match other files
            "font_large": ("Arial", 28, "bold"),  # For profile pic
            "frame":["gray86", "gray17"]
        }
        return self.theme  # Return the theme dictionary
=======
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
>>>>>>> 263f666345c0bcb90842933d4acc0f0751c416f0
