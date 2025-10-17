import mido
import os
import numpy as np
import matplotlib.pyplot as plt
from midi_to_wav import midi_to_wav # Assuming midi_to_wav.py is in the same folder

# --- Configuration ---
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..')
DATA_DIR = os.path.join(ROOT_DIR, "data", "groove-v1.0.0-midionly", "groove")
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")
SOUNDFONT_PATH = os.path.join(ROOT_DIR, "config", "TSC-105.sf2") # Or your preferred soundfont

os.makedirs(OUTPUT_DIR, exist_ok=True)

QUANTIZATION_LEVEL = 8
instrument_map = {
    'bass_drum': {'pitches': [35, 36], 'index': 0},
    'snare_drum': {'pitches': [38, 40], 'index': 1},
    'hi_hat': {'pitches': [42, 44, 46], 'index': 2}
}
NUM_INSTRUMENTS = len(instrument_map)

# --- Import your conversion functions here (or define them as before) ---
# For brevity, assuming they are defined as in the previous examples
from vectorize_data import get_notes_from_midi, midi_to_piano_roll, piano_roll_to_midi, visualize_piano_roll


if __name__ == "__main__":
    # 1. Select a MIDI file to test
    filename = "1_funk_80_beat_4-4"
    midi_filename = filename + ".mid"
    original_midi_path = os.path.join(DATA_DIR, "drummer1", "session1", midi_filename)
    
    print(f"Processing: {original_midi_path}")
    
    # 2. Convert the MIDI to a quantized piano roll
    # Note: Using the function from vectorize_data which returns multiple values
    mid = mido.MidiFile(original_midi_path)
    piano_roll, ticks_per_step, original_tpb = midi_to_piano_roll(original_midi_path, quantization_level=QUANTIZATION_LEVEL, instrument_map=instrument_map, num_instruments=NUM_INSTRUMENTS)
    print(f"Created piano roll with shape: {piano_roll.shape}")
    
    # 3. Visualize the piano roll
    viz_path = os.path.join(OUTPUT_DIR, f"viz_{filename}.png")
    visualize_piano_roll(piano_roll, viz_path, num_instruments=NUM_INSTRUMENTS, instrument_map=instrument_map)
    
    # 4. Convert the piano roll back to a MIDI file
    reconstructed_midi_path = os.path.join(OUTPUT_DIR, f"reconstructed_{filename}.mid")
    piano_roll_to_midi(piano_roll, ticks_per_step, original_tpb, reconstructed_midi_path)
    
    # 5. Convert the reconstructed MIDI to a WAV file to hear it
    reconstructed_wav_path = os.path.join(OUTPUT_DIR, f"reconstructed_{filename}.wav")
    midi_to_wav(
        soundfont_path=SOUNDFONT_PATH, 
        midi_path=reconstructed_midi_path, 
        output_wav_path=reconstructed_wav_path
    )

    print(f"\n✅ Single file test complete. Check the '{OUTPUT_DIR}' folder.")