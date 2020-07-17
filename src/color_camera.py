from .camera import Camera
import cv2
import math
import numpy as np


# Displays a circle in the middle of the screen, and prints the correct color in the circle
class ColorCamera(Camera):
    def __init__(self, circle_radius=10):
        super().__init__()
        # Circle attributes
        self.circle_radius = circle_radius

    def _edit_frame(self, frame, frame_counter):
        height, width, _channels = frame.shape
        center = (int(width/2), int(height/2))

        # Calculate the average color (use better algorithm)
        total_points = 0
        # color_sum = [0, 0, 0]
        # x_counter = -1 * self.circle_radius
        # for x in range(center[0]-self.circle_radius, center[0]+self.circle_radius+1):
        #     y_limit = int(math.sqrt(self.circle_radius**2 - x_counter**2))
        #     for y in range(center[1] - y_limit, center[1] + y_limit):
        #         # frame[y,x] = [0,255,0]
        #         color_sum +=
        #     x_counter += 1
        mask = np.zeros((height, width))
        cv2.circle(mask, center, self.circle_radius, 1, -1)
        # In (B, G, R)
        average_color = np.mean(frame[mask == 1], axis=0)
        print(average_color)

        # Draw circle in center
        cv2.circle(frame, center, self.circle_radius, (0, 0, 255), 1)
        return frame
