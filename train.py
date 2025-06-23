import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.model_selection import train_test_split
import numpy as np
import os
import cv2
from datetime import datetime
import matplotlib.pyplot as plt
from config import *
from tqdm import tqdm

class FaceTrainer:
    def __init__(self):
        self.model = None
        self.label_map = {}
        self.reverse_label_map = {}
        self.history = None

    def load_training_data(self):
        """Load and preprocess training data with augmentation"""
        images, labels = [], []

        # Load label map if exists
        if os.path.exists(LABEL_MAP_PATH):
            self.label_map = np.load(LABEL_MAP_PATH, allow_pickle=True).item()
            self.reverse_label_map = {v: k for k, v in self.label_map.items()}
            next_label_id = max(self.label_map.values()) + 1 if self.label_map else 0
        else:
            next_label_id = 0

        class_counts = {}
        for folder in os.listdir(DATASET_PATH):
            folder_path = os.path.join(DATASET_PATH, folder)
            if not os.path.isdir(folder_path):
                continue

            # Extract student ID from folder name (format: studentID_name_teacherID_name)
            student_id = folder.split("_")[0]
            if student_id not in self.label_map:
                self.label_map[student_id] = next_label_id
                self.reverse_label_map[next_label_id] = student_id
                next_label_id += 1
                class_counts[student_id] = 0

            for img_name in os.listdir(folder_path):
                if not img_name.lower().endswith(tuple(VALID_IMAGE_EXTENSIONS)):
                    continue

                img_path = os.path.join(folder_path, img_name)
                try:
                    img = cv2.imread(img_path)
                    if img is None:
                        continue
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))

                    # Original
                    images.append(img / 255.0)
                    labels.append(self.label_map[student_id])
                    class_counts[student_id] += 1

                    # Augmented
                    for _ in range(AUGMENTATION_FACTOR):
                        augmented = self.augment_image(img)
                        images.append(augmented / 255.0)
                        labels.append(self.label_map[student_id])
                        class_counts[student_id] += 1

                except Exception as e:
                    print(f"Error processing {img_path}: {e}")
                    continue

        # Warn if any class has too few samples
        for student_id, count in class_counts.items():
            if count < MIN_SAMPLES_PER_CLASS:
                print(f"⚠️ Warning: Class {student_id} has only {count} samples")

        if not images:
            raise ValueError("No training data found.")

        return np.array(images), np.array(labels)

    def augment_image(self, img):
        """Random image augmentations"""
        if np.random.rand() > 0.5:
            img = cv2.flip(img, 1)

        angle = np.random.uniform(-15, 15)
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        img = cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)

        alpha = np.random.uniform(0.8, 1.2)
        beta = np.random.uniform(-10, 10)
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        return img

    def create_model(self, num_classes):
        """Create MobileNetV2-based model"""
        base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(IMG_SIZE, IMG_SIZE, 3))
        base_model.trainable = False

        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dropout(0.3)(x)
        output = Dense(num_classes, activation='softmax')(x)

        model = Model(inputs=base_model.input, outputs=output)
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])
        return model

    def train(self, epochs=20, batch_size=32):
        """Train and save model"""
        print(f"\n[{datetime.now()}] 🚀 Starting training...")

        X, y = self.load_training_data()
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

        self.model = self.create_model(len(self.label_map))

        callbacks = [
            EarlyStopping(patience=5, restore_best_weights=True),
            ModelCheckpoint(MODEL_PATH, monitor='val_accuracy', mode='max', save_best_only=True)
        ]

        print(
            f"🧐 Training on {len(X_train)} samples | Validating on {len(X_val)} samples | Classes: {len(self.label_map)}")

        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )

        # Save model and label map
        np.save(LABEL_MAP_PATH, self.label_map)
        self.model.save(MODEL_PATH)

        print(f"✅ Training complete. Model saved to {MODEL_PATH}")
        print(f"📁 Label map saved to {LABEL_MAP_PATH}")
        return self.model

    def plot_training_history(self):
        """Plot accuracy and loss"""
        if self.history is None:
            print("No training history found.")
            return

        plt.figure(figsize=(12, 5))

        # Accuracy plot
        plt.subplot(1, 2, 1)
        plt.plot(self.history.history['accuracy'], label='Train')
        plt.plot(self.history.history['val_accuracy'], label='Validation')
        plt.title('Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()

        # Loss plot
        plt.subplot(1, 2, 2)
        plt.plot(self.history.history['loss'], label='Train')
        plt.plot(self.history.history['val_loss'], label='Validation')
        plt.title('Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()

        plt.tight_layout()
        plt.show()

    def train_model(self):
        """Main function to trigger training"""
        try:
            model = self.train(epochs=15, batch_size=16)
            self.plot_training_history()
            return model
        except Exception as e:
            print(f"❌ Error during training: {e}")
            raise