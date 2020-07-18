from .camera import Camera
import cv2
import numpy as np
import pandas as pd
import threading


# Displays a circle in the middle of the screen, and prints the correct color in the circle
class ColorCamera(Camera):
    def __init__(self, circle_radius=10):
        super().__init__()
        # Circle attributes
        self.circle_radius = circle_radius
        self.closest_color_bgr = (0, 0, 0)

        # Calculated beforehand
        self.curr_frame = None
        self.center = None
        self.average_color = (0,0,0)

        # For help debugging, will create the average color box next to the real color box
        self.debug_mode = False

    def _calculate_before_hand(self, frame):
        height, width, _channels = frame.shape
        self.center = (int(width / 2), int(height / 2))
        self.curr_frame = frame

        # Makes a circle of ones in a bunch of zeros. Will tell the camera where to find the average color
        mask = np.zeros((height, width))
        cv2.circle(mask, self.center, self.circle_radius, 1, -1)

        color_file = pd.read_csv('res/colors.csv', header=None)
        color_file.columns = color_file.columns = ['comp_name', 'human_name', 'hex', 'r', 'g', 'b']

        # Set up a thread so the closest color can be calculated without stuttering the video
        def get_and_calculate_colors():
            exit_flag = threading.Event()
            while exit_flag:
                exit_flag.wait(.25)
                # In (B, G, R)
                average_color = np.mean(self.curr_frame[mask == 1], axis=0)
                self.average_color = average_color
                colors = np.array(color_file[['b', 'g', 'r']])
                errors = np.sum((colors - average_color) ** 2, axis=1)
                closest_color = color_file.loc[errors.argmin(), :]
                self.closest_color_bgr = tuple(closest_color[['b', 'g', 'r']])
                # Print the color name and the RGB value
                print(f"{closest_color['human_name']} ({self.closest_color_bgr[2]}, {self.closest_color_bgr[1]}"
                      f", {self.closest_color_bgr[0]})")

        color_thread = threading.Thread(target=get_and_calculate_colors, daemon=True)
        color_thread.start()

    def _edit_frame(self, frame, frame_counter, **kwargs):
        self.curr_frame = frame.copy()

        # Draw circle in center
        cv2.circle(frame, self.center, self.circle_radius, (0, 0, 255), 1)
        # Draw colored square in corner
        cv2.rectangle(frame, (0, 0), (100, 100),
                      (int(self.closest_color_bgr[0]), int(self.closest_color_bgr[1]),
                       int(self.closest_color_bgr[2])), -1)
        if self.debug_mode:
            cv2.rectangle(frame, (100, 0), (200, 100), self.average_color, -1)
        return frame
