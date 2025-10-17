import os
from data_loader import load_dataset

  # --- Configuration ---
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
SEQUENCE_LENGTH = 32

if __name__ == "__main__":
  # --- Load Data ---
  # Call the function for each data split you need
  X_train, y_train = load_dataset(os.path.join(OUTPUT_DIR, 'train_data.npz'), SEQUENCE_LENGTH)
  X_val, y_val = load_dataset(os.path.join(OUTPUT_DIR, 'validation_data.npz'), SEQUENCE_LENGTH)