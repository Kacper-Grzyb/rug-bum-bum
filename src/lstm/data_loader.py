import numpy as np
import os

def load_dataset(npz_path, sequence_length=32):
    """
    Loads data from a specified .npz file and creates fixed-length sequences
    for LSTM training, validation, or testing.

    Args:
        npz_path (str): The full path to the .npz file.
        sequence_length (int): The number of time steps in each input sequence.

    Returns:
        A tuple (X, y) of NumPy arrays, where X is the input sequences
        and y is the corresponding target steps.
    """
    if not os.path.exists(npz_path):
        raise FileNotFoundError(f"Dataset file not found at {npz_path}")

    print(f"Loading and preparing data from {os.path.basename(npz_path)}...")
    with np.load(npz_path, allow_pickle=True) as data:
        # data.files provides the keys: ['arr_0', 'arr_1', ...]
        piano_rolls = [data[key] for key in data.files]

    all_sequences = []
    all_targets = []

    # Iterate through each song's piano roll to create "sliding windows"
    for roll in piano_rolls:
        if len(roll) > sequence_length:
            for i in range(len(roll) - sequence_length):
                # The input sequence (e.g., 32 steps)
                seq = roll[i : i + sequence_length]
                all_sequences.append(seq)
                
                # The single step that the model should predict
                target = roll[i + sequence_length]
                all_targets.append(target)
            
    # Convert lists into final NumPy arrays for the model
    X = np.array(all_sequences)
    y = np.array(all_targets)
    
    print(f"Created {len(X)} samples.")
    print(f"  X shape: {X.shape}") # (num_samples, sequence_length, num_instruments)
    print(f"  y shape: {y.shape}") # (num_samples, num_instruments)
    
    return X, y

if __name__ == '__main__':
    # This part is for testing the data loader directly
    print("--- Testing Data Loader ---")
    ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
    TRAIN_NPZ = os.path.join(ROOT_DIR, "output", "train_data.npz")
    
    # Example of how to use the function
    X_train, y_train = load_dataset(TRAIN_NPZ, sequence_length=64)