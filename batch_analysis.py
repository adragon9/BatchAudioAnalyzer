import librosa
# Freeze librosa
import os, platform, subprocess, json
from typing import Literal
from pathlib import Path
from tkinter import filedialog

def clear():
    cmd = "cls" if platform.system() == "Windows" else "clear"
    subprocess.run(cmd, shell=True)

def get_folder():
    return filedialog.askdirectory()

def analyze_music(file: Path) -> dict:
    # just in case
    if not os.path.exists(file):
        return {"error":f"No such file {file}!"}

    # Load audio data
    try:
        y, sr = librosa.load(file)
    except Exception as e:
        return {"error":f"{e}"}
    
    tempo = librosa.feature.tempo(y=y, sr=sr)
    
    try:
        seconds_per_beat = 60/tempo
    except Exception as e:
        return {"error":f"{e}"}
    
    return {
        "tempo_data":{
            "tempo_raw":tempo[0], #type:ignore
            "tempo_rounded": round(tempo[0]), #type:ignore
            "tempo_adjustments":{
                "Sixteenth": round(tempo[0] * 4),
                "Dotted Sixteenth": round(tempo[0] * (8/3)),
                "Eighth Triplet": round(tempo[0] * 3),
                "Eighth Note": round(tempo[0] * 2),
                "Dotted Eighth": round(tempo[0] * (4/3)),
                "Quarter Triplet": round(tempo[0] * (3/2)),
                "Dotted Quarter": round(tempo[0] * (2/3)),
                "Half Triplet": round(tempo[0] * (3/4)),
                "Half Note": round(tempo[0] / 2),
                "Dotted Half Note": round(tempo[0] / 3),
                "Whole Triplet": round(tempo[0] * (3/8)),
                "Whole Note": round(tempo[0] / 4)
            }
        },
        "offset_data":{
            "offset_raw": seconds_per_beat[0], #type:ignore
            "offset_rounded": round(seconds_per_beat[0], 3), #type:ignore
            "offset_ms": round(seconds_per_beat[0] * 1000), #type:ignore
            "offset_adjustments":{
                "Sixteenth": round(seconds_per_beat[0] / 4, 3) * 1000,
                "Dotted Sixteenth": round(seconds_per_beat[0] / (8/3), 3) * 1000,
                "Eighth Triplet": round(seconds_per_beat[0] / 3, 3) * 1000,
                "Eighth Note": round(seconds_per_beat[0] / 2, 3) * 1000,
                "Dotted Eighth": round(seconds_per_beat[0] / (4/3), 3) * 1000,
                "Quarter Triplet": round(seconds_per_beat[0] / (3/2), 3) * 1000,
                "Dotted Quarter": round(seconds_per_beat[0] / (2/3), 3) * 1000,
                "Half Triplet": round(seconds_per_beat[0] / (3/4), 3) * 1000,
                "Half Note": round(seconds_per_beat[0] * 2, 3) * 1000,
                "Dotted Half Note": round(seconds_per_beat[0] * 3, 3) * 1000,
                "Whole Triplet": round(seconds_per_beat[0] / (3/8), 3) * 1000,
                "Whole Note": round(seconds_per_beat[0] * 4, 3) * 1000
            }
        }
    }

def pre_process(output_path: Path, file_name: str) -> list:
    file_path = os.path.join(output_path, file_name)
    return_list = []
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                for key in data.keys():
                    return_list.append(key)
        except json.decoder.JSONDecodeError as e:
            return return_list
        return return_list
    else:
        return return_list

def process_data(path_list: list, 
                 pre_processed_list: list|set, 
                 file_type: Literal["mp3", "flac", "wav"], 
                 output_root:Path, 
                 output_json: str, 
                 update_resolution:int):
    
    processed_data = {}
    for i, audiofile in enumerate(path_list):
        if audiofile.name in pre_processed_list:
            pass
        else:
            processed_data[audiofile.name] = analyze_music(audiofile)
            if i % update_resolution == 0:
                clear()
                print(f"Progress ({file_type}'s): {(i / len(path_list)) * 100:.2f}%")
        
    with open(os.path.join(output_root, output_json), "r+") as file:
        if processed_data != {}:
            try:
                music_data = json.load(file)
                for key in processed_data.keys():
                    music_data[key] = processed_data[key]
            except json.decoder.JSONDecodeError as e:
                music_data = processed_data
            
            file.seek(0)
            file.truncate(0)
            json.dump(music_data, file, indent=4)
            
if __name__ == "__main__":
    folder = get_folder() # get the directory to process
    OUTPUT_PATH = Path(os.path.join(os.getcwd(), "data\\outputs"))
    MUSIC_LIST = "LatestScannedSongs.txt"
    MP3_ANALYSIS = "MP3Analysis.json"
    WAV_ANALYSIS = "WAVAnalysis.json"
    FLAC_ANALYSIS = "FLACAnalysis.json"
    
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
        
    if not os.path.exists(f"{OUTPUT_PATH}\\{MP3_ANALYSIS}"):
        with open(f"{OUTPUT_PATH}\\{MP3_ANALYSIS}", 'w') as file:
            file.write("")
            
    if not os.path.exists(f"{OUTPUT_PATH}\\{FLAC_ANALYSIS}"):
        with open(f"{OUTPUT_PATH}\\{FLAC_ANALYSIS}", 'w') as file:
            file.write("")
            
    if not os.path.exists(f"{OUTPUT_PATH}\\{WAV_ANALYSIS}"):
        with open(f"{OUTPUT_PATH}\\{WAV_ANALYSIS}", 'w') as file:
            file.write("")
    
    already_processed = []
    already_processed.extend(pre_process(OUTPUT_PATH, MP3_ANALYSIS))
    already_processed.extend(pre_process(OUTPUT_PATH, WAV_ANALYSIS))
    already_processed.extend(pre_process(OUTPUT_PATH, FLAC_ANALYSIS))
    already_processed = set(already_processed)
            
    # Collect MP3's, FLAC's, and WAV's
    mp3_paths = []
    flac_paths = []
    wav_paths = []
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            file = Path(file)
            if file.suffix == ".mp3":
                mp3_paths.append(Path(os.path.join(root, file)))
            elif file.suffix == ".wav":
                wav_paths.append(Path(os.path.join(root, file)))
            elif file.suffix == ".flac":
                flac_paths.append(Path(os.path.join(root, file)))
                
    # Log file names
    with open(os.path.join(OUTPUT_PATH, MUSIC_LIST), 'w', encoding='utf-8') as file:
        file.write(f"{"#"*10} MP3 {"#"*10}\n")
        for audiofile in mp3_paths:
            file.write(f"{audiofile.name}\n")
            
        file.write(f"\n{"#"*10} WAV {"#"*10}\n")
        for audiofile in wav_paths:
            file.write(f"{audiofile.name}\n")
            
        file.write(f"\n{"#"*10} FLAC {"#"*10}\n")
        for audiofile in flac_paths:
            file.write(f"{audiofile.name}\n")
            
    # Process files
    GLOBAL_UPDATE_RESOLUTION = 5 # Lower equals more updates for progress bar adds overhead
    print("Processing has begun...")
    
    # PROCESS MP3
    process_data(mp3_paths, already_processed, "mp3", OUTPUT_PATH, MP3_ANALYSIS, GLOBAL_UPDATE_RESOLUTION)
    
    # PROCESS FLAC
    process_data(flac_paths, already_processed, "flac", OUTPUT_PATH, FLAC_ANALYSIS, GLOBAL_UPDATE_RESOLUTION)
    
    # PROCESS WAV
    process_data(wav_paths, already_processed, "wav", OUTPUT_PATH, WAV_ANALYSIS, GLOBAL_UPDATE_RESOLUTION)
    
    clear()
    print("Finished processing!")