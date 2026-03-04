import numpy
import queue
import time
import cv2

import config

TIMEOUT = 15
MAX_TIMEOUT = 2000

def frame_generator(path):
    cap = cv2.VideoCapture(filename=path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        yield frame
    cap.release()

def produce_frames(frame_buffer, video_path):
    #performance_times = {}

    CHAR_SIZE_X = 1
    CHAR_SIZE_Y = 2

    frame_gen = frame_generator(video_path)
    image_frame_buffer = queue.Queue(maxsize=frame_buffer.maxsize)

    image_sleep_time = time.time()

    conf = config.get_config()
    quantization_level = conf["quantization_level"]
    black_point = conf["black_point"]

    char_x = CHAR_SIZE_X * quantization_level
    char_y = CHAR_SIZE_Y * quantization_level
    
    while True:
        if image_frame_buffer.full():
            if time.time() - image_sleep_time > MAX_TIMEOUT / 1000:
                raise Exception("YOU'RE TAKING TOO LONG")

            time.sleep(TIMEOUT / 1000)
        
        image_sleep_time = time.time()

        #start_time = time.time()

        try:
            file_frame = next(frame_gen)
        except StopIteration:
            return

        #end_time = time.time()
        #performance_times["get_image"] = end_time - start_time

        #start_time = time.time()

        pixels_grid = cv2.cvtColor(file_frame, cv2.COLOR_BGR2RGB)

        height = pixels_grid.shape[0]
        width = pixels_grid.shape[1]

        h2 = (height // char_y) * char_y
        w2 = (width // char_x) * char_x

        cropped = pixels_grid[:h2, :w2]

        blocks_y = h2 // char_y
        blocks_x = w2 // char_x

        reshaped = cropped.reshape(
            blocks_y, char_y,
            blocks_x, char_x,
            3
        )

        avg_color = numpy.mean(reshaped, axis=(1, 3)).astype("uint8")

        #end_time = time.time()

        #performance_times["prepare_image"] = end_time - start_time

        #start_time = time.time()

        # Loop over all blocks
        lines = []

        for y in range(blocks_y):
            chars = []

            for x in range(blocks_x):
                color = avg_color[y, x]

                if color[0] > black_point or color[1] > black_point or color[2] > black_point:
                    chars.append(f"\033[38;2;{color[0]};{color[1]};{color[2]}m█")
                else:
                    chars.append(' ')

            lines.append("".join(chars) + "\n")
        
        frame_buffer.put("".join(lines))
        #end_time = time.time()

        #performance_times["convert_image_to_text"] = end_time - start_time

        #print("Buffer Performance: ", performance_times)