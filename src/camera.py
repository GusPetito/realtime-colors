import cv2


class Camera:
    # Override this function to calculate values before the loop wit ha starting frame. Returns an object
    def _calculate_before_hand(self, frame):
        return {}

    # Use this function to edit the frame in the camera loop. Must return an np array of the same shape as frame
    # and a dict with continued states if you override.
    # Additional kwargs passed in by _calculate_before_hand and by the continued state.
    def _edit_frame(self, frame, frame_counter, **kwargs):
        return frame, {}

    # Runs the camera loop.
    # frame_delay is the minimum amount of milliseconds between each frame.
    # closing_keys are the keys to close the program as characters. Empty list for no keys, None for all keys
    def run_camera(self, frame_delay=1, closing_keys=['q']):
        cap = cv2.VideoCapture(0)

        ret, frame = cap.read()
        cv2.imshow('frame', frame)
        cv2.moveWindow('frame', 40, 30)

        additional_edit_args = self._calculate_before_hand(frame)
        continued_state = {}

        # The loop to run the program
        frame_counter = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Edit the frame
            frame, continued_state = self._edit_frame(frame, frame_counter, **additional_edit_args, **continued_state)

            # Show the frame'
            cv2.imshow('frame', frame)

            # Stop if the user clicks a closing character or closes the window
            key = cv2.waitKey(frame_delay)
            if closing_keys is None and key != -1:
                break
            if closing_keys is not None and key in map(lambda stop_key: ord(stop_key), closing_keys):
                break
            if cv2.getWindowProperty('frame', cv2.WND_PROP_VISIBLE) < 1:
                break

            frame_counter += 1

        # Release the capture and destroy the window after the user quits
        cap.release()
        cv2.destroyAllWindows()