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

    def _calculate_before_hand(self, frame):
        height, width, _channels = frame.shape
        center = (int(width / 2), int(height / 2))

        mask = np.zeros((height, width))
        cv2.circle(mask, center, self.circle_radius, 1, -1)

        return {'center': center, 'mask': mask}

    def _edit_frame(self, frame, frame_counter, **kwargs):
        # In (B, G, R)
        average_color = np.mean(frame[kwargs['mask'] == 1], axis=0).astype(np.uint8)
        print(average_color)

        # Draw circle in center
        cv2.circle(frame, kwargs['center'], self.circle_radius, (0, 0, 255), 1)
        return frame
