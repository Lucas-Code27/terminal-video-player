from pathlib import Path
from tqdm import tqdm
import termcolor
import os
import sys
import time

frames_folder = "output/"

FPS = 30
FRAME_DELAY = 1 / FPS

filenames = [str(f) for f in Path(frames_folder).glob("*.txt")]
sorted_filenames = sorted(filenames)

next_frame_time = time.perf_counter()

frames = []

for image_path in tqdm(sorted_filenames, desc="Preloading Frames"):
    with open(image_path, "r") as f:
        frames.append(f.read())

print("\033[?25l")
os.system("clear")

for frame in frames:
    sys.stdout.write("\033[0;0H")
    sys.stdout.write(frame)
    sys.stdout.flush()

    next_frame_time += FRAME_DELAY
    sleep_time = next_frame_time - time.perf_counter()
    if sleep_time > 0:
        time.sleep(FRAME_DELAY)

print("\033[?25h")
os.system("clear")