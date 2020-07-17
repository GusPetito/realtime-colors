from .camera import Camera
import cv2
import numpy as np
import pandas as pd
import threading
from queue import Queue


# Displays a circle in the middle of the screen, and prints the correct color in the circle
class ColorCamera(Camera):
    def __init__(self, circle_radius=10):
        super().__init__()
        # Circle attributes
        self.circle_radius = circle_radius
        self.closest_color_bgr = (0, 0, 0)

    # Returns the squared error when both colors are 3-length numpy arrays, to be used to find the closest color
    def _squared_error(self, average_color, target_color):
        return ((average_color - target_color)**2).mean()

    def _squared_error_row(self, average_color, row):
        # Switch from (R, G, B) to (B, G, R)
        row = row.to_numpy()
        row[3], row[5] = row[5], row[3]
        return pd.Series(np.concatenate((row, [self._squared_error(average_color, row[3:])])))

    def _calculate_before_hand(self, frame):
        height, width, _channels = frame.shape
        center = (int(width / 2), int(height / 2))

        # Makes a circle of ones in a bunch of zeros. Will tell the camera where to find the average color
        mask = np.zeros((height, width))
        cv2.circle(mask, center, self.circle_radius, 1, -1)

        colors = pd.read_csv('res/colors.csv')

        # Set up a thread so the closest color can be calculated without stuttering the video
        # Add a frame to the queue to start the calculation
        # TODO: Maybe generate all colors beforehand
        color_queue = Queue()
        def get_and_calculate_colors():
            exit_flag = threading.Event()
            while exit_flag:
                curr_frame = color_queue.get()
                # In (B, G, R)
                average_color = np.mean(curr_frame[mask == 1], axis=0)
                errors = colors.apply(lambda row: self._squared_error_row(average_color, row), axis=1)
                errors.columns = ['comp_name', 'human_name', 'hex', 'b', 'g', 'r', 'error']
                closest_color = errors.iloc[errors['error'].idxmin()]
                self.closest_color_bgr = tuple(closest_color[['b', 'g', 'r']])
                print(closest_color['human_name'], self.closest_color_bgr)

                color_queue.task_done()

        color_thread = threading.Thread(target=get_and_calculate_colors, daemon=True)
        color_thread.start()

        return {'center': center, 'color_queue': color_queue}

    def _edit_frame(self, frame, frame_counter, **kwargs):
        if frame_counter % 100 == 0:
            kwargs['color_queue'].put(frame)\

        # Draw circle in center
        cv2.circle(frame, kwargs['center'], self.circle_radius, (0, 0, 255), 1)
        # Draw colored square in corner
        cv2.rectangle(frame, (0, 0), (100, 100),
                      (int(self.closest_color_bgr[0]), int(self.closest_color_bgr[1]),
                       int(self.closest_color_bgr[2])), -1)
        return frame, {}
