import mido
import os
import numpy as np
import matplotlib.pyplot as plt
from midi_to_wav import midi_to_wav


# --- Helper Functions ---

def get_notes_from_midi(mid):
    """Extracts all note events from a MIDI file."""
    notes = []
    for track in mid.tracks:
        current_time_ticks = 0
        for msg in track:
            current_time_ticks += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                notes.append({
                    'pitch': msg.note,
                    'start': current_time_ticks,
                    'end': -1 # Placeholder for end time
                })
            elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                # Find the corresponding note_on to set its end time
                for note in reversed(notes):
                    if note['pitch'] == msg.note and note['end'] == -1:
                        note['end'] = current_time_ticks
                        break
    return notes
    
def visualize_piano_roll(piano_roll, output_path, num_instruments=3, instrument_map=None):
    """Saves a visualization of the piano roll."""
    plt.figure(figsize=(20, 5))
    plt.imshow(piano_roll.T, aspect='auto', origin='lower', cmap='viridis')
    plt.yticks(range(num_instruments), [key.replace('_', ' ').title() for key in instrument_map.keys()])
    plt.xlabel('Time Step (Quantized)')
    plt.ylabel('Instrument')
    plt.title('Piano Roll Representation')
    plt.savefig(output_path)
    plt.close()
    print(f"✔️ Saved visualization to {output_path}")

# --- Core Conversion Logic ---

def midi_to_piano_roll(midi_path, quantization_level=8, instrument_map=None, num_instruments=3):
    """
    Quantizes a MIDI file into a simplified numpy array (piano roll).
    
    Returns a tuple of (piano_roll, ticks_per_step, original_ticks_per_beat).
    """
    mid = mido.MidiFile(midi_path)
    notes = get_notes_from_midi(mid)
    
    if not notes:
        return np.array([]), 0, mid.ticks_per_beat

    if instrument_map is None:  
        raise ValueError("instrument_map must be provided")

    # Calculate quantization grid
    ticks_per_beat = mid.ticks_per_beat
    ticks_per_step = ticks_per_beat / quantization_level
    
    # Determine total steps needed
    last_note_end = max(note['end'] for note in notes if note['end'] != -1)
    total_steps = int(np.ceil(last_note_end / ticks_per_step))
    
    # Create the piano roll grid
    piano_roll = np.zeros((total_steps, num_instruments), dtype=np.uint8)

    # Create a reverse map for quick pitch lookup
    pitch_to_instrument = {pitch: details['index'] 
                           for _, details in instrument_map.items() 
                           for pitch in details['pitches']}

    # Populate the grid
    for note in notes:
        if note['pitch'] in pitch_to_instrument:
            instrument_index = pitch_to_instrument[note['pitch']]
            step = int(note['start'] / ticks_per_step)
            if step < total_steps:
                piano_roll[step, instrument_index] = 1
                
    return piano_roll, ticks_per_step, ticks_per_beat

def piano_roll_to_midi(piano_roll, ticks_per_step, ticks_per_beat, output_path):
    """Converts a piano roll numpy array back into a MIDI file."""
    mid = mido.MidiFile(ticks_per_beat=int(ticks_per_beat))
    track = mido.MidiTrack()
    mid.tracks.append(track)
    
    # Map from our index back to a standard MIDI pitch
    index_to_pitch = {
        0: 36,  # Bass Drum
        1: 38,  # Snare
        2: 42   # Hi-Hat
    }
    
    velocity = 100
    ticks_since_last_note = 0
    
    for step_vector in piano_roll:
        notes_to_play = [index_to_pitch[i] for i, active in enumerate(step_vector) if active]
        
        if not notes_to_play:
            ticks_since_last_note += ticks_per_step
        else:
            delta_time = int(ticks_since_last_note + ticks_per_step)
            ticks_since_last_note = 0 # Reset time
            
            # Add all notes for this step
            for i, pitch in enumerate(notes_to_play):
                # The first note carries the delta time, others are simultaneous
                track.append(mido.Message('note_on', note=pitch, velocity=velocity, time=delta_time if i == 0 else 0, channel=9))
            
            # Add corresponding note_off messages immediately
            for pitch in notes_to_play:
                 track.append(mido.Message('note_off', note=pitch, velocity=velocity, time=0, channel=9))

    mid.save(output_path)
    print(f"✔️ Saved reconstructed MIDI to {output_path}")

# # --- Configuration ---

# # Adjust these paths based on your project structure
# ROOT_DIR = os.path.join(os.path.dirname(__file__), '..', '..') # Assumes script is in src/data_prep
# DATA_DIR = os.path.join(ROOT_DIR, "data", "groove-v1.0.0-midionly", "groove")
# OUTPUT_DIR = os.path.join(ROOT_DIR, "output") 
# SOUNDFONT_PATH = os.path.join(ROOT_DIR, "config", "TSC-105.sf2")

# # Ensure the output directory exists
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# # Quantization level: 8 splits each quarter note into 8 steps (32nd notes)
# QUANTIZATION_LEVEL = 8

# # Instrument mapping: Define which MIDI notes correspond to which drum part
# # This simplifies the complex drum kit into three main parts.
# instrument_map = {
#     'bass_drum': {'pitches': [35, 36], 'index': 0},
#     'snare_drum': {'pitches': [38, 40], 'index': 1},
#     'hi_hat': {'pitches': [42, 44, 46], 'index': 2} # Closed, Pedal, Open
# }
# NUM_INSTRUMENTS = len(instrument_map)
# # --- Main Execution ---

# if __name__ == "__main__":
#     # 1. Select a MIDI file from your dataset
#     filename = "1_funk_80_beat_4-4"
#     midi_filename = filename + ".mid"
#     original_midi_path = os.path.join(DATA_DIR, "drummer1", "session1", midi_filename)
    
#     print(f"Processing: {original_midi_path}")
    
#     # 2. Convert the MIDI to a quantized piano roll
#     piano_roll, ticks_per_step, original_tpb = midi_to_piano_roll(original_midi_path)
#     print(f"Created piano roll with shape: {piano_roll.shape}")
    
#     # 3. (Optional) Visualize the piano roll
#     viz_path = os.path.join(OUTPUT_DIR, f"viz_pianoroll_{filename}.png")
#     visualize_piano_roll(piano_roll, viz_path)
    
#     # 4. Convert the piano roll back to a MIDI file to check for loss
#     reconstructed_midi_path = os.path.join(OUTPUT_DIR, "reconstructed_" + midi_filename)
#     piano_roll_to_midi(piano_roll, ticks_per_step, original_tpb, reconstructed_midi_path)
    
#     print("\nProcess complete. 🥁 You can now listen to:")
#     print(f" - Original: {original_midi_path}")
#     print(f" - Reconstructed: {reconstructed_midi_path}")

#     midi_to_wav(
#         soundfont_path=SOUNDFONT_PATH, 
#         midi_path=reconstructed_midi_path, 
#         output_wav_path=os.path.join(OUTPUT_DIR, f"reconstructed_{filename}.wav")
#     )

#     print("✔️ MIDI to WAV conversion complete.")