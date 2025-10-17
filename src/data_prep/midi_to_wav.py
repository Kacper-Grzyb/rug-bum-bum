import os
import subprocess

def midi_to_wav(soundfont_path, midi_path, output_wav_path):
    """
    Converts a MIDI file to a WAV file by calling the fluidsynth command-line tool.
    This method is robust and not dependent on specific library versions.
    """
    if not os.path.exists(soundfont_path):
        print(f"Error: SoundFont file not found at {soundfont_path}")
        return
    if not os.path.exists(midi_path):
        print(f"Error: MIDI file not found at {midi_path}")
        return

    print(f"Converting {os.path.basename(midi_path)} to WAV...")

    # The command to execute: fluidsynth -ni [soundfont] [midi] -F [wav_out]
    command = [
        'fluidsynth',
        '-ni',
        soundfont_path,
        midi_path,
        '-F',
        output_wav_path
    ]

    try:
        # Run the command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if result.stderr:
            # Print warnings, but not as an error
            print(f"Fluidsynth warnings:\n{result.stderr}")
        print(f"✔️ Successfully created {os.path.basename(output_wav_path)}")

    except FileNotFoundError:
        print("Error: 'fluidsynth' command not found.")
        print("Please ensure FluidSynth is installed and accessible in your system's PATH.")
        
    except subprocess.CalledProcessError as e:
        # This catches errors from the fluidsynth command itself
        print(f"Error during MIDI to WAV conversion.")
        print(f"Command failed with exit code {e.returncode}")
        print(f"Stderr: {e.stderr}")