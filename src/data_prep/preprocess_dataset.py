import mido
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
from vectorize_data import midi_to_piano_roll  

# --- Configuration ---
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
DATA_DIR = os.path.join(ROOT_DIR, "data", "groove-v1.0.0-midionly", "groove")
INFO_CSV_PATH = os.path.join(DATA_DIR, "info.csv")
OUTPUT_DIR = os.path.join(ROOT_DIR, "training_data") 

os.makedirs(OUTPUT_DIR, exist_ok=True)

QUANTIZATION_LEVEL = 8
instrument_map = {
    'bass_drum': {'pitches': [35, 36], 'index': 0},
    'snare_drum': {'pitches': [38, 40], 'index': 1},
    'hi_hat': {'pitches': [42, 44, 46], 'index': 2}
}
NUM_INSTRUMENTS = len(instrument_map)


if __name__ == "__main__":
    metadata_df = pd.read_csv(INFO_CSV_PATH)
    
    # Loop through each data split ('train', 'validation', 'test')
    for split in metadata_df['split'].unique():
        print(f"--- Processing {split} set ---")
        split_df = metadata_df[metadata_df['split'] == split]
        print(f"Found {len(split_df)} MIDI files for the {split} set.")
        
        all_piano_rolls = []
        
        for index, row in tqdm(split_df.iterrows(), total=split_df.shape[0]):
            midi_path = os.path.join(DATA_DIR, row['midi_filename'])
            if os.path.exists(midi_path):
                piano_roll, _, _ = midi_to_piano_roll(midi_path, quantization_level=QUANTIZATION_LEVEL, instrument_map=instrument_map, num_instruments=NUM_INSTRUMENTS) 
                if piano_roll is not None and piano_roll.size > 0:
                    all_piano_rolls.append(piano_roll)
        
        # Save the data for the current split into its own file
        output_npz_path = os.path.join(OUTPUT_DIR, f"{split}_data.npz")
        np.savez_compressed(output_npz_path, *all_piano_rolls)
        
        print(f"Successfully processed {len(all_piano_rolls)} files.")
        print(f"{split.capitalize()} data saved to: {output_npz_path}\n")

    print("✅ All dataset processing complete.")