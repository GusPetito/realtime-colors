from .camera import Camera
import cv2
import numpy as np
import pandas as pd


# Displays a circle in the middle of the screen, and prints the correct color in the circle
class ColorCamera(Camera):
    def __init__(self, circle_radius=10):
        super().__init__()
        # Circle attributes
        self.circle_radius = circle_radius

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

        mask = np.zeros((height, width))
        cv2.circle(mask, center, self.circle_radius, 1, -1)

        colors = pd.read_csv('res/colors.csv')

        return {'center': center, 'mask': mask, 'colors': colors}

    def _edit_frame(self, frame, frame_counter, **kwargs):
        # In (B, G, R)
        average_color = np.mean(frame[kwargs['mask'] == 1], axis=0)

        # Find the closest color
        if frame_counter % 100 == 0:
            errors = kwargs['colors'].apply(lambda row: self._squared_error_row(average_color, row), axis=1)
            errors.columns = ['comp_name', 'human_name', 'hex', 'b', 'g', 'r', 'error']
            closest_color = errors.iloc[errors['error'].idxmin()]
            closest_color_bgr = tuple(closest_color[['b', 'g', 'r']])
            print(closest_color['human_name'], closest_color_bgr)
        else:
            closest_color_bgr = kwargs['closest_color_bgr']

        # Draw circle in center
        cv2.circle(frame, kwargs['center'], self.circle_radius, (0, 0, 255), 1)
        # Draw colored square in corner
        cv2.rectangle(frame, (0, 0), (100, 100),
                      (int(closest_color_bgr[0]), int(closest_color_bgr[1]), int(closest_color_bgr[2])), -1)
        return frame, {'closest_color_bgr': closest_color_bgr}
