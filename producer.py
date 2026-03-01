from PIL import Image
import numpy
import io
import termcolor
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

def produce_frames(frame_buffer):
    frame_gen = frame_generator("video/school commercial.mp4")
    image_frame_buffer = queue.Queue(maxsize=frame_buffer.maxsize)

    image_sleep_time = time.time()

    conf = config.get_config()
    quantization_level = conf["quantization_level"]
    
    while True:
        if image_frame_buffer.full():
            if time.time() - image_sleep_time > MAX_TIMEOUT / 1000:
                raise Exception("YOU'RE TAKING TOO LONG")

            time.sleep(TIMEOUT / 1000)
        
        image_sleep_time = time.time()

        start_time = time.time()

        try:
            file_frame = next(frame_gen)
        except StopIteration:
            return

        encode_success, image = cv2.imencode(".png", file_frame)

        if not encode_success:
            raise Exception("Failed to encode frame")

        frame = image.tobytes()
        frame_bytes = io.BytesIO(frame)

        picture = Image.open(frame_bytes)
        picture = picture.convert("RGB")

        width, height = picture.size

        CHAR_SIZE_X = 1
        CHAR_SIZE_Y = 2

        char_x = CHAR_SIZE_X * quantization_level
        char_y = CHAR_SIZE_Y * quantization_level

        pixels_grid = numpy.array(picture)

        image_text_data = ""

        # Loop over all pixels
        for y in range(0, height, char_y):
            line = ""

            for x in range(0, width, char_x):
                pixel_chunk = pixels_grid[y : y + char_y, x : x + char_x]

                if pixel_chunk.size == 0:
                    continue

                avg_color = numpy.mean(pixel_chunk, axis=(0, 1))

                if numpy.isnan(avg_color).any():
                    continue

                red, green, blue = numpy.round(avg_color).astype(numpy.ubyte)
                color = (red, green, blue)

                line += termcolor.colored('█', color)
                
            image_text_data += line + "\n"
        frame_buffer.put(image_text_data)
        end_time = time.time()

        print("time to buffer frame: ", end_time - start_time)